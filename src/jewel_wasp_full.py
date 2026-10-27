"""Original 140-second Jewel Wasp documentary, 14 independent 10s Blender shots.
Uses shared procedural insect rigs and environment in jewel_wasp_3d.py.
STORY_CHAPTER=0..13 BLENDER_OUTPUT=/path/shot_N.mp4
"""
import os,runpy,pathlib,math
import bpy
from mathutils import Vector
os.environ['JEWEL_SKIP_RENDER']='1'
ns=runpy.run_path(str(pathlib.Path(__file__).with_name('jewel_wasp_3d.py')))
scene=ns['scene'];roach=ns['roach'];wasp=ns['wasp'];cam=ns['cam']
ell=ns['ell'];mat=ns['mat'];aim=ns['aim'];link=ns['link']
chapter=int(os.getenv('STORY_CHAPTER','0'))
assert 0<=chapter<14
scene.frame_start=1;scene.frame_end=240;scene.render.fps=24
scene.render.filepath=os.getenv('BLENDER_OUTPUT','/tmp/jewel_full_%02d.mp4'%chapter)
scene.render.resolution_x=540;scene.render.resolution_y=960;scene.render.resolution_percentage=100
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
# A wide/medium/macro camera grammar with visible subjects and changing angles.
wide=chapter in (0,1,2,7,9,10,13)
if chapter>=10:
 target=(1.1,.65,.38)
elif chapter in (3,4,5,6,8):
 target=(0,-.65,.42)
else:
 target=(0,-.2,.48)
camera_paths=[
 ((3.7,-5.7,3.0),(3.2,-5.0,2.8),(2.8,-4.7,2.6)),
 ((-3.7,-5.2,3.0),(-3.1,-4.6,2.4),(-2.8,-4.1,2.3)),
 ((3.1,-4.8,2.6),(2.7,-4.3,2.1),(2.4,-4.0,2.0)),
 ((2.2,-3.5,1.7),(1.9,-3.2,1.5),(2.0,-3.1,1.6)),
 ((-2.6,-3.6,1.9),(-2.2,-3.2,1.6),(-2.0,-3.0,1.6)),
 ((2.4,-3.8,1.9),(2.0,-3.2,1.6),(-1.9,-3.2,1.7)),
 ((-2.2,-3.3,1.8),(-1.9,-3.1,1.6),(2.1,-3.5,1.8)),
 ((3.5,-5.2,3.0),(3.2,-4.8,2.7),(2.8,-4.4,2.5)),
 ((-2.7,-4.0,2.0),(-2.3,-3.7,1.8),(-2.1,-3.4,1.7)),
 ((3.8,-5.4,3.1),(3.4,-4.9,2.7),(3.0,-4.5,2.5)),
 ((3.8,-4.8,3.0),(3.4,-4.4,2.7),(3.0,-4.0,2.4)),
 ((2.8,-3.9,2.1),(2.5,-3.5,1.8),(2.3,-3.2,1.6)),
 ((-2.6,-3.7,2.0),(-2.4,-3.5,1.9),(-2.1,-3.3,1.8)),
 ((4.1,-5.8,3.5),(4.6,-6.4,4.0),(5.0,-7.0,4.5)),
]
for frame,position in zip((1,120,240),camera_paths[chapter]):
 cam.location=position;aim(cam,target)
 cam.keyframe_insert(data_path='location',frame=frame)
 cam.keyframe_insert(data_path='rotation_euler',frame=frame)
cam.data.lens=32 if wide else 38
cam.data.sensor_fit='VERTICAL'
# Physically distinct event markers: stinger, neural pathways, burrow, egg and larva.
if chapter in (3,5):
 stinger=ell('sting tip',(0,.87,.32),(.025,.13,.025),ns['black'],wasp)
 for frame,angle in ((1,0),(90,-.20),(150,.18),(240,0)):
  stinger.rotation_euler[0]=angle;stinger.keyframe_insert(data_path='rotation_euler',frame=frame)
if chapter in (4,6):
 nerve=mat('schematic neural signal',(1,.31,.025),.08,.22)
 for i in range(4):
  p=ell('schematic nerve node %d'%i,(0,-.55-i*.17,.58),(.055,.055,.045),nerve,roach)
  for frame,scale in ((1,.001),(60,.055),(120,.065),(180,.055),(240,.001)):
   p.scale=(scale,scale,scale*.82);p.keyframe_insert(data_path='scale',frame=frame)
if chapter>=10:
 dark=mat('burrow entrance dark',(.014,.011,.008),0,.98)
 ell('burrow entrance',(1.9,1.5,.055),(.95,.75,.06),dark)
 for i in range(12):
  angle=i*math.tau/12
  ell('burrow edge pebble %d'%i,(1.9+math.cos(angle)*.89,1.5+math.sin(angle)*.68,.10),(.13,.11,.08),ns['soil'])
if chapter in (11,12,13):
 eggmat=mat('ivory egg',(0.88,.78,.52),0,.38)
 egg=ell('wasp egg on cockroach',(.05,.1,.69),(.075,.13,.065),eggmat,roach)
 if chapter==11:
  for frame,size in ((1,.001),(130,.001),(200,1),(240,1)):
   egg.scale=(.075*size,.13*size,.065*size);egg.keyframe_insert(data_path='scale',frame=frame)
 if chapter>=12:
  larva=ell('schematic larva',(.05,.16,.78),(.12,.28,.11),eggmat,roach)
  for frame,size in ((1,.05),(120,.4),(240,1)):
   larva.scale=(.12*size,.28*size,.11*size);larva.keyframe_insert(data_path='scale',frame=frame)
scene.render.image_settings.file_format='FFMPEG'
scene.render.ffmpeg.format='MPEG4';scene.render.ffmpeg.codec='H264'
print('JEWEL_FULL_CHAPTER_READY',chapter,scene.render.filepath,flush=True)
bpy.ops.render.render(animation=True)
print('JEWEL_FULL_CHAPTER_DONE',chapter,flush=True)
