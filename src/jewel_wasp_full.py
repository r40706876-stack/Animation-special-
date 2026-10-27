"""Original 140-second Jewel Wasp documentary, 14 independent 10s Blender shots.
Uses shared procedural insect rigs and environment in jewel_wasp_3d.py.
STORY_CHAPTER=0..13 BLENDER_OUTPUT=/path/shot_N.mp4
"""
import os,runpy,pathlib,math
import bpy
from mathutils import Vector
os.environ['JEWEL_SKIP_RENDER']='1'
ns=runpy.run_path(str(pathlib.Path(__file__).with_name('jewel_wasp_v2.py')))
scene=ns['scene'];roach=ns['roach'];wasp=ns['wasp'];cam=ns['cam']
ell=ns['ell'];mat=ns['mat'];aim=ns['aim'];link=ns['link']
chapter=int(os.getenv('STORY_CHAPTER','0'))
assert 0<=chapter<14
scene.frame_start=1;scene.frame_end=240;scene.render.fps=24
scene.render.filepath=os.getenv('BLENDER_OUTPUT','/tmp/jewel_full_%02d.mp4'%chapter)
scene.render.resolution_x=540;scene.render.resolution_y=960;scene.render.resolution_percentage=100
# Eevee CPU rendering: halve default 64 samples while keeping full 540x960 pixels.
# Restores feasibility on free runners; review contact sheet before declaring visual QA.
if hasattr(scene, 'eevee') and hasattr(scene.eevee, 'taa_render_samples'):
 scene.eevee.taa_render_samples=32
print('JEWEL_EEVEE_RENDER_SAMPLES',getattr(scene.eevee,'taa_render_samples','unavailable'),flush=True)
# Preserve reusable joint animations; loop them across the entire chapter.
for ob in bpy.data.objects:
 if ob.parent in (roach,wasp) and ob.animation_data and ob.animation_data.action:
  for curve in ob.animation_data.action.fcurves:
   if not any(m.type=='CYCLES' for m in curve.modifiers):
    curve.modifiers.new('CYCLES')
for ob in (roach,wasp,cam):
 ob.animation_data_clear()
# The three poses of each insect define distinct blocking for each narrative chapter.
# Coordinates are world positions of each rig root; insect details stay parented.
paths=[
 # forage, pursuit, attempted escape
 ([(-.9,.4,.03),(-.25,.1,.03),(.7,.3,.03)],[(-2,-1.9,1.5),(-1.5,-1.4,1.3),(-1.1,-1.1,1.0)]),
 ([(.7,.3,.03),(.1,.2,.03),(-.5,.15,.03)],[(-1.7,-1.4,1.4),(-1,-1.3,.95),(-.4,-1.1,.65)]),
 ([(-.5,.15,.03),(.25,.25,.03),(.5,.15,.03)],[(-.7,-1.6,.8),(-.3,-1.5,.5),(.2,-1.4,.36)]),
 # thoracic sting and recovery
 ([(0,0,.03),(0,0,.02),(0,0,.03)],[(-.5,-1.9,.75),(-.12,-1.45,.32),(0,-1.40,.3)]),
 ([(0,0,.03),(0,-.04,.01),(0,-.04,.03)],[(0,-1.4,.3),(-.4,-1.7,.65),(-.65,-1.9,.75)]),
 # head sting and nerve schematic
 ([(0,0,.03),(0,0,.03),(0,0,.03)],[(-.7,-1.9,.85),(-.2,-1.85,.32),(-.1,-1.75,.32)]),
 ([(0,0,.03),(0,0,.03),(0,0,.03)],[(-.2,-1.75,.35),(-.55,-1.8,.65),(-.8,-1.7,.8)]),
 # behavior, antenna grasp, leading to burrow
 ([(-.6,.2,.03),(-.15,.2,.03),(.35,.2,.03)],[(-1.2,-1.3,.75),(-.8,-1.15,.5),(-.4,-.9,.4)]),
 ([(0,.1,.03),(.05,.15,.03),(.25,.25,.03)],[(-.6,-1.5,.6),(-.25,-1.4,.36),(.15,-1.3,.35)]),
 ([(-.9,-.5,.03),(-.1,.05,.03),(.9,.6,.03)],[(-1.1,-1.6,.35),(-.3,-1.05,.35),(.7,-.5,.35)]),
 # burrow, egg, development and closing lifecycle
 ([(.4,.2,.03),(1,.65,.03),(1.45,1.05,.03)],[(.2,-.9,.35),(.8,-.35,.35),(1.25,.2,.35)]),
 ([(1.3,.9,.03),(1.55,1.12,.03),(1.6,1.2,.03)],[(1.1,.15,.4),(1.5,.45,.35),(1.3,.35,.7)]),
 ([(1.6,1.2,.03),(1.6,1.2,.03),(1.6,1.2,.03)],[(1.4,.5,.7),(1.6,.9,1.2),(2,1.2,1.8)]),
 ([(1.6,1.2,.03),(1.6,1.2,.03),(1.6,1.2,.03)],[(2,1.2,1.8),(1.2,.5,2.2),(-.4,-1.2,2.6)])
]
rpath,wpath=paths[chapter]
for rig,positions in ((roach,rpath),(wasp,wpath)):
 for frame,position in zip((1,120,240),positions):
  rig.location=position;rig.keyframe_insert(data_path='location',frame=frame)
 for frame in (1,60,120,180,240):
  rig.rotation_euler[2]=(.035 if rig==roach else .09)*math.sin(frame*.11+chapter)
  rig.keyframe_insert(data_path='rotation_euler',frame=frame)
