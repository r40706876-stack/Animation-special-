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
        ramp=m.node_tree.nodes.new("ShaderNodeValToRGB")
        ramp.color_ramp.elements[0].position=.20
        ramp.color_ramp.elements[1].position=.80
        ramp.color_ramp.elements[0].color=(*(max(0,min(1,c*.74)) for c in rgb),1)
        ramp.color_ramp.elements[1].color=(*(max(0,min(1,c*1.17)) for c in rgb),1)
        m.node_tree.links.new(n.outputs["Fac"],ramp.inputs["Fac"])
        m.node_tree.links.new(ramp.outputs["Color"],bs.inputs["Base Color"])
    return m

emerald=material("iridescent emerald cuticle",(.012,.15,.115),.43,.34,noise=37)
blue=material("blue-green sclerites",(.018,.075,.095),.48,.28,noise=42)
dark=material("joint membranes",(.016,.022,.018),.76)
leg_amber=material("jewel wasp warm amber leg cuticle",(.22,.074,.028),.62,.08,noise=25)
eye=material("compound eye dark",(.008,.012,.011),.24,.10)
brown=material("roach dark chitin",(.043,.018,.010),.82,.04,noise=21)
bronze=material("roach elytra",(.078,.033,.017),.78,.06,noise=26)
tan=material("ventral segment",(.056,.024,.014),.83)
wing=material("transparent wasp wing membrane",(.12,.22,.19),.62,0,.23)
vein=material("membrane veins",(.11,.16,.14),.59)
soil=material("soil granular",(.095,.071,.049),.98,noise=23)
leafmat=material("leaf litter",(.19,.13,.052),.94,noise=14)
green=material("understory leaves",(.037,.10,.042),.83,noise=17)
bark=material("rough distant bark",(.045,.036,.026),.94,noise=29)
forest_depth=material("deep forest shadow backdrop",(.017,.038,.024),.99,noise=4)

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
        width=halfwidth*(.15+.85*math.sin(math.pi*t)**.72)
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

wasp=root("ANATOMY_WASP_ROOT",(-.68,-.18,.43),-.10)
# Scale both complete insect rigs to fit the narrow 9:16 composition.
wasp.scale=(.78,.78,.78)
ell("wasp head",(.39,0,.05),(.17,.16,.13),emerald,wasp)
ell("wasp thorax",(.11,0,.06),(.24,.19,.17),blue,wasp)
ell("wasp petiole",(-.17,0,.03),(.18,.075,.075),dark,wasp)
# One continuous spindle-shaped gaster, not six visibly separate toy beads.
# Narrow inter-tergite seams are material bands on the SAME mesh.
verts=[];faces=[];rings=43;around=20
for i in range(rings):
    t=i/(rings-1)
    x=-.275-.66*t
    profile=max(.025,math.sin(math.pi*t)**.60)
    ry=(.078+.073*profile)*(1-.18*t)
    rz=(.069+.064*profile)*(1-.12*t)
    zc=.035+.043*math.sin(math.pi*t)
    for j in range(around):
        theta=2*math.pi*j/around
        verts.append((x,ry*math.cos(theta),zc+rz*math.sin(theta)))
for i in range(rings-1):
    for j in range(around):
        k=i*around+j;kn=i*around+(j+1)%around
        faces.append((k,kn,kn+around,k+around))
mesh=bpy.data.meshes.new("continuous sculpted gaster mesh")
mesh.from_pydata(verts,[],faces);mesh.update()
gaster=bpy.data.objects.new("wasp continuous anatomical gaster",mesh)
scene.collection.objects.link(gaster);gaster.parent=wasp
mesh.materials.append(emerald);mesh.materials.append(blue);mesh.materials.append(dark)
for face in mesh.polygons:
    face.use_smooth=True
    axial=face.index//around
    face.material_index=2 if axial in (8,15,22,29,36) else (0 if axial<23 else 1)
