"""First reference: procedural 3D jewel-wasp and cockroach motion proof.
Run: blender -b -t 2 --python src/jewel_wasp_3d.py
No external models or paid APIs. This is a motion proof, not the final documentary.
"""
import bpy, math, os
from mathutils import Vector
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
scene=bpy.context.scene
scene.render.engine='BLENDER_EEVEE_NEXT' if bpy.app.version >= (4,2,0) else 'BLENDER_EEVEE'
scene.render.resolution_x=540;scene.render.resolution_y=960;scene.render.resolution_percentage=100
scene.render.fps=24;scene.frame_start=1;scene.frame_end=96
scene.render.image_settings.file_format='FFMPEG' if False else 'PNG'
scene.render.filepath=os.getenv('BLENDER_OUTPUT','/tmp/JEWEL_WASP_3D_PROOF.mp4')
scene.render.image_settings.color_mode='RGB'
scene.render.ffmpeg.format='MPEG4';scene.render.ffmpeg.codec='H264';scene.render.ffmpeg.constant_rate_factor='MEDIUM'
scene.render.file_extension=True
def mat(name,color,metal=0,rough=.55):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True
 p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough
 return m
soil=mat('forest floor',(0.13,.095,.06));roachmat=mat('roach chestnut',(.25,.085,.025),.18);wingmat=mat('roach wing covers',(.38,.16,.055),.1)
green=mat('jewel wasp iridescent emerald',(.012,.47,.24),.72,.19);blue=mat('wasp blue thorax',(.012,.22,.42),.65)
trans=mat('wing pale cyan',(.33,.72,.78),.1);black=mat('eye black',(.009,.012,.015));leaf=mat('leaf green',(.13,.25,.055))
def ell(name,loc,scale,material,parent=None):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=16,ring_count=8,location=loc);o=bpy.context.object;o.name=name;o.scale=scale;o.data.materials.append(material)
 if parent:o.parent=parent
 return o
def link(name,a,b,r,material,parent):
 a,b=Vector(a),Vector(b);d=b-a
 bpy.ops.mesh.primitive_cylinder_add(vertices=8,radius=r,depth=d.length,location=(a+b)/2)
 o=bpy.context.object;o.name=name;o.rotation_euler=d.to_track_quat('Z','Y').to_euler();o.data.materials.append(material);o.parent=parent
 return o
bpy.ops.mesh.primitive_plane_add(size=200);bpy.context.object.name='forest floor';bpy.context.object.data.materials.append(soil)
for i in range(14):
 x=-4+(i%7)*1.3;y=-3+(i//7)*5
 ell('leaf litter', (x,y,.04),(.45,.17,.03),leaf)
def root(name):
 o=bpy.data.objects.new(name,None);scene.collection.objects.link(o);return o
roach=root('RIG cockroach')
ell('cockroach abdomen',(0,0,.39),(.43,.8,.28),roachmat,roach)
ell('cockroach thorax',(0,-.63,.4),(.38,.35,.22),wingmat,roach)
ell('cockroach head',(0,-.98,.36),(.29,.23,.2),roachmat,roach)
for side in [-1,1]:
 ell('cockroach eye',(.22*side,-1.02,.43),(.075,.09,.085),black,roach)
 for i in range(3):
  y=-.58+i*.42
  link('cockroach leg upper',(side*.3,y,.33),(side*.62,y+.10,.2),.035,roachmat,roach)
  link('cockroach leg lower',(side*.62,y+.10,.2),(side*.82,y+.2,.045),.022,wingmat,roach)
 link('cockroach antenna',(side*.11,-1.15,.41),(side*.55,-2.05,.55),.012,black,roach)
wasp=root('RIG jewel wasp')
ell('wasp abdomen',(0,.45,.35),(.19,.43,.19),green,wasp)
ell('wasp thorax',(0,-.1,.38),(.24,.26,.23),blue,wasp)
ell('wasp head',(0,-.47,.4),(.2,.19,.19),green,wasp)
for side in [-1,1]:
 ell('wasp eye',(.16*side,-.49,.45),(.055,.07,.07),black,wasp)
 for i in range(3):
  y=-.28+i*.29
  link('wasp leg',(side*.16,y,.3),(side*.43,y+.12,.06),.018,black,wasp)
 wing=ell('animated wasp wing',(side*.35,-.02,.57),(.45,.14,.018),trans,wasp)
 wing.rotation_euler[1]=side*.24
 for f in [1,7,13,19,25,31,37,43,49,55,61,67,73,79,85,91,96]:
  wing.rotation_euler[1]=side*(.2 if f%12<6 else .85);wing.keyframe_insert(data_path='rotation_euler',frame=f)
for f in [1,25,49,73,96]:
 t=(f-1)/95
 roach.location=(-.5+1.5*t,0,.02+abs(math.sin(t*math.pi*8))*.035)
 roach.rotation_euler[2]=math.sin(t*math.pi*5)*.08
 roach.keyframe_insert(data_path='location',frame=f);roach.keyframe_insert(data_path='rotation_euler',frame=f)
 wasp.location=(-1.6+1.9*t,-1.6+.8*t,1.4+.22*math.sin(t*math.pi*3))
 wasp.rotation_euler[2]=-.2+.18*math.sin(t*math.pi*2)
 wasp.keyframe_insert(data_path='location',frame=f);wasp.keyframe_insert(data_path='rotation_euler',frame=f)
def aim(obj,point):obj.rotation_euler=(Vector(point)-obj.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(3,-5,3.3));cam=bpy.context.object;aim(cam,(0,-.25,.5));scene.camera=cam;cam.data.type='PERSP';cam.data.lens=38
for f,loc in [(1,(3,-5,3.3)),(49,(2.4,-4,2.5)),(96,(1.8,-3.2,1.9))]:
 cam.location=loc;aim(cam,(0,-.25,.5));cam.keyframe_insert(data_path='location',frame=f);cam.keyframe_insert(data_path='rotation_euler',frame=f)
world=bpy.data.worlds.new('Forest ambient');scene.world=world;world.use_nodes=True;world.node_tree.nodes['Background'].inputs['Color'].default_value=(.25,.31,.22,1)
bpy.ops.object.light_add(type='AREA',location=(0,-2,5));bpy.context.object.data.energy=850;bpy.context.object.data.shape='DISK';bpy.context.object.data.size=5
scene.render.film_transparent=False
scene.render.image_settings.file_format='FFMPEG'
print('JEWEL_WASP_3D_SCENE_READY',scene.frame_end,scene.render.filepath)
bpy.ops.render.render(animation=True)
print('JEWEL_WASP_3D_RENDER_DONE')