# V3 cinematography: use narrative-specific shot scales and subjects instead of
# repeating the same distant two-insect composition for all 14 chapters.
# Preserve the animation paths, frame count and the finished V2 artifact.
shot_distance=[11.2,9.7,8.8,6.9,7.5,6.7,7.5,9.3,7.4,10.6,6.8,6.4,6.2,10.2]
shot_lens=[36,39,42,44,43,46,42,39,44,36,38,43,43,35]
shot_azimuth=[24,34,43,55,22,62,36,45,52,29,60,48,32,18]
cam.data.lens=shot_lens[chapter]
cam.data.sensor_fit='VERTICAL'
def interp(points,frame):
    if frame<=120:
        t=(frame-1)/119
        a,b=points[0],points[1]
    else:
        t=(frame-120)/120
        a,b=points[1],points[2]
    return Vector(a).lerp(Vector(b),max(0,min(1,t)))
for frame in (1,48,96,144,192,240):
    rp=interp(rpath,frame);wp=interp(wpath,frame)
    focus=rp*.56+wp*.44+Vector((0,-.16,.20))
    # Sting: camera favors the wasp's abdomen and the roach's thorax.
    if chapter in (3,5):
        focus=rp*.62+wp*.38+Vector((0,-.25,.33))
    # Neurological explanation: stay near the roach's head.
    elif chapter in (4,6):
        focus=rp*.78+wp*.22+Vector((0,-.50,.38))
    # Antenna grasp: favor the roach's face.
    elif chapter==8:
        focus=rp*.72+wp*.28+Vector((0,-.58,.35))
    # Burrow and egg sequence: make the entrance and developing egg visible.
    elif chapter==10:
        focus=Vector((2.02,1.48,.13))*.80+focus*.20
    elif chapter in (11,12):
        focus=rp*.82+wp*.18+Vector((.25,.20,.42))
    elif chapter==13:
        focus=wp*.70+rp*.30+Vector((0,0,.24))
    az=math.radians(shot_azimuth[chapter])+.065*math.sin(frame/240*math.pi)
    direction=Vector((math.sin(az)*.35,-.52,.98)).normalized() if chapter in (10,11,12) else (Vector((math.sin(az)*.45,-.72,.78)).normalized() if chapter in (3,4,5,6,8) else Vector((math.sin(az)*.55,-.84,.49)).normalized())
    cam.location=focus+direction*shot_distance[chapter]
    aim(cam,focus)
    cam.keyframe_insert(data_path='location',frame=frame)
    cam.keyframe_insert(data_path='rotation_euler',frame=frame)
print('JEWEL_V3_STORY_CAMERA',chapter,shot_distance[chapter],shot_lens[chapter],flush=True)
# A large empty band above the subjects is not useful in a vertical documentary.
# Tracking the actual center also keeps the wasp visible during sting and flight.
# Physically distinct event markers: stinger, neural pathways, burrow, egg and larva.
if chapter in (3,5):
 stinger=ell('sting tip',(0,.87,.32),(.025,.13,.025),ns['black'],wasp)
 for frame,angle in ((1,0),(90,-.20),(150,.18),(240,0)):
  stinger.rotation_euler[0]=angle;stinger.keyframe_insert(data_path='rotation_euler',frame=frame)