for s in (-1,1):
    ell("wasp eye %d"%s,(.46,s*.123,.083),(.065,.025,.065),eye,wasp)
    curve("wasp geniculate antenna %d"%s,
        [(.50,s*.07,.12),(.63,s*.12,.19),(.71,s*.17,.19),(.80,s*.18,.13)],
        .007,dark,wasp)
    # Small paired mandibles and palps distinguish the wasp face from a sphere.
    curve("wasp mandibular palp %d"%s,
          [(.52,s*.065,-.015),(.59,s*.09,-.06),(.64,s*.075,-.085)],
          .008,dark,wasp)
    for leg in range(3):
        x=.29-leg*.19;y=s*.15
        hip=Vector((x,y,.01));knee=Vector((x+.10-leg*.075,s*(.34+.035*leg),-.16))
        ankle=Vector((x+.13-leg*.10,s*(.39+.065*leg),-.48))
        gait=root("wasp gait pivot %d %d"%(s,leg),(0,0,0))
        gait.parent=wasp;gait.location=hip
        taper("wasp coxa %d %d"%(s,leg),(0,0,0),knee-hip,.036,.022,leg_amber,gait)
        ell("wasp joint %d %d"%(s,leg),knee-hip,(.033,.033,.033),dark,gait)
        taper("wasp tibia %d %d"%(s,leg),knee-hip,ankle-hip,.019,.008,leg_amber,gait)
        taper("wasp tarsus %d %d"%(s,leg),ankle-hip,
              ankle-hip+Vector((.09,s*.025,-.02)),.009,.002,dark,gait)
    for hind in (0,1):
        pivot=root("wing hinge %d %d"%(s,hind),(0,0,0))
        pivot.parent=wasp;pivot.location=(.08-hind*.12,s*.14,.16)
        span=.65 if hind==0 else .46
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
        for f in range(1,49):
            pivot.rotation_euler.x=s*(.25+.74*math.sin(f*1.73+hind*.9))
            pivot.keyframe_insert(data_path="rotation_euler",frame=f)

roach=root("ANATOMY_ROACH_ROOT",(.72,.20,.20),math.pi)
roach.scale=(.78,.78,.78)
ell("roach ventral abdomen",(-.12,0,0),(.55,.32,.13),tan,roach)
ell("roach pronotum",(.41,0,.08),(.22,.275,.095),bronze,roach)
ell("roach head",(.64,0,-.015),(.16,.155,.115),brown,roach)
ell("roach pronotal dark marking",(.44,0,.169),(.085,.155,.009),brown,roach)
for s in (-1,1):
    curve("roach rear cercus %d"%s,
          [(-.63,s*.12,-.05),(-.79,s*.19,-.07),(-.91,s*.25,-.09)],
          .012,brown,roach)
for i in range(7):
    x=.20-i*.12
    ell("roach abdominal sternite %02d"%i,(x,0,-.065),
        (.08,.29-.02*i,.12),brown if i%2==0 else tan,roach)
for s in (-1,1):
    shield("curved articulated elytron %d"%s,.23,-.69,s*.14,.18,.13,.060,
           bronze,roach)
    # Low-relief longitudinal wing veins break the smooth toy-like roach shell.
    for vein_idx, offset in enumerate((-.060,.015,.078)):
        curve("roach elytron vein %d %d"%(s,vein_idx),
              [(.20,s*(.14+offset),.182),(-.18,s*(.14+offset),.196),
               (-.52,s*(.14+offset*.60),.153)],
              .0035,brown,roach)
    ell("roach compound eye %d"%s,(.71,s*.15,.025),(.064,.029,.060),eye,roach)
    curve("roach filiform antenna %d"%s,
        [(.76,s*.10,.025),(.96,s*.17,.06),(1.22,s*.25,.02),
         (1.45,s*.34,-.10)],.005,dark,roach)
    for leg in range(3):
        x=.35-leg*.34
        hip=Vector((x,s*.20,-.04))
        femur=Vector((x+.15-leg*.12,s*.43,-.14))
        foot=Vector((x+.23-leg*.18,s*.53,-.27))
        gait=root("roach gait pivot %d %d"%(s,leg),(0,0,0))
        gait.parent=roach;gait.location=hip
        taper("roach femur %d %d"%(s,leg),(0,0,0),femur-hip,.054,.026,brown,gait)
        ell("roach knee %d %d"%(s,leg),femur-hip,(.035,.035,.035),dark,gait)
        taper("roach tibia %d %d"%(s,leg),femur-hip,foot-hip,.024,.009,brown,gait)
        for spike in range(4):
            t=(spike+1)/5
            p=(femur-hip).lerp(foot-hip,t)
            taper("roach tibial spine",p,
                  p+Vector((-.04,s*.035,.015)),.007,.001,dark,gait)
        taper("roach tarsus",foot-hip,
              foot-hip+Vector((.13,s*.03,-.01)),.010,.002,dark,gait)

