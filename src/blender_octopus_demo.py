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
  emission_color=bs.inputs.get('Emission Color') or bs.inputs.get('Emission')
  if emission_color: emission_color.default_value=(*color,1)
  emission_strength=bs.inputs.get('Emission Strength')
  if emission_strength: emission_strength.default_value=emission
 return m
skin=mat('Living octopus skin',(.62,.19,.14),.24)
nerve=mat('Animated neural signal',(.08,.8,.94),.15,2.0)
sucker=mat('Sucker rings',(.89,.52,.35))
floor=mat('Ocean background',(.015,.07,.13))
def uv(name,loc,scale,material):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=24,ring_count=16,location=loc)
 o=bpy.context.object;o.name=name;o.scale=scale;o.data.materials.append(material)
 bpy.ops.object.shade_smooth();return o
# Continuous tapered tentacles built as one skinned tube per arm.
# Animate each ring of vertices with shape keys, avoiding disconnected spheres.
head=uv('Octopus mantle',(0,0,1.45),(.72,.62,.86),skin)
face=mat('Eye white',(.96,.94,.82))
pupil=mat('Pupils',(.012,.025,.045))
for x in [-.32,.32]:
 uv('Eye white',(x,-.53,1.35),(.24,.15,.27),face)
 uv('Pupil',(x,-.665,1.33),(.115,.065,.15),pupil)
 uv('Eye glint',(x-.045,-.727,1.41),(.035,.022,.045),face)
# All arm vertices are continuous rings, with smoothly decreasing radii.
for k in range(8):
 theta=math.tau*k/8
 verts=[];faces=[]
 rings=26; sides=10
 for j in range(rings):
  t=j/(rings-1)
  distance=.43+1.85*t
  angle=theta+.20*math.sin(t*math.pi*1.5+k)
  center=Vector((distance*math.cos(angle),distance*math.sin(angle),.58+.26*math.sin(math.pi*t)+.30*t*t))
  radius=.245*(1-t)**1.15+.018
  for q in range(sides):
   a=math.tau*q/sides
   verts.append(tuple(center+Vector((radius*math.cos(a)*math.cos(angle),radius*math.cos(a)*math.sin(angle),radius*math.sin(a)))))
 for j in range(rings-1):
  for q in range(sides):
   a=j*sides+q;b=j*sides+(q+1)%sides
   faces.append((a,b,b+sides,a+sides))
 faces.append(tuple(reversed(range(sides))))
 faces.append(tuple((rings-1)*sides+q for q in range(sides)))
 mesh=bpy.data.meshes.new('Tentacle mesh');mesh.from_pydata(verts,[],faces);mesh.update()
 obj=bpy.data.objects.new('Smooth tentacle '+str(k),mesh);bpy.context.collection.objects.link(obj)
 obj.data.materials.append(skin)
 for poly in mesh.polygons: poly.use_smooth=True
 basis=obj.shape_key_add(name='Rest')
 for index,frame in enumerate([1,31,61,91,120]):
  key=obj.shape_key_add(name='Swim '+str(frame))
  phase=math.tau*(frame-1)/119
  for j in range(rings):
   t=j/(rings-1)
   shift=.38*t*t*math.sin(phase+k*.8+t*4)
   rise=.29*t*t*math.cos(phase+k*.9+t*5)
   for q in range(sides):
    n=j*sides+q
    key.data[n].co=Vector(verts[n])+Vector((-math.sin(theta)*shift,math.cos(theta)*shift,rise))
  key.value=0
  for f in [1,31,61,91,120]:
   key.value=1 if f==frame else 0
   key.keyframe_insert(data_path='value',frame=f)
# Ground and underwater context
uv('Sea floor',(0,0,-.55),(9,9,.16),floor)
for i in range(22):
 a=i*2.39996
 r=2.4+(i%5)*.46
 bubble=uv('Bubble '+str(i),(r*math.cos(a),r*math.sin(a),.4+(i%9)*.29),(.035,.035,.055),nerve)
 start=bubble.location.copy()
 for frame in (1,60,120):
  bubble.location=start+Vector((.09*math.sin(frame*.045+i),0,.65*(frame-1)/119))
  bubble.keyframe_insert(data_path='location',frame=frame)
bpy.ops.object.light_add(type='AREA',location=(1,-4,7))
bpy.context.object.data.energy=1400;bpy.context.object.data.shape='DISK';bpy.context.object.data.size=7
bpy.ops.object.camera_add(location=(0,-8,6))
cam=bpy.context.object;direction=Vector((0,0,.7))-cam.location
cam.rotation_euler=direction.to_track_quat('-Z','Y').to_euler()
cam.data.type='ORTHO';cam.data.ortho_scale=9.4
scene.camera=cam
for frame,ang in [(1,-.12),(60,.10),(120,-.12)]:
 cam.rotation_euler[2]=ang
 cam.keyframe_insert(data_path='rotation_euler',frame=frame)
scene.render.film_transparent=False
bpy.ops.render.render(animation=True)
print('BLENDER_3D_RENDER_COMPLETE',scene.render.filepath)
