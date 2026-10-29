"""V6.8 clean-room insect anatomy/rig proof, NOT a film approval.
Independent of V4/V5/V6 scene mutations; keep all prior artifacts untouched.
Renders one 48-frame 24-fps portrait motion proof and a still. This is an
anatomy-first gate before spending runner hours on 14 chapters.
"""
import math, os, random
import bpy
from mathutils import Vector

bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
scene=bpy.context.scene
scene.render.engine="BLENDER_EEVEE_NEXT"
scene.render.resolution_x=270
scene.render.resolution_y=480
scene.render.resolution_percentage=100
scene.render.film_transparent=False
scene.render.image_settings.color_mode="RGBA"
scene.render.fps=24
scene.frame_start=1
scene.frame_end=48
scene.render.image_settings.file_format="PNG"
scene.view_settings.view_transform="AgX"
scene.world.color=(.13,.14,.11)
scene.render.film_transparent=False

def material(name, rgb, rough=.65, metal=0, alpha=1, noise=0):
    m=bpy.data.materials.new(name);m.diffuse_color=(*rgb,alpha);m.use_nodes=True
    bs=m.node_tree.nodes.get("Principled BSDF")
    bs.inputs["Base Color"].default_value=(*rgb,1)
    bs.inputs["Roughness"].default_value=rough
    bs.inputs["Metallic"].default_value=metal
    bs.inputs["Alpha"].default_value=alpha
    if alpha<1:
        m.surface_render_method="DITHERED"
    if noise:
        n=m.node_tree.nodes.new("ShaderNodeTexNoise")
        n.inputs["Scale"].default_value=noise
        bump=m.node_tree.nodes.new("ShaderNodeBump")
        bump.inputs["Strength"].default_value=.13
        bump.inputs["Distance"].default_value=.012
        m.node_tree.links.new(n.outputs["Fac"],bump.inputs["Height"])
        m.node_tree.links.new(bump.outputs["Normal"],bs.inputs["Normal"])
    return m

emerald=material("iridescent emerald cuticle",(.018,.27,.18),.29,.56,noise=37)
blue=material("blue-green sclerites",(.018,.10,.16),.34,.45,noise=42)
dark=material("joint membranes",(.016,.022,.018),.76)
eye=material("compound eye dark",(.008,.012,.011),.24,.10)
brown=material("roach dark chitin",(.17,.052,.020),.45,.16,noise=33)
bronze=material("roach elytra",(.25,.092,.029),.40,.23,noise=41)
tan=material("ventral segment",(.10,.036,.017),.70)
wing=material("transparent wasp wing membrane",(.31,.42,.39),.42,0,.37)
vein=material("membrane veins",(.11,.16,.14),.59)
soil=material("soil granular",(.095,.071,.049),.98,noise=23)
leafmat=material("leaf litter",(.19,.13,.052),.94,noise=14)
green=material("understory leaves",(.047,.14,.054),.79,noise=17)

def root(name, location, angle=0):
    o=bpy.data.objects.new(name,None);scene.collection.objects.link(o)
    o.location=location;o.rotation_euler.z=angle;return o

def ell(name,loc,scale,mat,parent=None,segments=24,rings=12):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=segments,ring_count=rings)
    o=bpy.context.object;o.name=name;o.parent=parent;o.location=loc;o.scale=scale
    o.data.materials.append(mat)
    for f in o.data.polygons:f.use_smooth=True
    return o

def taper(name,a,b,r1,r2,mat,parent=None):
    v1,v2=Vector(a),Vector(b);d=v2-v1
    bpy.ops.mesh.primitive_cone_add(vertices=10,radius1=r1,radius2=r2,depth=d.length)
    o=bpy.context.object;o.name=name;o.parent=parent
    o.location=(v1+v2)*.5
    o.rotation_euler=d.to_track_quat("Z","Y").to_euler()
    o.data.materials.append(mat)
    for p in o.data.polygons:p.use_smooth=True
    return o

def curve(name,points,r,mat,parent):
    data=bpy.data.curves.new(name,"CURVE");data.dimensions="3D"
    data.bevel_depth=r;data.bevel_resolution=2
    spl=data.splines.new("BEZIER");spl.bezier_points.add(len(points)-1)
    for b,pt in zip(spl.bezier_points,points):
        b.co=pt;b.handle_left_type="AUTO";b.handle_right_type="AUTO"
    o=bpy.data.objects.new(name,data);scene.collection.objects.link(o)
    o.parent=parent;data.materials.append(mat);return o

