"""Jewel Wasp 14-chapter DRAFT scene builder using the actual V6.8.25 rigs.
Not final, not V4, and never an approval of realism. Each chapter is 240 frames.
Preview with JW_MODE=still or motion before running JW_MODE=draft.
"""
import os, pathlib, math
import bpy
from mathutils import Vector

chapter=int(os.getenv("JW_CHAPTER","0"))
assert 0 <= chapter < 14
mode=os.getenv("JW_MODE","still")
assert mode in ("preflight","still","motion","draft")
source=pathlib.Path(__file__).with_name("jewel_wasp_v68_anatomy_proof.py")
code=source.read_text()
boundary="# Independent roach macro still complements"
assert code.count(boundary)==1, "V6.8 scene builder changed; review integration"
# Reuse the entire V6.8.25 anatomical meshes, gait pivots, forest and materials.
# Skip the isolated 48-frame proof's camera/render tail; rebuild chapter action.
exec(compile(code.split(boundary)[0],str(source),"exec"),globals())
assert wasp.name=="ANATOMY_WASP_ROOT" and roach.name=="ANATOMY_ROACH_ROOT"
scene.frame_start=1;scene.frame_end=240;scene.render.fps=24
for actor in (wasp,roach,camera):
    actor.animation_data_clear()
camera_data.animation_data_clear()
# Keep the actual V6.8 articulated wing and tripod animation running for 10s.
for obj in bpy.data.objects:
    if obj.name.startswith(("wasp gait pivot","roach gait pivot","wing hinge",
                             "roach filiform antenna")):
        if obj.animation_data and obj.animation_data.action:
            for fc in obj.animation_data.action.fcurves:
                if not any(mod.type=="CYCLES" for mod in fc.modifiers):
                    fc.modifiers.new("CYCLES")

# Distinct narrative beats; 10 seconds each, 14 chapters total.
# All positions are world-space. Changes are a rough animatic, not physics QA.
titles=[
    "Forest encounter","Wasp pursuit","Cockroach escapes","Thoracic sting",
    "Temporary motor effect","Head ganglion sting","Neural response",
    "Changed walking behavior","Antenna guidance","Path to burrow",
    "Burrow entry","Egg placement","Larval development","Life-cycle finale"]
# (wasp start, wasp middle, wasp end, roach start, roach end)
poses=[
    ((-1.9,-.9,1.0),(-1.2,-.6,.78),(-.75,-.3,.52),(.95,.2,.18),(.70,.2,.18)),
    ((-2,-1.0,1.1),(-1.0,-.7,.85),(-.2,-.3,.60),(1.1,.3,.18),(.7,.3,.18)),
    ((-1.2,-.8,1.05),(-.4,-.5,.65),(.3,-.2,.50),(1.3,.2,.18),(.55,.35,.18)),
    ((-.55,-.8,.92),(.88,-.06,.56),(1.0,.03,.53),(.55,.2,.18),(.55,.2,.18)),
    ((-1.6,-.7,1.2),(-1.5,-.7,1.2),(-1.5,-.7,1.2),(.65,.15,.18),(.65,.15,.18)),
    ((-.45,-.85,.92),(.96,-.05,.56),(1.0,.02,.53),(.6,.2,.18),(.6,.2,.18)),
    ((-1.7,-.7,1.1),(-1.7,-.7,1.1),(-1.7,-.7,1.1),(.65,.15,.18),(.65,.15,.18)),
    ((-.9,-.5,.52),(-.5,-.4,.44),(-.2,-.3,.42),(.75,.2,.18),(.3,.25,.18)),
    ((-.8,-.4,.42),(-.5,-.1,.40),(-.2,.15,.42),(.9,.2,.18),(.25,.45,.18)),
    ((-.7,-.5,.52),(.1,.1,.42),(.8,.5,.40),(.75,.0,.18),(1.45,.95,.18)),
    ((.1,-.5,.52),(.05,-.10,.58),(-.50,-.30,.64),(.8,.1,.18),(1.6,1.10,-1.02)),
    ((1.0,.15,.50),(1.4,.6,.40),(1.7,.9,.42),(1.50,1.0,.18),(1.50,1.0,.18)),
    ((-1.6,-1.0,1.2),(-1.6,-1.0,1.2),(-1.6,-1.0,1.2),(1.5,1.0,.18),(1.5,1.0,.18)),
    ((1.60,1.10,-1.65),(1.60,1.10,-.62),(-.35,-.70,1.60),(.95,.2,.18),(.95,.2,.18))]
