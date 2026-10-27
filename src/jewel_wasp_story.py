"""Six actual Blender 3D animated story chapters, 5s each, reusable insect rigs.
Run with STORY_SHOT=0..5 BLENDER_OUTPUT=... blender -b -t 2 --python src/jewel_wasp_story.py
"""
import os, runpy, pathlib, math
from mathutils import Vector
import bpy
os.environ['JEWEL_SKIP_RENDER']='1'
ns=runpy.run_path(str(pathlib.Path(__file__).with_name('jewel_wasp_3d.py')))
scene=ns['scene']; roach=ns['roach']; wasp=ns['wasp']; cam=ns['cam']
ell=ns['ell']; mat=ns['mat']; aim=ns['aim']; link=ns['link']
shot=int(os.getenv('STORY_SHOT','0'))
assert 0 <= shot <= 5
scene.frame_start=1;scene.frame_end=120;scene.render.fps=24
scene.render.filepath=os.getenv('BLENDER_OUTPUT','/tmp/jewel_wasp_shot_%d.mp4'%shot)
for obj in [roach,wasp,cam]:
 obj.animation_data_clear()
# Distinct narrative actions and camera compositions: not still-image pans.
sequences=[
 # hook: active pursuit across forest floor
 ([(1,(.8,.5,.04)),(60,(.4,.15,.04)),(120,(-.3,.1,.04))],
  [(1,(-1.6,-1.6,1.6)),(60,(-1.1,-1.3,1.1)),(120,(-.5,-1.0,.7))],
  [(1,(3.0,-5,3.0)),(120,(2.1,-3.5,2.1))],(0,-.4,.5)),
 # thoracic sting: wasp lands and moves its abdomen near thorax
 ([(1,(0,0,.03)),(120,(0,0,.03))],
  [(1,(-.6,-1.9,.85)),(65,(-.1,-1.5,.35)),(120,(0,-1.48,.3))],
  [(1,(1.8,-3.3,1.6)),(120,(1.1,-2.5,1.0))],(0,-.7,.4)),
 # mechanism: nerve ganglia and front legs illuminated
 ([(1,(0,0,.04)),(50,(0,-.02,.01)),(120,(0,-.02,.03))],
  [(1,(-1.1,-1.7,.9)),(120,(-.7,-1.4,.8))],
  [(1,(1.5,-3.1,1.4)),(120,(1.0,-2.2,1.1))],(0,-.6,.4)),
 # head sting: targeted second sting, close macro arc
 ([(1,(0,0,.04)),(120,(0,0,.04))],
  [(1,(-.6,-2.1,.9)),(75,(-.2,-1.9,.35)),(120,(-.1,-1.75,.3))],
  [(1,(1.7,-3.3,1.35)),(120,(-1.7,-2.8,1.4))],(0,-1.05,.42)),
 # behavior change: cockroach still walks, slower
 ([(1,(-.7,.2,.03)),(60,(-.2,.2,.04)),(120,(.4,.2,.03))],
  [(1,(-1.6,-1.5,.8)),(60,(-1.2,-1.2,.5)),(120,(-.6,-.8,.4))],
  [(1,(3,-3,2.4)),(120,(1.8,-2.6,1.4))],(0,0,.4)),
 # antenna-led walk to burrow, final cave reveal
 ([(1,(-.9,-.4,.04)),(60,(0,.1,.04)),(120,(1.0,.7,.04))],
  [(1,(-1.1,-1.6,.35)),(60,(-.2,-1.1,.35)),(120,(.8,-.5,.35))],
  [(1,(3,-4,2.7)),(120,(2.8,-2,2.0))],(.4,.3,.3)),
]
rp,wp,cp,target=sequences[shot]
def animate(o,keys):
 for frame,location in keys:
  o.location=location;o.keyframe_insert(data_path='location',frame=frame)
animate(roach,rp);animate(wasp,wp)
for f,loc in cp:
 cam.location=loc;aim(cam,target);cam.keyframe_insert(data_path='location',frame=f);cam.keyframe_insert(data_path='rotation_euler',frame=f)
cam.data.lens=[38,60,68,75,43,40][shot]
# Active body motion; leg geometry is articulated rig hierarchy, parent translates.
for f in [1,30,60,90,120]:
 roach.rotation_euler[2]=.05*math.sin(f*.15) if shot in (0,4,5) else 0
 roach.keyframe_insert(data_path='rotation_euler',frame=f)
 wasp.rotation_euler[2]=.09*math.sin(f*.12)
 wasp.keyframe_insert(data_path='rotation_euler',frame=f)
# Explicit schematic highlights only in nerve mechanism chapters.
if shot in (2,3):
 glow=mat('schematic neural highlight',(1.0,.35,.035),.15,.25)
 for idx,(x,y,z) in enumerate([(0,-.62,.66),(-.08,-.84,.62),(.08,-1.03,.58)]):
  orb=ell('schematic nerve ganglion %d'%idx,(x,y,z),(.10,.11,.10),glow,roach)
  orb.hide_render=False
 for a,b in [((0,-.62,.66),(-.08,-.84,.62)),((-.08,-.84,.62),(.08,-1.03,.58))]:
  link('schematic neural pathway',a,b,.025,glow,roach)
# Burrow landmark only in finale, with a visibly descending camera.
if shot==5:
 dark=mat('burrow cavity',(.009,.008,.006))
 ell('burrow entrance',(1.8,1.3,.07),(.9,.65,.07),dark)
 for i in range(9):
  theta=i*math.pi*2/9
  ell('burrow stone',(1.8+math.cos(theta)*.85,1.3+math.sin(theta)*.64,.12),(.14,.13,.1),ns['soil'])
# Speed-conscious software rendering, consistent real 3D geometry and camera.
scene.render.image_settings.file_format='FFMPEG'
scene.render.ffmpeg.format='MPEG4'
scene.render.ffmpeg.codec='H264'
print('JEWEL_WASP_STORY_CHAPTER_READY',shot,scene.render.filepath,flush=True)
bpy.ops.render.render(animation=True)
print('JEWEL_WASP_STORY_CHAPTER_DONE',shot,flush=True)
