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
assert mode in ("still","motion","draft")
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
    ((.4,-.8,.85),(1.10,-.4,.43),(1.32,-.16,.36),(.55,.2,.18),(.55,.2,.18)),
    ((-1.6,-.7,1.2),(-1.5,-.7,1.2),(-1.5,-.7,1.2),(.65,.15,.18),(.65,.15,.18)),
    ((.6,-.7,.85),(1.20,-.25,.43),(1.38,-.13,.36),(.6,.2,.18),(.6,.2,.18)),
    ((-1.7,-.7,1.1),(-1.7,-.7,1.1),(-1.7,-.7,1.1),(.65,.15,.18),(.65,.15,.18)),
    ((-.9,-.5,.52),(-.5,-.4,.44),(-.2,-.3,.42),(.75,.2,.18),(.3,.25,.18)),
    ((-.8,-.4,.42),(-.5,-.1,.40),(-.2,.15,.42),(.9,.2,.18),(.25,.45,.18)),
    ((-.7,-.5,.52),(.1,.1,.42),(.8,.5,.40),(.75,.0,.18),(1.45,.95,.18)),
    ((.1,-.5,.52),(.7,.2,.43),(1.4,.9,.38),(.8,.1,.18),(1.6,1.1,-.16)),
    ((1.0,.15,.50),(1.4,.6,.40),(1.7,.9,.42),(1.50,1.0,.18),(1.50,1.0,.18)),
    ((-1.6,-1.0,1.2),(-1.6,-1.0,1.2),(-1.6,-1.0,1.2),(1.5,1.0,.18),(1.5,1.0,.18)),
    ((.4,.0,.40),(.3,-.2,.95),(-1.1,-1.0,1.55),(.95,.2,.18),(.95,.2,.18))]
ws,wm,we,rs,re=poses[chapter]
def key_loc(actor,frame,point):
    actor.location=point;actor.keyframe_insert(data_path="location",frame=frame)
for f,p in ((1,ws),(120,wm),(240,we)):key_loc(wasp,f,p)
for f,p in ((1,rs),(120,tuple((a+b)/2 for a,b in zip(rs,re))),(240,re)):
    key_loc(roach,f,p)
wasp.rotation_euler.z=-.10 if chapter<8 else .12
roach.rotation_euler.z=math.pi
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

# Burrow is a dark opening with an uneven soil rim, not a floating black disc.
if chapter in (9,10,11,12):
    holemat=material("burrow interior dark",(.007,.006,.004),rough=.99)
    ell("burrow cavity",(1.60,1.10,-.054),(.65,.49,.012),holemat)
    for i in range(20):
        theta=2*math.pi*i/20
        ell("irregular earth rim",
            (1.6+(.69+.07*math.sin(i*2.1))*math.cos(theta),
             1.1+(.53+.04*math.cos(i*1.9))*math.sin(theta),-.035),
            (.085,.075,.045),soil,segments=12,rings=8)

# Needle tip travels toward the intended thoracic/head region; visual proof
# still needed to establish contact, no numerical geometry claim here.
if chapter in (3,5):
    bpy.ops.mesh.primitive_cone_add(vertices=12,radius1=.022,radius2=.001,depth=1)
    needle=bpy.context.object;needle.name="DRAFT visible articulated sting"
    needle.data.materials.append(leg_amber)
    for frame,reach in ((1,.01),(70,.01),(100,.40),(135,1.0),(160,1.0),
                        (185,.30),(240,.01)):
        scene.frame_set(frame);bpy.context.view_layer.update()
        start=wasp.matrix_world @ Vector((-.80,0,.04))
        target=roach.matrix_world @ Vector((.27 if chapter==3 else .56,0,.11))
        delta=target-start
        # Cap needle length; if actors are far apart it must not bridge a gap.
        distance=min(delta.length,.24)*reach
        direction=delta.normalized() if delta.length>.001 else Vector((1,0,0))
        needle.location=start+direction*distance*.5
        needle.rotation_euler=direction.to_track_quat("Z","Y").to_euler()
        needle.scale=(1,1,max(.002,distance))
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
    eggmat=material("egg ivory",(.76,.70,.49),rough=.78)
    # Egg attaches near a cockroach leg, not as a white bead on its dorsal shell.
    egg=ell("single jewel wasp egg",(.18,.30,-.08),(.075,.13,.055),eggmat,roach)
    for f,s in ((1,.001),(110,.001),(170,.65),(240,1.0)):
        egg.scale=(.075*s,.13*s,.055*s);egg.keyframe_insert(data_path="scale",frame=f)