# Organic leaf silhouettes, subdued debris and background-only vegetation.
# No tall foreground sticks should bisect the two specimens.
# The former flattened UV sphere exposed its silhouette as a black horizontal band
# at the bottom of the portrait image. A broad soil plane covers the entire
# orthographic camera footprint, including its near/bottom rays.
bpy.ops.mesh.primitive_plane_add(size=2, location=(0,0,-.066))
earth=bpy.context.object
earth.name="continuous forest floor - no visible edge"
earth.scale=(80,80,1)
earth.data.materials.append(soil)
rng=random.Random(6801)
def leaf_blade(name,center,length,width,heading,material_ref):
    verts=[];faces=[]
    for i in range(9):
        t=i/8
        w=width*(math.sin(math.pi*t)**.72)
        for side in (-1,1):
            along=length*(t-.5)
            across=side*w
            x=center[0]+along*math.cos(heading)-across*math.sin(heading)
            y=center[1]+along*math.sin(heading)+across*math.cos(heading)
            z=center[2]+.015*math.sin(math.pi*t)+.005*side
            verts.append((x,y,z))
    for i in range(8):
        a=i*2;faces.append((a,a+2,a+3,a+1))
    mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.update()
    obj=bpy.data.objects.new(name,mesh);scene.collection.objects.link(obj)
    mesh.materials.append(material_ref)
    for poly in mesh.polygons:poly.use_smooth=True
    return obj
for i in range(190):
    x=rng.uniform(-4.2,4.2);y=rng.uniform(-3.6,3.8)
    if abs(x)<1.45 and abs(y)<.65:continue
    leaf_blade("curved fallen leaf",(x,y,-.066),rng.uniform(.09,.33),
               rng.uniform(.015,.065),rng.uniform(-math.pi,math.pi),
               leafmat if i%4 else green)
# Low foreground moss/leaf litter supplies depth without obscuring the insect silhouettes.
# Place clusters outside the central encounter corridor; preserve clean anatomy visibility.
for i in range(120):
    x=rng.uniform(-3.3,3.3);y=rng.uniform(-2.8,-1.0)
    if abs(x)<1.55 and y>-1.9:
        continue
    leaf_blade("foreground organic litter",
               (x,y,-.045+rng.uniform(0,.025)),
               rng.uniform(.11,.42),rng.uniform(.025,.095),
               rng.uniform(-math.pi,math.pi),
               green if i%5==0 else leafmat)
for i in range(35):
    x=rng.uniform(-3.1,3.1);y=rng.uniform(-2.7,2.9)
    if abs(x)<1.4 and abs(y)<.9:
        continue
    ell("irregular soil pebble",(x,y,-.045),
        (rng.uniform(.018,.052),rng.uniform(.014,.038),rng.uniform(.008,.024)),
        soil,segments=10,rings=6)
# Rear-only vegetation, away from the subjects and their camera sightlines.
for i in range(30):
    x=rng.uniform(-3.7,3.7);y=rng.uniform(1.45,3.65)
    if i%5==0:
        taper("distant mossy stem",(x,y,-.12),
              (x+rng.uniform(-.12,.12),y,.45+rng.random()*.55),
              .025,.008,brown)
    for j in range(3):
        heading=rng.uniform(-math.pi,math.pi)
        leaf_blade("layered understory blade",
                   (x+rng.uniform(-.13,.13),y+rng.uniform(-.13,.13),.04+j*.09),
                   rng.uniform(.23,.53),rng.uniform(.045,.10),
                   heading,green)