ws,wm,we,rs,re=poses[chapter]
def key_loc(actor,frame,point):
    actor.location=point;actor.keyframe_insert(data_path="location",frame=frame)
for f,p in ((1,ws),(120,wm),(240,we)):key_loc(wasp,f,p)
if chapter==13:
    # A visible rise from inside the burrow, then a distinct flight departure.
    # Keep adult scale constant throughout the shot, never grow the insect.
    wasp.scale=(.72,.72,.72)
    for f,p in ((1,(1.60,1.10,-1.65)),(50,(1.60,1.10,-1.48)),
                (90,(1.60,1.10,-1.12)),(120,(1.60,1.10,-.62)),
                (150,(1.60,1.10,-.04)),(180,(1.60,1.10,.72)),
                (205,(1.10,.55,1.16)),(240,(-.35,-.70,1.60))):
        key_loc(wasp,f,p)
for f,p in ((1,rs),(120,tuple((a+b)/2 for a,b in zip(rs,re))),(240,re)):
    key_loc(roach,f,p)
wasp.rotation_euler.z=-.10 if chapter<8 else .12
# Burrow approach must face the actual travel direction, not walk backwards.
roach.rotation_euler.z=(math.atan2(re[1]-rs[1],re[0]-rs[0])
                         if chapter in (8,9,10) and
                         math.hypot(re[0]-rs[0],re[1]-rs[1])>.05
                         else math.pi)
# Stage the sting and oviposition on the correct side of the roach.
# Keyframe the complete root rig, not a disconnected floating needle.
if chapter in (3,5,11):
    for f,dx,dy,dz in ((75,.94,-.46,.48),(112,.61,-.14,.27),
                        (145,.58,-.13,.25),(171,.60,-.13,.25),
                        (205,.95,-.47,.50)):
        scene.frame_set(f);bpy.context.view_layer.update()
        local=(Vector((.025,.34,-.11)) if chapter==11 else
               Vector((.27 if chapter==3 else .56,0,.11)))
        target=roach.matrix_world @ local
        wasp.location=target+Vector((dx,dy,dz))
        wasp.keyframe_insert(data_path="location",frame=f)
if chapter==10:
    # The animal must visibly cross the mouth and descend, not stop beside it.
    for f,xyz,scale in ((80,(1.14,.63,.18),1.0),
                        (125,(1.47,.88,.08),1.0),
                        (175,(1.60,1.08,-.34),1.0),
                        (210,(1.60,1.10,-.72),1.0),
                        (240,(1.60,1.10,-1.02),1.0)):
        roach.location=xyz;roach.keyframe_insert(data_path="location",frame=f)
        roach.scale=(scale,)*3;roach.keyframe_insert(data_path="scale",frame=f)
    # Insect stays physically above ground until it reaches the entrance.
    assert roach.location.z<0
# Keep the full-size roach rig as it enters; pitch head-down rather than shrink.
if chapter==10:
    for f,pitch in ((1,0.0),(110,0.0),(155,.22),(195,.76),(240,1.08)):
        roach.rotation_euler.y=pitch
        roach.keyframe_insert(data_path="rotation_euler",frame=f)
scene.frame_set(1)
for actor in (wasp,roach):
    actor.keyframe_insert(data_path="rotation_euler",frame=1)
    actor.keyframe_insert(data_path="rotation_euler",frame=240)
# Use selective absence, rather than a toy wasp obstructing the science shots.
if chapter in (4,6,12):
    for ob in bpy.data.objects:
        current=ob
        while current:
            if current==wasp:
                ob.hide_render=True;break
            current=current.parent

# Finale must be a different event: adult wasp emerges from the burrow.
# Keep the original cockroach rig in memory but hide it only in this shot.
if chapter==13:
    for ob in bpy.data.objects:
        current=ob
        while current:
            if current==roach:
                ob.hide_render=True;break
            current=current.parent