def shield(name, x0,x1, ycenter, halfwidth, zbase, lift, mat, parent):
    # Longitudinal shell with curved transverse profile, not a scaled oval.
    verts=[];faces=[];nx=15;ny=10
    for i in range(nx+1):
        t=i/nx
        width=halfwidth*(.48+.52*math.sin(math.pi*(.15+.72*t)))
        for j in range(ny+1):
            s=2*j/ny-1
            verts.append((x0+(x1-x0)*t,ycenter+s*width,
                          zbase+lift*(1-s*s)*math.sin(math.pi*(.10+.82*t))))
    for i in range(nx):
        for j in range(ny):
            a=i*(ny+1)+j;faces.append((a,a+ny+1,a+ny+2,a+1))
    mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.update()
    obj=bpy.data.objects.new(name,mesh);scene.collection.objects.link(obj)
    obj.parent=parent;mesh.materials.append(mat)
    for f in mesh.polygons:f.use_smooth=True
    sol=obj.modifiers.new("thin organic shell","SOLIDIFY");sol.thickness=.012
    return obj

wasp=root("ANATOMY_WASP_ROOT",(-.68,-.18,.63),-.10)
ell("wasp head",(.39,0,.05),(.17,.16,.13),emerald,wasp)
ell("wasp thorax",(.11,0,.06),(.24,.19,.17),blue,wasp)
ell("wasp petiole",(-.17,0,.03),(.18,.075,.075),dark,wasp)
# tapered segmented abdomen: each tergite follows a curved gaster
for i in range(6):
    t=i/5
    ell("wasp gaster tergite %02d"%i,
        (-.31-.105*i,0,.03+.045*math.sin(t*math.pi)),
        (.108,.125+.043*math.sin(t*math.pi),.102+.036*math.sin(t*math.pi)),
        emerald if i%2==0 else blue,wasp)
    if i<5:
        ell("wasp intersegment %02d"%i,(-.36-.105*i,0,.03),
            (.023,.124,.09),dark,wasp)
for s in (-1,1):
    ell("wasp eye %d"%s,(.46,s*.123,.083),(.065,.025,.065),eye,wasp)
    curve("wasp geniculate antenna %d"%s,
        [(.50,s*.07,.12),(.63,s*.12,.19),(.71,s*.17,.19),(.80,s*.18,.13)],
        .007,dark,wasp)
    for leg in range(3):
        x=.29-leg*.19;y=s*.15
        hip=(x,y,.01);knee=(x+.10-leg*.075,s*(.34+.035*leg),-.16)
        ankle=(x+.13-leg*.10,s*(.39+.065*leg),-.48)
        taper("wasp coxa %d %d"%(s,leg),hip,knee,.036,.022,emerald,wasp)
        ell("wasp joint %d %d"%(s,leg),knee,(.033,.033,.033),dark,wasp)
        taper("wasp tibia %d %d"%(s,leg),knee,ankle,.019,.008,dark,wasp)
        taper("wasp tarsus %d %d"%(s,leg),ankle,
              (ankle[0]+.09,ankle[1]+s*.025,ankle[2]-.02),.009,.002,dark,wasp)
    for hind in (0,1):
        pivot=root("wing hinge %d %d"%(s,hind),(0,0,0))
        pivot.parent=wasp;pivot.location=(.08-hind*.12,s*.14,.16)
        span=.78 if hind==0 else .57
        verts=[];faces=[]
        for i in range(17):
            t=i/16;breadth=(.13 if hind==0 else .09)*math.sin(math.pi*t)**.8
            for side in (-1,1):
                verts.append((-.18*t+side*breadth,s*span*t,.03*math.sin(math.pi*t)))
        for i in range(16):
            a=2*i;faces.append((a,a+2,a+3,a+1))
        mesh=bpy.data.meshes.new("wasp wing membrane");mesh.from_pydata(verts,[],faces)
        mesh.update();o=bpy.data.objects.new("veined membrane",mesh)
        scene.collection.objects.link(o);o.parent=pivot;mesh.materials.append(wing)
        curve("wing longitudinal vein",[(0,0,0),(-.08,s*span*.50,.02),
             (-.16,s*span*.92,0)],.003,vein,pivot)
        for f in range(1,49,3):
            pivot.rotation_euler.x=s*(.13+.10*math.sin(f*.72+hind))
            pivot.keyframe_insert(data_path="rotation_euler",frame=f)

roach=root("ANATOMY_ROACH_ROOT",(.72,.20,.26),math.pi)
ell("roach ventral abdomen",(-.12,0,0),(.55,.31,.17),tan,roach)
ell("roach pronotum",(.41,0,.08),(.24,.33,.12),bronze,roach)
ell("roach head",(.64,0,-.015),(.17,.19,.13),brown,roach)
for i in range(7):
    x=.20-i*.12
    ell("roach abdominal sternite %02d"%i,(x,0,-.065),
        (.08,.29-.02*i,.12),brown if i%2==0 else tan,roach)
