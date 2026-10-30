"""V6.8.19 clean-room insect anatomy/rig proof, NOT a film approval.
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
scene.frame_end=int(os.environ.get("V68_FRAMES","48"))
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

emerald=material("iridescent emerald cuticle",(.008,.095,.075),.39,.48,noise=57)
blue=material("blue-green sclerites",(.011,.050,.064),.48,.36,noise=52)
dark=material("joint membranes",(.016,.022,.018),.76)
leg_amber=material("jewel wasp muted amber leg cuticle",(.115,.044,.020),.70,.06,noise=31)
eye=material("micro-faceted compound eye dark",(.008,.012,.011),.35,.06,noise=165)
brown=material("roach dark chitin",(.035,.015,.008),.59,.07,noise=47)
bronze=material("roach elytra",(.026,.010,.005),.78,.035,noise=95)
tan=material("ventral segment",(.056,.024,.014),.83)
wing=material("transparent wasp wing membrane",(.075,.145,.135),.72,0,.19)
vein=material("membrane veins",(.11,.16,.14),.59)
soil=material("soil granular",(.065,.053,.037),.98,noise=23)
leafmat=material("leaf litter",(.19,.13,.052),.94,noise=14)
green=material("understory leaves",(.028,.073,.031),.86,noise=17)
green_shadow=material("shadowed understory leaves",(.019,.045,.020),.91,noise=22)
green_olive=material("olive understory leaves",(.053,.068,.028),.87,noise=19)
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
        width=halfwidth*(.04+.96*math.sin(math.pi*t)**.72)
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
    sol=obj.modifiers.new("thin organic shell","SOLIDIFY");sol.thickness=.002
    # Subtle smoothing keeps the elytral contour from reading as a hard plate.
    bevel=obj.modifiers.new("soft elytron contour","SUBSURF");bevel.levels=1
    return obj

wasp=root("ANATOMY_WASP_ROOT",(-.68,-.18,.43),-.10)
# Scale both complete insect rigs to fit the narrow 9:16 composition.
wasp.scale=(.78,.78,.78)
ell("wasp head",(.39,0,.05),(.142,.090,.073),emerald,wasp)
ell("wasp thorax",(.11,0,.06),(.270,.166,.151),blue,wasp)
ell("wasp petiole",(-.17,0,.03),(.18,.075,.075),dark,wasp)
# One continuous spindle-shaped gaster, not six visibly separate toy beads.
# Narrow inter-tergite seams are material bands on the SAME mesh.
verts=[];faces=[];rings=43;around=20
for i in range(rings):
    t=i/(rings-1)
    x=-.275-.66*t
    profile=max(.025,math.sin(math.pi*t)**.60)
    ry=.145*profile*(1-.30*t)
    rz=.118*profile*(1-.26*t)
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
    face.material_index=1 if axial in (8,15,22,29,36) else (0 if axial<23 else 1)
for s in (-1,1):
    ell("wasp eye %d"%s,(.433,s*.094,.073),(.025,.012,.030),eye,wasp)
    curve("wasp geniculate antenna %d"%s,
        [(.50,s*.07,.12),(.63,s*.12,.19),(.71,s*.17,.19),(.80,s*.18,.13)],
        .007,dark,wasp)
    # Small paired mandibles and palps distinguish the wasp face from a sphere.
    curve("wasp mandibular palp %d"%s,
          [(.52,s*.065,-.015),(.59,s*.09,-.06),(.64,s*.075,-.085)],
          .008,dark,wasp)
    for leg in range(3):
        x=.29-leg*.19;y=s*.15
        # Front/mid/hind legs need different femur directions and a real
        # knee-to-tibia bend; V6.8.16 read as six near-vertical stilts.
        hip=Vector((x,y,.01))
        knee=Vector((x+( .18 if leg==0 else -.05 if leg==1 else -.19),
                     s*(.28 if leg==0 else .33 if leg==1 else .30),
                     -.17 if leg<2 else -.13))
        ankle=Vector((x+( .27 if leg==0 else .01 if leg==1 else -.31),
                      s*(.39 if leg==0 else .49 if leg==1 else .43),
                      -.35 if leg==0 else -.37 if leg==1 else -.36))
        gait=root("wasp gait pivot %d %d"%(s,leg),(0,0,0))
        gait.parent=wasp;gait.location=hip
        femur_joint=(knee-hip)*.35+Vector((.015,s*.015,.028))
        taper("wasp coxa %d %d"%(s,leg),(0,0,0),femur_joint,.020,.016,leg_amber,gait)
        ell("wasp femur joint %d %d"%(s,leg),femur_joint,(.016,.016,.016),dark,gait)
        taper("wasp femur %d %d"%(s,leg),femur_joint,knee-hip,.018,.013,leg_amber,gait)
        ell("wasp knee %d %d"%(s,leg),knee-hip,(.014,.014,.014),dark,gait)
        taper("wasp tibia %d %d"%(s,leg),knee-hip,ankle-hip,.011,.004,leg_amber,gait)
        taper("wasp tarsus %d %d"%(s,leg),ankle-hip,
              ankle-hip+Vector((.09,s*.025,-.02)),.009,.002,dark,gait)
    for hind in (0,1):
        pivot=root("wing hinge %d %d"%(s,hind),(0,0,0))
        pivot.parent=wasp;pivot.location=(.08-hind*.12,s*.14,.16)
        span=.50 if hind==0 else .34
        verts=[];faces=[]
        for i in range(17):
            t=i/16;breadth=(.067 if hind==0 else .044)*math.sin(math.pi*t)**.8
            for side in (-1,1):
                verts.append((-.29*t+side*breadth,s*span*t,.018*math.sin(math.pi*t)))
        for i in range(16):
            a=2*i;faces.append((a,a+2,a+3,a+1))
        mesh=bpy.data.meshes.new("wasp wing membrane");mesh.from_pydata(verts,[],faces)
        mesh.update();o=bpy.data.objects.new("veined membrane",mesh)
        scene.collection.objects.link(o);o.parent=pivot;mesh.materials.append(wing)
        curve("wing longitudinal vein",[(0,0,0),(-.08,s*span*.50,.02),
             (-.16,s*span*.92,0)],.003,vein,pivot)
        for f in range(1,49):
            pivot.rotation_euler.x=s*(.10+.25*math.sin(f*1.73+hind*.9))
            pivot.keyframe_insert(data_path="rotation_euler",frame=f)

roach=root("ANATOMY_ROACH_ROOT",(.72,.20,.20),math.pi)
roach.scale=(.78,.78,.78)
# V6.8.10: visual macro review: dark continuous dorsal cuticle, overlapping\n# elytra, tucked head, and smaller eyes instead of a bead-like toy face.\n# V6.8.9: continuous flattened cockroach abdomen with cuticular seam bands.
# The earlier seven intersecting oval sternites resembled toy beads.
abd_verts=[];abd_faces=[];abd_rings=42;abd_sides=24
for i in range(abd_rings):
    t=i/(abd_rings-1)
    x=-.75+1.13*t
    profile=max(.006,math.sin(math.pi*(.01+.98*t))**.52)
    ry=.285*profile*(1+.06*math.sin(math.pi*t))
    rz=.119*profile
    for j in range(abd_sides):
        angle=math.tau*j/abd_sides
        abd_verts.append((x,ry*math.cos(angle),-.012+rz*math.sin(angle)))
for i in range(abd_rings-1):
    for j in range(abd_sides):
        k=i*abd_sides+j;kn=i*abd_sides+(j+1)%abd_sides
        abd_faces.append((k,kn,kn+abd_sides,k+abd_sides))
# Close the two abdomen ends: the V6.8.12 macro exposed an open ring.
abd_faces.append(tuple(reversed(range(abd_sides))))
abd_faces.append(tuple((abd_rings-1)*abd_sides+j for j in range(abd_sides)))
abd_mesh=bpy.data.meshes.new("roach continuous cuticular abdomen mesh")
abd_mesh.from_pydata(abd_verts,[],abd_faces);abd_mesh.update()
abd_obj=bpy.data.objects.new("roach continuous abdomen",abd_mesh)
scene.collection.objects.link(abd_obj);abd_obj.parent=roach
abd_mesh.materials.append(brown);abd_mesh.materials.append(tan)
for polygon in abd_mesh.polygons:
    polygon.use_smooth=True
    axial=polygon.index//abd_sides
    polygon.material_index=1 if axial in (7,13,19,25,31,37) else 0
# A real cockroach pronotum is a low, broad protective dorsal plate.
# The V6.8.16 oval sphere and button-like top read as toy geometry.
shield("roach integrated pronotal shield",.68,.24,0,.215,.082,.046,
       bronze,roach)
ell("roach tucked head",(.56,0,.007),(.111,.101,.061),brown,roach)
for s in (-1,1):
    curve("roach rear cercus %d"%s,
          [(-.63,s*.12,-.05),(-.79,s*.19,-.07),(-.91,s*.25,-.09)],
          .012,brown,roach)
for s in (-1,1):
    # Lower the elytra onto the abdomen, curve them over the body and taper
    # their outline. The old raised flat plates looked like detached toy wings.
    shield("overlapping dorsal elytron %d"%s,.27,-.74,s*.083,.165,.094,.038,
           bronze,roach)
    # Low-relief longitudinal wing veins break the smooth toy-like roach shell.
    for vein_idx, offset in enumerate((-.045,.055)):
        # Keep veins embedded as subtle relief, not elevated rail tracks.
        curve("roach elytron vein %d %d"%(s,vein_idx),
              [(.19,s*(.096+offset),.115),(-.18,s*(.096+offset),.131),
               (-.54,s*(.096+offset*.60),.116)],
              .0022,brown,roach)
    ell("roach compound eye %d"%s,(.605,s*.102,.025),(.030,.018,.032),eye,roach)
    curve("roach filiform antenna %d"%s,
        [(.65,s*.095,.025),(.86,s*.16,.06),(1.13,s*.25,.02),
         (1.38,s*.34,-.10)],.005,dark,roach)
    for leg in range(3):
        x=.35-leg*.34
        hip=Vector((x,s*.20,-.04))
        femur=Vector((x+.15-leg*.12,s*.43,-.14))
        foot=Vector((x+.23-leg*.18,s*.53,-.27))
        gait=root("roach gait pivot %d %d"%(s,leg),(0,0,0))
        gait.parent=roach;gait.location=hip
        taper("roach femur %d %d"%(s,leg),(0,0,0),femur-hip,.027,.015,brown,gait)
        ell("roach knee %d %d"%(s,leg),femur-hip,(.020,.020,.020),dark,gait)
        taper("roach tibia %d %d"%(s,leg),femur-hip,foot-hip,.013,.005,brown,gait)
        for spike in range(4):
            t=(spike+1)/5
            p=(femur-hip).lerp(foot-hip,t)
            taper("roach tibial spine",p,
                  p+Vector((-.04,s*.035,.015)),.007,.001,dark,gait)
        taper("roach tarsus",foot-hip,
              foot-hip+Vector((.09,s*.03,-.01)),.007,.002,dark,gait)

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
            # Raised midrib, curled tip and asymmetric edge break paper-flat leaf silhouettes.
            z=center[2]+.075*math.sin(math.pi*t)+.025*t*t+.016*side*math.sin(2*math.pi*t)
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
               leafmat if i%4 else (green_olive if i%8 else green_shadow))
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
                   heading,(green_shadow if (i+j)%4==0 else green_olive if (i+j)%5==0 else green))

# V6.8.9: upright, multi-plane fern crowns behind the action corridor.
# Horizontal ground litter alone looked like flat stickers in the actual proof.
for i in range(20):
    x=rng.uniform(-2.25,2.25)
    y=rng.uniform(1.15,3.25)
    height=rng.uniform(.38,1.05)
    lean=rng.uniform(-.22,.22)
    taper("living fern rachis",(x,y,-.04),
          (x+lean,y+.08,height),.012,.003,green)
    for j in range(4):
        z=.12+height*(j+.7)/5
        spread=(.12+.13*math.sin(math.pi*(j+1)/5))
        for side in (-1,1):
            leaf_blade("raised fern pinna",
                       (x+lean*(z/height)+side*spread,y+.02,z),
                       rng.uniform(.17,.32),rng.uniform(.035,.07),
                       side*rng.uniform(.10,.52),green)
# Broken decaying wood and roots establish forest scale in the rear plane.
for i in range(5):
    x=rng.uniform(-2.5,2.5);y=rng.uniform(1.45,3.4)
    taper("fallen decaying branch",(x,y,-.025),
          (x+rng.uniform(-.8,.8),y+rng.uniform(-.2,.2),.025),
          rng.uniform(.045,.085),rng.uniform(.022,.048),bark)

# Asymmetric understory clusters at mid-depth create a real layered forest
# rather than an empty soil stage. Keep the insect corridor unobstructed.
for i in range(55):
    side=-1 if i%2 else 1
    x=side*rng.uniform(1.50,3.65)
    y=rng.uniform(.85,3.2)
    z=rng.uniform(.14,.70)
    leaf_blade("midground fern leaflet",
               (x,y,z),rng.uniform(.22,.55),rng.uniform(.035,.11),
               rng.uniform(-math.pi,math.pi),(green_shadow if i%3==0 else green_olive if i%5==0 else green))
# Exposed branching roots interrupt the cylindrical bases of distant trees.
for i in range(11):
    x=-3.3+i*.64
    y=3.7+rng.uniform(-.20,.30)
    for side in (-1,1):
        curve("buried tree root",
              [(x,y,-.05),(x+side*.23,y-.18,-.03),
               (x+side*.48,y-.34,-.045)],
              .022,bark,None)

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
                   rng.uniform(-math.pi,math.pi),(green_shadow if i%3==0 else green_olive if i%5==0 else green))

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
camera.location=(.8,-5.3,3.75)
direction=Vector((0,0,.82))-camera.location
camera.rotation_euler=direction.to_track_quat("-Z","Y").to_euler()
camera_data.type="ORTHO";camera_data.ortho_scale=5.9
# V6.8.7 review exposed clipped roach at frame 1 and an unlit bottom band.
# V6.8.8: aim the elevated camera at the midpoint of BOTH insects, not one.
# Portrait-safe specimen tracking: complete insects must remain within horizontal margins.
# Earlier V6.8.3 preview visibly clipped both subjects at frame 1/48.
# Camera language: wasp anatomy -> complete two-subject encounter -> roach anatomy.
# The middle still remains a wide safety shot; the ends intentionally isolate each rig.
for frame,focus,scale in [(1,-.04,5.95),(12,-.02,5.90),
                          (24,.02,5.80),(36,.05,5.90),(48,.08,5.95)]:
    # Preserve BOTH insect silhouettes: earlier focus=-.50 clipped the roach.
    # Higher camera elevation also keeps every bottom image ray above the soil.
    camera.location=(.8+focus*.60,-5.3,3.75)
    target=Vector((focus,0,.66))
    camera.rotation_euler=(target-camera.location).to_track_quat("-Z","Y").to_euler()
    camera.keyframe_insert(data_path="location",frame=frame)
    camera.keyframe_insert(data_path="rotation_euler",frame=frame)
    camera_data.ortho_scale=scale
    camera_data.keyframe_insert(data_path="ortho_scale",frame=frame)
# A legible two-second action: approach, hovering lift and leg/antenna response.
# Preserve enough clearance for anatomy inspection; this is NOT a sting shot.
def smoothstep(v):
    v=max(0.0,min(1.0,v))
    return v*v*(3.0-2.0*v)

# A two-second approach-to-touchdown diagnostic, not a fabricated sting.
# At frame 48, the scaled tarsi reach the soil; earlier proofs ended with
# the wasp hovering far above the ground and could not evaluate leg contact.
for f in (1,7,13,19,25,31,37,43,48):
    t=(f-1)/47
    landing=smoothstep((t-.46)/.54)
    wasp.location=(-.90+.62*t,-.18+.06*math.sin(math.pi*t),
                   .50+.16*math.sin(math.pi*t)-.295*landing)
    wasp.keyframe_insert(data_path="location",frame=f)
    wasp.rotation_euler.z=-.16+.13*t
    wasp.rotation_euler.x=.065*math.sin(2*math.pi*t)
    wasp.rotation_euler.y=.095*math.sin(2*math.pi*t)
    wasp.keyframe_insert(data_path="rotation_euler",frame=f)
    # Cockroach tarsi, too, should meet the floor instead of levitating.
    roach.location=(.84-.19*t,.20,.15+.012*math.sin(math.pi*3*t))
    roach.keyframe_insert(data_path="location",frame=f)
    roach.rotation_euler.z=math.pi+.05*math.sin(math.pi*2*t)
    roach.keyframe_insert(data_path="rotation_euler",frame=f)
for obj in list(bpy.data.objects):
    if obj.name.startswith(("wasp gait pivot","roach gait pivot")):
        # Alternating tripods, not six unrelated hash-based phases. Wasp
        # leg swing increases only as it approaches ground contact.
        side,leg=map(int,obj.name.split()[-2:])
        phase=0.0 if (leg+(1 if side>0 else 0))%2==0 else math.pi
        is_wasp=obj.name.startswith("wasp")
        for f in list(range(1,49,3))+[48]:
            t=(f-1)/47
            contact=smoothstep((t-.46)/.54)
            amplitude=(.06+.12*contact) if is_wasp else .19
            cycle=(f-1)*.36+phase
            obj.rotation_euler.y=amplitude*math.sin(cycle)
            obj.rotation_euler.z=(.025+.045*contact if is_wasp else .075)*math.cos(cycle)
            obj.keyframe_insert(data_path="rotation_euler",frame=f)
    if obj.name.startswith("wing hinge"):
        # Visible flight beats decelerate and settle during landing.
        # Overwrite the initial per-frame wing keys with a landing envelope.
        side,hind=map(int,obj.name.split()[-2:])
        for f in range(1,49):
            contact=smoothstep(((f-1)/47-.55)/.45)
            obj.rotation_euler.x=side*(.14+(1-contact)*.48*math.sin(f*1.32+hind*.65))
            obj.rotation_euler.y=contact*(.12 if hind==0 else .07)
            obj.keyframe_insert(data_path="rotation_euler",frame=f)
    if obj.name.startswith("roach filiform antenna"):
        for f in (1,13,25,37,48):
            obj.rotation_euler.z=.055*math.sin((f-1)*.17)
            obj.keyframe_insert(data_path="rotation_euler",frame=f)

# Independent roach macro still complements the safe two-insect motion proof
# and makes leg joints, pronotum and abdomen inspectable at useful pixel scale.
# It is diagnostic evidence, not an approval or a new film chapter.
if os.environ.get("V68_SHOT","").lower()=="roach_macro":
    camera.animation_data_clear()
    camera_data.animation_data_clear()
    for f in (1,24,48):
        scene.frame_set(f)
        focus=roach.matrix_world @ Vector((-.08,0,.06))
        camera.location=focus+Vector((1.05,-2.80,1.52))
        camera.rotation_euler=(focus-camera.location).to_track_quat("-Z","Y").to_euler()
        camera_data.ortho_scale=3.10
        camera.keyframe_insert(data_path="location",frame=f)
        camera.keyframe_insert(data_path="rotation_euler",frame=f)
        camera_data.keyframe_insert(data_path="ortho_scale",frame=f)


# Independent wasp close-up: diagnostic of compound eyes, petiole, transparent
# wing hinge and six attached legs. This is NOT full-film visual approval.
if os.environ.get("V68_SHOT","").lower()=="wasp_macro":
    camera.animation_data_clear()
    camera_data.animation_data_clear()
    for f in (1,24,48):
        scene.frame_set(f)
        focus=wasp.matrix_world @ Vector((-.30,0,.055))
        camera.location=focus+Vector((1.45,-2.55,1.40))
        camera.rotation_euler=(focus-camera.location).to_track_quat("-Z","Y").to_euler()
        camera_data.ortho_scale=3.00
        camera.keyframe_insert(data_path="location",frame=f)
        camera.keyframe_insert(data_path="rotation_euler",frame=f)
        camera_data.keyframe_insert(data_path="ortho_scale",frame=f)

output=os.environ.get("BLENDER_OUTPUT","/tmp/jewel_wasp_v68_anatomy.png")
motion=os.environ.get("V68_MOTION","0")=="1"
# A 24-frame close-up must show the ENTIRE approach-to-touchdown, not just
# source frames 1-24 (which ended while the insect was still hovering).
# Preserve the 48-frame master animation and compress only short motion proofs.
if motion and scene.frame_end == 24:
    factor=(scene.frame_end-1)/47.0
    for action in bpy.data.actions:
        for fc in action.fcurves:
            for key in fc.keyframe_points:
                key.co.x=1+(key.co.x-1)*factor
                key.handle_left.x=1+(key.handle_left.x-1)*factor
                key.handle_right.x=1+(key.handle_right.x-1)*factor
            fc.update()
    print("V68_MACRO_FULL_ACTION_RETIMED_48_TO_24", flush=True)
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
    scene.frame_set(int(os.environ.get("V68_STILL_FRAME","24")))
    scene.render.filepath=output
    bpy.ops.render.render(write_still=True)
print("JEWEL_V68_ANATOMY_RENDER_DONE", "motion" if motion else "still")
