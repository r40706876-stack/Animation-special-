"""Keyless procedural 3D octopus neural-system demo; Blender background mode."""
import bpy, math, os
from mathutils import Vector
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
scene=bpy.context.scene
# Use Eevee instead of Cycles: Ubuntu's packaged Cycles build can lack
# OpenImageDenoiser and fail at render time even when the scene loads.
try:
    scene.render.engine='BLENDER_EEVEE'
except TypeError:
    scene.render.engine='BLENDER_EEVEE_NEXT'
if hasattr(scene,'eevee') and hasattr(scene.eevee,'taa_render_samples'):
    scene.eevee.taa_render_samples=16
print('RENDER_ENGINE',scene.render.engine)
scene.render.resolution_x=540
scene.render.resolution_y=960
scene.render.resolution_percentage=100
scene.render.fps=24
scene.frame_start=1
scene.frame_end=120
scene.render.image_settings.file_format='FFMPEG'
scene.render.ffmpeg.format='MPEG4'
scene.render.ffmpeg.codec='H264'
scene.render.filepath=os.environ.get('BLENDER_OUTPUT','/tmp/octopus_3d_demo.mp4')
scene.world.color=(0.025,0.045,0.085)
def mat(name,color,metal=0,emission=0):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True
 bs=m.node_tree.nodes.get('Principled BSDF')
 bs.inputs['Base Color'].default_value=(*color,1)
 bs.inputs['Metallic'].default_value=metal
 bs.inputs['Roughness'].default_value=.36
 if emission:
  bs.inputs['Emission Color'].default_value=(*color,1)
  bs.inputs['Emission Strength'].default_value=emission
 return m
skin=mat('Living octopus skin',(.62,.19,.14),.24)
nerve=mat('Animated neural signal',(.08,.8,.94),.15,2.0)
sucker=mat('Sucker rings',(.89,.52,.35))
floor=mat('Ocean background',(.015,.07,.13))
def uv(name,loc,scale,material):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=24,ring_count=16,location=loc)
 o=bpy.context.object;o.name=name;o.scale=scale;o.data.materials.append(material)
 bpy.ops.object.shade_smooth();return o
head=uv('Octopus mantle', (0,0,1.0),(.8,.7,.95),skin)
eyes=[]
for x in [-.45,.45]:
 eye=uv('Eye', (x,-.57,.82),(.14,.12,.14),nerve);eyes.append(eye)
arms=[]
for k in range(8):
 theta=k*math.tau/8
 parent=bpy.data.objects.new('Arm control '+str(k),None)
 bpy.context.collection.objects.link(parent);parent.location=(0,0,.35)
 for j in range(8):
  t=(j+.5)/8
  radius=1.15+2.4*t
  x=radius*math.cos(theta);y=radius*math.sin(theta)
  z=.32+.35*math.sin(t*math.pi)
  seg=uv('Arm %d segment %d'%(k,j),(x,y,z),(.27*(1-t)+.055,.27*(1-t)+.055,.18*(1-t)+.05),skin)
  seg.parent=parent
  seg.matrix_parent_inverse=parent.matrix_world.inverted()
  if j%2==0:
   uv('Sucker %d %d'%(k,j),(x,y,z-.17),(.11,.11,.045),sucker)
 arms.append(parent)
 for frame in [1,31,61,91,120]:
  parent.rotation_euler[2]=.09*math.sin(frame*.065+k)
  parent.rotation_euler[0]=.08*math.sin(frame*.07+k)
  parent.keyframe_insert(data_path='rotation_euler',frame=frame)
for k in range(8):
 theta=k*math.tau/8
 for j in range(6):
  t=j/5
  pulse=uv('Neural impulse %d-%d'%(k,j),((1.15+2.35*t)*math.cos(theta),(1.15+2.35*t)*math.sin(theta),.65),(.09,.09,.09),nerve)
  pulse.hide_render=True;pulse.keyframe_insert(data_path='hide_render',frame=1)
  for frame in range(1,121,20):
   on=((frame//20+k+j)%3==0)
   pulse.hide_render=not on;pulse.keyframe_insert(data_path='hide_render',frame=frame)
bpy.ops.object.light_add(type='AREA',location=(1,-4,7))
bpy.context.object.data.energy=1400;bpy.context.object.data.shape='DISK';bpy.context.object.data.size=7
bpy.ops.object.camera_add(location=(0,-8,6))
cam=bpy.context.object;direction=Vector((0,0,.7))-cam.location
cam.rotation_euler=direction.to_track_quat('-Z','Y').to_euler()
cam.data.type='ORTHO';cam.data.ortho_scale=8.5
scene.camera=cam
for frame,ang in [(1,-.12),(60,.10),(120,-.12)]:
 cam.rotation_euler[2]=ang
 cam.keyframe_insert(data_path='rotation_euler',frame=frame)
scene.render.film_transparent=False
bpy.ops.render.render(animation=True)
print('BLENDER_3D_RENDER_COMPLETE',scene.render.filepath)