if chapter in (4,6):
 nerve=mat('schematic neural signal',(0.02,.86,1.0),.15,.15)
  node_bsdf=nerve.node_tree.nodes.get('Principled BSDF')
  if node_bsdf:
   node_bsdf.inputs['Emission Color'].default_value=(.02,.7,1.0,1)
   node_bsdf.inputs['Emission Strength'].default_value=3.0
 for i in range(4):
  p=ell('schematic nerve node %d'%i,(0,-.55-i*.17,.69),(.11,.11,.075),nerve,roach)
  for frame,scale in ((1,.001),(60,.085),(120,.13),(180,.11),(240,.001)):
   p.scale=(scale,scale,scale*.78);p.keyframe_insert(data_path='scale',frame=frame)
if chapter>=10:
 dark=mat('burrow entrance dark',(.014,.011,.008),0,.98)
 ell('burrow entrance',(2.72,1.75,.055),(.84,.64,.06),dark)
 for i in range(12):
  angle=i*math.tau/12
  ell('burrow edge pebble %d'%i,(2.72+math.cos(angle)*.80,1.75+math.sin(angle)*.60,.10),(.13,.11,.08),ns['soil'])
if chapter in (11,12,13):
 eggmat=mat('ivory egg',(0.88,.78,.52),0,.38)
 egg=ell('wasp egg on cockroach',(.05,.1,.70),(.15,.24,.12),eggmat,roach)
 if chapter==11:
  for frame,size in ((1,.001),(130,.001),(200,1),(240,1)):
   egg.scale=(.15*size,.24*size,.12*size);egg.keyframe_insert(data_path='scale',frame=frame)
 if chapter>=12:
  larva=ell('schematic larva',(.05,.16,.84),(.19,.38,.15),eggmat,roach)
  for frame,size in ((1,.05),(120,.4),(240,1)):
   larva.scale=(.19*size,.38*size,.15*size);larva.keyframe_insert(data_path='scale',frame=frame)
# Visible anatomical cues distinguish sting and antenna-grasp chapters.
if chapter in (3,5,8):
 cue=mat('anatomy cue amber',(1.0,.34,.035),.12,.12)
 cue_bsdf=cue.node_tree.nodes.get('Principled BSDF')
 if cue_bsdf:
  cue_bsdf.inputs['Emission Color'].default_value=(1.0,.26,.01,1)
  cue_bsdf.inputs['Emission Strength'].default_value=2.0
 target_y=-.62 if chapter==3 else (-1.10 if chapter==5 else -1.72)
 bpy.ops.mesh.primitive_torus_add(major_segments=24,minor_segments=8,location=(0,target_y,.73),major_radius=.27 if chapter!=8 else .20,minor_radius=.022)
 target=bpy.context.object
 target.name='visible anatomy target %d'%chapter
 target.parent=roach
 target.data.materials.append(cue)
 for f,s in ((1,.5),(80,1.0),(150,1.18),(240,.75)):
  target.scale=(s,s,s);target.keyframe_insert(data_path='scale',frame=f)
if os.getenv('JEWEL_PREVIEW','0')=='1':
 scene.frame_set(int(os.getenv('JEWEL_PREVIEW_FRAME','120')))
 scene.render.resolution_percentage=70
 if hasattr(scene.eevee,'taa_render_samples'):scene.eevee.taa_render_samples=16
 scene.render.image_settings.file_format='PNG'
 scene.render.filepath=os.getenv('BLENDER_OUTPUT','/tmp/jewel_v2_preview.png')
 print('JEWEL_V2_PREVIEW_READY',chapter,scene.render.filepath,flush=True)
 bpy.ops.render.render(write_still=True)
 print('JEWEL_V2_PREVIEW_DONE',chapter,flush=True)
else:
 scene.render.image_settings.file_format='FFMPEG'
 scene.render.ffmpeg.format='MPEG4';scene.render.ffmpeg.codec='H264'
 print('JEWEL_FULL_CHAPTER_READY',chapter,scene.render.filepath,flush=True)
 bpy.ops.render.render(animation=True)
 print('JEWEL_FULL_CHAPTER_DONE',chapter,flush=True)