# A real geometric opening: the original dark disc sat ON the opaque floor,
# so the cockroach appeared to sink through solid soil instead of entering.
# Preserve the V6.8 forest; only replace its ground plane in burrow chapters.
if chapter in (9,10,11,12,13):
    earth.hide_render=True
    holemat=material("burrow interior dark",(.007,.006,.004),rough=.99)
    cx,cy=1.60,1.10
    sides=64
    rings=[(.54,-.54),(.56,-.35),(.59,-.17),(.65,-.066),
           (.78,-.066),(1.4,-.066),(3.0,-.066),(30.0,-.066)]
    vertices=[]
    for radius,z in rings:
        for i in range(sides):
            theta=2*math.pi*i/sides
            vertices.append((cx+radius*1.13*math.cos(theta),
                             cy+radius*.91*math.sin(theta),z))
    faces=[]
    for ring in range(len(rings)-1):
        for i in range(sides):
            a=ring*sides+i
            b=ring*sides+(i+1)%sides
            faces.append((a,a+sides,b+sides,b))
    mesh=bpy.data.meshes.new("burrow cutout ground and tunnel wall mesh")
    mesh.from_pydata(vertices,[],faces);mesh.update()
    floor=bpy.data.objects.new("actual open burrow soil geometry",mesh)
    scene.collection.objects.link(floor)
    mesh.materials.append(soil)
    for poly in mesh.polygons:poly.use_smooth=True
    ell("dark bottom INSIDE burrow",(cx,cy,-.57),(.62,.50,.018),holemat)
    for i in range(24):
        theta=2*math.pi*i/24
        ell("irregular earth rim",
            (cx+(.73+.05*math.sin(i*2.1))*math.cos(theta),
             cy+(.60+.04*math.cos(i*1.9))*math.sin(theta),-.047),
            (.075,.065,.040),soil,segments=12,rings=8)
    # Hide nearby overgrowth from the burrow's action camera, not the forest.
    for obj in bpy.data.objects:
        if obj.name.startswith(("living fern rachis","raised fern pinna",
                                "midground fern leaflet")):
            obj.hide_render=True

# Real contact geometry: a sting must touch the thorax/head during the hold.
# Fail preflight rather than quietly rendering a floating fake sting.
if chapter in (3,5):
    bpy.ops.mesh.primitive_cone_add(vertices=14,radius1=.026,radius2=.001,depth=1)
    needle=bpy.context.object;needle.name="DRAFT anatomical sting contact"
    needle.data.materials.append(leg_amber)
    for frame,reach in ((1,.001),(80,.001),(108,.08),(120,1.0),
                        (145,1.0),(170,1.0),(195,.10),(240,.001)):
        scene.frame_set(frame);bpy.context.view_layer.update()
        start=wasp.matrix_world @ Vector((-.80,0,.04))
        target=roach.matrix_world @ Vector((.27 if chapter==3 else .56,0,.11))
        delta=target-start
        if frame in (120,145,170):
            assert .025<delta.length<.55, (
                "Sting preflight: subject separation %.3f at frame %d" %
                (delta.length,frame))
        length=max(.002,delta.length*reach)
        direction=delta.normalized() if delta.length>.001 else Vector((1,0,0))
        needle.location=start+direction*length*.5
        needle.rotation_euler=direction.to_track_quat("Z","Y").to_euler()
        needle.scale=(1,1,length)
        for attr in ("location","rotation_euler","scale"):
            needle.keyframe_insert(data_path=attr,frame=frame)
# Scientific diagram, explicitly stylized rather than pretending it is
# visible tissue through an opaque cockroach.
if chapter in (4,6):
    signal=material("schematic amber neural pulse",(.80,.24,.015),rough=.3)
    for i,x in enumerate((.25,.06,-.18,-.42)):
        node=ell("schematic ganglion %d"%i,(x,0,.17),(.055,.045,.035),signal,roach)
        for f in (1,60,120,180,240):
            amp=.6+.4*math.sin(f*.12+i)
            node.scale=(.055*amp,.045*amp,.035*amp)
            node.keyframe_insert(data_path="scale",frame=f)