# Layered forest: hide the infinite grey horizon and create depth silhouettes.
# Everything is behind the specimens; no foreground obstructions.
back_verts=[(-9,6,-.35),(9,6,-.35),(9,6,7),(-9,6,7)]
back_mesh=bpy.data.meshes.new("forest depth curtain mesh")
back_mesh.from_pydata(back_verts,[],[(0,1,2,3)]);back_mesh.update()
back_obj=bpy.data.objects.new("deep forest background",back_mesh)
scene.collection.objects.link(back_obj);back_mesh.materials.append(forest_depth)
for i in range(17):
    x=rng.uniform(-6.4,6.4);y=rng.uniform(3.9,5.7)
    height=rng.uniform(2.0,4.9)
    taper("rough layered tree trunk",(x,y,-.12),
          (x+rng.uniform(-.22,.22),y+.08,height),
          rng.uniform(.085,.18),rng.uniform(.055,.12),bark)
    for j in range(7):
        leaf_blade("high background foliage",
                   (x+rng.uniform(-.65,.65),y+rng.uniform(-.5,.5),
                    height*.65+rng.uniform(-.35,.6)),
                   rng.uniform(.35,.8),rng.uniform(.09,.20),
                   rng.uniform(-math.pi,math.pi),green)

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
camera.location=(.8,-5.0,2.45)
direction=Vector((0,0,.30))-camera.location
camera.rotation_euler=direction.to_track_quat("-Z","Y").to_euler()
camera_data.type="ORTHO";camera_data.ortho_scale=6.6
# Portrait-safe specimen tracking: complete insects must remain within horizontal margins.
# Earlier V6.8.3 preview visibly clipped both subjects at frame 1/48.
# Camera language: wasp anatomy -> complete two-subject encounter -> roach anatomy.
# The middle still remains a wide safety shot; the ends intentionally isolate each rig.
for frame,focus,scale in [(1,-.50,6.25),(12,-.38,6.10),
                          (24,0,5.85),(36,.26,6.15),(48,.35,6.30)]:
    camera.location=(.8+focus*.60,-5.0,2.45)
    target=Vector((focus,0,.30))
    camera.rotation_euler=(target-camera.location).to_track_quat("-Z","Y").to_euler()
    camera.keyframe_insert(data_path="location",frame=frame)
    camera.keyframe_insert(data_path="rotation_euler",frame=frame)
    camera_data.ortho_scale=scale
    camera_data.keyframe_insert(data_path="ortho_scale",frame=frame)
# A legible two-second action: approach, hovering lift and leg/antenna response.
# Preserve enough clearance for anatomy inspection; this is NOT a sting shot.
for f in (1,7,13,19,25,31,37,43,48):
    t=(f-1)/47
    wasp.location=(-.90+.62*t,-.18+.06*math.sin(math.pi*t),.43+.33*math.sin(math.pi*t))
    wasp.keyframe_insert(data_path="location",frame=f)
    wasp.rotation_euler.z=-.16+.13*t
    wasp.keyframe_insert(data_path="rotation_euler",frame=f)
    roach.location=(.84-.19*t,.20,.20+.024*math.sin(math.pi*3*t))
    roach.keyframe_insert(data_path="location",frame=f)
    roach.rotation_euler.z=math.pi+.05*math.sin(math.pi*2*t)
    roach.keyframe_insert(data_path="rotation_euler",frame=f)
for obj in list(bpy.data.objects):
    if obj.name.startswith(("wasp gait pivot","roach gait pivot")):
        # Rotate the entire articulated leg from its hip, not isolated femur
        # and tibia meshes around their centers (which visibly disconnected joints).
        phase=(sum(ord(c) for c in obj.name)%7)*.67
        amplitude=.20 if obj.name.startswith("roach") else .29
        for f in (1,7,13,19,25,31,37,43,48):
            obj.rotation_euler.y=amplitude*math.sin((f-1)*.29+phase)
            obj.rotation_euler.z=.11*math.cos((f-1)*.29+phase)
            obj.keyframe_insert(data_path="rotation_euler",frame=f)
    if obj.name.startswith("roach filiform antenna"):
        for f in (1,13,25,37,48):
            obj.rotation_euler.z=.055*math.sin((f-1)*.17)
            obj.keyframe_insert(data_path="rotation_euler",frame=f)

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
    scene.render.resolution_x=540
    scene.render.resolution_y=960
    scene.frame_set(24)
    scene.render.filepath=output
    bpy.ops.render.render(write_still=True)
print("JEWEL_V68_ANATOMY_RENDER_DONE", "motion" if motion else "still")