for s in (-1,1):
    shield("curved articulated elytron %d"%s,.23,-.69,s*.14,.18,.14,.085,
           bronze,roach)
    ell("roach compound eye %d"%s,(.71,s*.15,.025),(.064,.029,.060),eye,roach)
    curve("roach filiform antenna %d"%s,
        [(.76,s*.10,.025),(.96,s*.17,.06),(1.22,s*.25,.02),
         (1.45,s*.34,-.10)],.005,dark,roach)
    for leg in range(3):
        x=.35-leg*.34
        hip=(x,s*.20,-.04)
        femur=(x+.15-leg*.12,s*.43,-.14)
        foot=(x+.23-leg*.18,s*.53,-.27)
        taper("roach femur %d %d"%(s,leg),hip,femur,.054,.026,brown,roach)
        ell("roach knee %d %d"%(s,leg),femur,(.035,.035,.035),dark,roach)
        taper("roach tibia %d %d"%(s,leg),femur,foot,.024,.009,brown,roach)
        for spike in range(4):
            t=(spike+1)/5
            p=Vector(femur).lerp(Vector(foot),t)
            taper("roach tibial spine",p,
                  p+Vector((-.04,s*.035,.015)),.007,.001,dark,roach)
        taper("roach tarsus",foot,
              (foot[0]+.13,foot[1]+s*.03,foot[2]-.01),.010,.002,dark,roach)

# Grounded set with depth layers, not identical pencil trunks.
ell("earth base",(0,0,-.24),(9,9,.17),soil)
rng=random.Random(6801)
for i in range(125):
    x=rng.uniform(-4.2,4.2);y=rng.uniform(-3.6,3.8)
    if abs(x)<1.5 and abs(y)<.8:continue
    o=ell("forest litter", (x,y,-.064),
          (rng.uniform(.035,.17),rng.uniform(.02,.07),.009),
          leafmat if i%3 else green,segments=12,rings=6)
    o.rotation_euler.z=rng.uniform(0,6.28)
for i in range(22):
    x=rng.uniform(-4.0,4.0);y=rng.choice([-1,1])*rng.uniform(1.7,4.2)
    if i%3==0:
        taper("irregular sapling",(x,y,-.12),(x+.13,y,.9+rng.random()),.065,.025,soil)
    for j in range(3):
        ell("understory fern",(x+rng.uniform(-.24,.24),
            y+rng.uniform(-.2,.2),.12+j*.08),
            (.30,.09,.035),green,segments=12,rings=6)

for name,loc,power,size in [
    ("large softbox",(-2.6,-3.2,4.0),600,4.0),
    ("forest rim",(2.0,1.7,3.2),450,3.0)]:
    data=bpy.data.lights.new(name,"AREA");data.energy=power;data.shape="DISK";data.size=size
    obj=bpy.data.objects.new(name,data);scene.collection.objects.link(obj)
    obj.location=loc;direction=Vector((0,0,.2))-obj.location
    obj.rotation_euler=direction.to_track_quat("-Z","Y").to_euler()

camera_data=bpy.data.cameras.new("portrait specimen camera")
camera=bpy.data.objects.new("portrait specimen camera",camera_data)
scene.collection.objects.link(camera);scene.camera=camera
camera.location=(2.3,-4.5,2.15)
direction=Vector((0,0,.32))-camera.location
camera.rotation_euler=direction.to_track_quat("-Z","Y").to_euler()
camera_data.type="ORTHO";camera_data.ortho_scale=3.2
for f in (1,24,48):
    wasp.location=(-.68+.06*(f-1)/47,-.18,.63+.022*math.sin(f*.14))
    wasp.keyframe_insert(data_path="location",frame=f)
    roach.location=(.72-.12*(f-1)/47,.20,.26)
    roach.keyframe_insert(data_path="location",frame=f)
    camera.location=(2.3-.10*(f-1)/47,-4.5,2.15)
    camera.keyframe_insert(data_path="location",frame=f)

output=os.environ.get("BLENDER_OUTPUT","/tmp/jewel_wasp_v68_anatomy.png")
motion=os.environ.get("V68_MOTION","0")=="1"
if motion:
    scene.render.image_settings.file_format="FFMPEG"
    scene.render.ffmpeg.format="MPEG4"
    scene.render.ffmpeg.codec="H264"
    scene.render.ffmpeg.constant_rate_factor="MEDIUM"
    scene.render.filepath=output
    bpy.ops.render.render(animation=True)
else:
    scene.frame_set(24)
    scene.render.filepath=output
    bpy.ops.render.render(write_still=True)
print("JEWEL_V68_ANATOMY_RENDER_DONE", "motion" if motion else "still")