if chapter==11:
    eggmat=material("egg ivory",(.76,.70,.49),rough=.78,noise=12)
    # Jewel wasp oviposits on a cockroach leg, not on the forest floor.
    # Mid-leg femur is parented to the gait pivot, so the egg follows the leg.
    egg_leg=bpy.data.objects.get("roach gait pivot 1 1")
    assert egg_leg is not None and egg_leg.parent==roach
    egg=ell("single jewel wasp egg",(.10,.17,-.08),(.036,.100,.028),eggmat,egg_leg)
    for f,size in ((1,.001),(108,.001),(145,.28),(170,.85),(240,1.0)):
        egg.scale=(.036*size,.100*size,.028*size)
        egg.keyframe_insert(data_path="scale",frame=f)
    # Animated ovipositor must actually approach the leg-attached egg.
    bpy.ops.mesh.primitive_cone_add(vertices=12,radius1=.012,radius2=.001,depth=1)
    ov=bpy.context.object;ov.name="DRAFT ovipositor depositing egg"
    ov.data.materials.append(leg_amber)
    for f,reach in ((1,.001),(90,.001),(115,.5),(140,1.0),
                    (168,1.0),(190,.25),(240,.001)):
        scene.frame_set(f);bpy.context.view_layer.update()
        a=wasp.matrix_world @ Vector((-.80,0,.04))
        b=egg.matrix_world.translation.copy()
        d=b-a
        if f in (140,168):
            assert d.length<.60, "Oviposition contact gap %.3f"%d.length
        length=max(.002,d.length*reach)
        ov.location=a+d.normalized()*length*.5
        ov.rotation_euler=d.to_track_quat("Z","Y").to_euler()
        ov.scale=(1,1,length)
        for attr in ("location","rotation_euler","scale"):
            ov.keyframe_insert(data_path=attr,frame=f)