if chapter==12:
    # One continuous tapered larval cuticle, not eight detached pearl spheres.
    # Shallow annular material changes are painted on the same watertight mesh.
    larvamat=material("organic cream larval cuticle",(.65,.54,.38),rough=.82,noise=18)
    groove=material("subtle larval segment grooves",(.48,.39,.29),rough=.91,noise=14)
    verts=[];faces=[];nring=49;nsides=20
    for i in range(nring):
        t=i/(nring-1)
        profile=max(.045,math.sin(math.pi*t)**.62)
        x=-.46+.82*t
        yc=.30+.020*math.sin(2*math.pi*t)
        zc=.10+.012*math.sin(math.pi*t)
        for j in range(nsides):
            a=2*math.pi*j/nsides
            verts.append((x,yc+.095*profile*math.cos(a),
                          zc+.076*profile*math.sin(a)))
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
    for poly in larva_mesh.polygons:
        poly.use_smooth=True
        axial=poly.index//nsides
        poly.material_index=1 if axial<nring-1 and axial%6==0 else 0
    for frame,size,sway in ((1,.25,0),(60,.40,.025),(120,.62,-.020),
                            (180,.83,.028),(240,1.0,0)):
        larva.scale=(size,size,size)
        larva.rotation_euler.z=sway
        larva.keyframe_insert(data_path="scale",frame=frame)
        larva.keyframe_insert(data_path="rotation_euler",frame=frame)
# Independent shot compositions, focal points and lens moves.
camera.animation_data_clear();camera_data.animation_data_clear()
camera_data.type="ORTHO"
shot_sizes=[5.8,4.4,4.2,3.15,2.9,2.9,2.7,4.0,3.7,5.2,4.6,1.75,1.75,5.5]
offsets=[
    (1.0,-5.2,3.4),(-2.0,-4.4,2.5),(2.1,-4.2,2.7),
    (1.7,-3.2,1.9),(-.9,-3.3,2.3),(-1.6,-2.8,1.7),
    (2.0,-3.0,2.3),(-2.0,-4.0,2.3),(1.5,-3.5,1.9),
    (1.0,-5.3,3.5),(-2.2,-4.0,2.8),(1.8,-2.8,1.0),
    (1.1,-2.4,1.0),(-1.2,-5.0,3.4)]
for f in (1,120,240):
    scene.frame_set(f)
    focus=(Vector(wasp.location)+Vector(roach.location))*.5
    if chapter in (4,6,12):focus=Vector(roach.location)
    if chapter in (9,10):focus=Vector((1.3,.80,.30))
    if chapter in (11,12):
        # Macro cutaway-style view: frame the near-side leg, egg and larva.
        focus=Vector(roach.location)+Vector((0,-.18,.05))
    focus.z+=.12
    off=Vector(offsets[chapter])
    camera.location=focus+off*(1.05 if f==1 else .94 if f==240 else 1.0)
    camera.rotation_euler=(focus-camera.location).to_track_quat("-Z","Y").to_euler()
    camera_data.ortho_scale=shot_sizes[chapter]*(1.08 if f==1 else .97 if f==240 else 1)
    camera.keyframe_insert(data_path="location",frame=f)
    camera.keyframe_insert(data_path="rotation_euler",frame=f)
    camera_data.keyframe_insert(data_path="ortho_scale",frame=f)

scene.render.engine="BLENDER_EEVEE_NEXT"
scene.render.resolution_x=270;scene.render.resolution_y=480
scene.render.resolution_percentage=int(os.getenv("JW_RES_PERCENT","60"))
scene.render.image_settings.color_mode="RGB"
scene.render.filepath=os.environ["BLENDER_OUTPUT"]
if mode=="still":
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