if chapter==12:
    # One continuous tapered larval cuticle, not eight detached pearl spheres.
    # Shallow annular material changes are painted on the same watertight mesh.
    larvamat=material("organic warm-tan larval cuticle",(.53,.33,.17),rough=.92,noise=18)
    groove=material("subtle larval segment grooves",(.25,.13,.065),rough=.94,noise=14)
    verts=[];faces=[];nring=49;nsides=20
    for i in range(nring):
        t=i/(nring-1)
        profile=max(.045,math.sin(math.pi*t)**.62)*(1+.025*math.sin(16*math.pi*t))
        x=-.32+.58*t
        # Place the body against the roach flank, not hovering beside it.
        yc=.345+.012*math.sin(2*math.pi*t)
        zc=-.050+.012*math.sin(math.pi*t)
        for j in range(nsides):
            a=2*math.pi*j/nsides
            verts.append((x,yc+.072*profile*math.cos(a),
                          zc+.130*profile*math.sin(a)))
    for i in range(nring-1):
        for j in range(nsides):
            k=i*nsides;jnext=i*nsides+(j+1)%nsides
            faces.append((k,jnext,jnext+nsides,k+nsides))
    faces.append(tuple(reversed(range(nsides))))
    faces.append(tuple((nring-1)*nsides+j for j in range(nsides)))
    larva_mesh=bpy.data.meshes.new("continuous organic larva mesh")
    larva_mesh.from_pydata(verts,[],faces);larva_mesh.update()
    larva=bpy.data.objects.new("single growing jewel wasp larva",larva_mesh)
    scene.collection.objects.link(larva);larva.parent=roach
    larva_mesh.materials.append(larvamat);larva_mesh.materials.append(groove)
    headmat=material("larval amber head capsule",(.17,.075,.032),rough=.91)
    ell("attached larva head capsule",(.252,.345,-.050),(.036,.044,.050),headmat,larva,
        segments=20,rings=10)
    for poly in larva_mesh.polygons:
        poly.use_smooth=True
        axial=poly.index//nsides
        poly.material_index=1 if axial<nring-1 and axial%9==0 else 0
    # Mesh deformation, not merely scaling a static white object.
    larva.shape_key_add(name="Basis",from_mix=False)
    bend=larva.shape_key_add(name="Organic lateral contraction",from_mix=False)
    for idx,v in enumerate(bend.data):
        axial=(idx//nsides)/(nring-1)
        v.co.y+=.075*math.sin(math.pi*axial)*math.sin(2*math.pi*axial)
        v.co.z+=.026*math.sin(math.pi*axial)
    for f,size,sway,bendval in ((1,.25,0,0),(60,.40,.025,1),
                               (108,.56,-.025,0),(120,.62,.020,1),
                               (132,.68,-.020,0),(180,.83,.028,1),
                               (240,.82,0,0)):
        larva.scale=(size,size,size)
        larva.rotation_euler.z=sway
        bend.value=bendval
        larva.keyframe_insert(data_path="scale",frame=f)
        larva.keyframe_insert(data_path="rotation_euler",frame=f)
        bend.keyframe_insert(data_path="value",frame=f)
# Shot grammar: 14 independent cinematic compositions. Use perspective,
# eye-level/overhead alternation, close-ups and motivated tracking.
camera.animation_data_clear();camera_data.animation_data_clear()
camera_data.type="PERSP"
camera_data.sensor_fit="VERTICAL";camera_data.sensor_height=24
camera_data.lens=45
shot_sizes=[4.5,3.65,3.3,2.25,2.1,2.25,1.9,
            3.15,2.7,3.6,2.30,1.15,1.18,3.2]
offsets=[
    (1,-5.2,2.2),(-2.8,-4.0,1.1),(2.5,-4.0,1.0),
    (1.5,-3.4,.9),(-1.1,-3.2,1.2),(-1.5,-2.8,.7),
    (2.0,-3.0,.9),(-2.6,-4.0,1.3),(1.8,-3.5,.85),
    (1.0,-4.4,2.4),(-1.6,-3.8,2.4),(.35,-3.0,.65),
    (-.65,-2.7,.55),(-2.0,-5.0,2.3)]
for f in ((1,60,120,180,240) if chapter==13 else (1,120,240)):
    scene.frame_set(f)
    focus=(Vector(wasp.location)+Vector(roach.location))*.5
    if chapter in (3,5):
        contact=roach.matrix_world @ Vector((.27 if chapter==3 else .56,0,.11))
        # Include the entire wasp abdomen and cockroach in the sting frame.
        focus=contact*.72+Vector(wasp.location)*.28
    elif chapter in (4,6,7,12):
        focus=Vector(roach.location)
    elif chapter in (9,10):
        focus=Vector((1.5,.90,-.02))
    elif chapter==11:
        focus=egg.matrix_world.translation.copy()
    elif chapter==13:
        # Hold on the burrow during the rise; following the wasp at every
        # frame made it appear stationary against a sliding background.
        # Follow the departure only after the body has cleared the rim.
        mouth=Vector((1.60,1.10,-.03))
        focus=(mouth if f<=180 else
               mouth.lerp(Vector(wasp.location),(f-180)/60.0*.60))
    focus.z+=(.04 if chapter in (3,5,10,11,12) else .13)
    off=Vector(offsets[chapter]).normalized()
    # Portrait vertical field of view: height=distance*sensor_height/lens.
    height=(2.85+.75*max(0,f-180)/60.0 if chapter==13 else
            shot_sizes[chapter]*(1.08 if f==1 else .96 if f==240 else 1))
    camera.location=focus+off*(height*camera_data.lens/camera_data.sensor_height)
    camera.rotation_euler=(focus-camera.location).to_track_quat("-Z","Y").to_euler()
    camera.keyframe_insert(data_path="location",frame=f)
    camera.keyframe_insert(data_path="rotation_euler",frame=f)
# Subject separation from the forest with an additional broad, soft fill.
fill_data=bpy.data.lights.new("story subject legibility fill","AREA")
fill_data.energy=320;fill_data.shape="DISK";fill_data.size=3.0
fill=bpy.data.objects.new("story subject legibility fill",fill_data)
scene.collection.objects.link(fill);fill.location=(1.0,-2.4,3.3)
fill.rotation_euler=(Vector((.3,.1,.3))-fill.location).to_track_quat("-Z","Y").to_euler()
# Cheap structural checks never substitute for actual still/motion visual QA.
assert len(titles)==len(poses)==len(shot_sizes)==len(offsets)==14
assert scene.frame_end-scene.frame_start+1==240

scene.render.engine="BLENDER_EEVEE_NEXT"
# Clearer review images; 162x288 draft pixels are NOT a visual approval.
# Allow deliberate low-res draft assembly, but don't inspect tiny proofs.
scene.render.resolution_x=360;scene.render.resolution_y=640
requested=int(os.getenv("JW_RES_PERCENT","100" if mode!="draft" else "60"))
scene.render.resolution_percentage=(max(75,requested) if mode=="motion" else
                                    max(100,requested) if mode in ("still","preflight")
                                    else requested)
assert 50<=scene.render.resolution_percentage<=100
scene.render.image_settings.color_mode="RGB"
scene.render.filepath=os.environ["BLENDER_OUTPUT"]
if mode=="preflight":
    # Blender executes every action and camera assertion without costly pixels.
    from bpy_extras.object_utils import world_to_camera_view
    proof_frames={3:145,5:145,10:195,11:190,12:180}
    frame=proof_frames.get(chapter,145)
    scene.frame_set(frame);bpy.context.view_layer.update()
    if chapter in (3,5):
        target=roach.matrix_world @ Vector((.27 if chapter==3 else .56,0,.11))
    elif chapter==10:
        target=Vector((1.60,1.10,-.12))
    elif chapter==11:
        target=egg.matrix_world.translation.copy()
    elif chapter==12:
        target=larva.matrix_world @ Vector((-.05,.345,-.050))
    elif chapter==13:
        # Geometry-only assertions: never substitute for visual emergence QA.
        scene.frame_set(1); low=float(wasp.location.z)
        scene.frame_set(120); mid=float(wasp.location.z)
        scene.frame_set(180); high=float(wasp.location.z)
        assert low<-1.2 and mid<-.25 and high>.55 and high-low>1.8, (
            "Finale must rise from underground before visible departure")
        scene.frame_set(frame);bpy.context.view_layer.update()
        target=Vector(wasp.location)
    else:
        target=Vector(roach.location)
    # Roach faces 180 degrees in these chapters: local +Y points toward
    # the negative-world-Y action camera. Never confuse local and world sides.
    # Verify both front-side separation and the actual camera-facing vector.
    if chapter==11:
        assert egg.matrix_world.translation.y < roach.location.y-.20, "Egg on hidden far-side leg"
        camera_side=(camera.location-roach.matrix_world.translation).normalized()
        egg_offset=egg.matrix_world.translation-roach.matrix_world.translation
        assert egg_offset.dot(camera_side)>.20, "Egg occluded from action camera"
    if chapter==12:
        larva_surface=larva.matrix_world @ Vector((-.05,.345,-.050))
        assert larva_surface.y < roach.location.y-.20, "Larva occluded on far side"
        camera_side=(camera.location-roach.matrix_world.translation).normalized()
        assert (larva_surface-roach.matrix_world.translation).dot(camera_side)>.20, "Larva occluded from action camera"
    projected=world_to_camera_view(scene,camera,target)
    print("JW_ACTION_TARGET_PROJECTION",chapter,frame,tuple(round(float(v),3) for v in projected),flush=True)
    assert .07<projected.x<.93 and .08<projected.y<.92 and projected.z>0, "Action focal point outside portrait view"
    assert scene.camera is camera and scene.render.fps==24
    print("JW_V68_STORY_GEOMETRY_PREFLIGHT_PASS",chapter,flush=True)
elif mode=="still":
    scene.frame_set(int(os.getenv("JW_STILL_FRAME","120")))
    scene.render.image_settings.file_format="PNG"
    bpy.ops.render.render(write_still=True)
else:
    if mode=="motion":
        scene.frame_start=int(os.getenv("JW_MOTION_START","108"))
        scene.frame_end=scene.frame_start+23
    scene.render.image_settings.file_format="FFMPEG"
    scene.render.ffmpeg.format="MPEG4"
    scene.render.ffmpeg.codec="H264"
    scene.render.ffmpeg.constant_rate_factor="LOW"
    bpy.ops.render.render(animation=True)
print("JW_V68_STORY_DRAFT_RENDER_DONE",chapter,mode,flush=True)
