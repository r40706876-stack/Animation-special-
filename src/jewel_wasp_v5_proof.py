"""V5 visual-quality experiment; proof stills only until human visual QA.
Uses the existing V4 story and camera blocking, then adds material/forest refinement.
Does not alter the verified V4 140-second MP4.
"""
import os, math, pathlib, random
import bpy
from mathutils import Vector

v4=pathlib.Path(__file__).with_name("jewel_wasp_v4_proof.py")
src=v4.read_text()
marker='out=os.getenv("BLENDER_OUTPUT"'
assert src.count(marker)==1, "V4 proof boundary changed"
ctx={"__name__":"__main__","__file__":str(v4)}
exec(compile(src.split(marker)[0],str(v4),"exec"),ctx)
scene=ctx["scene"];cam=ctx["cam"];chapter=ctx["chapter"]
mat=ctx["mat"];ell=ctx["ell"];link=ctx["link"];aim=ctx["aim"]
roach=ctx["roach"];wasp=ctx["wasp"]

# Replace lollipop-style background trees and oversized ground leaves.
for obj in bpy.data.objects:
 if obj.name.startswith(("V4 forest trunk","V4 layered forest foliage","leaf litter")):
  obj.hide_render=True

# Subtle mottled organic surfaces, rather than solid-colored toy plastic.
for name,scale,strength,distance,roughness in [
 ("roach chestnut",23,.24,.026,.43),
 ("roach wing covers",39,.17,.014,.34),
 ("V4 dark bronze carapace",45,.20,.010,.39),
 ("V4 warm carapace highlights",55,.14,.009,.35),
 ("jewel wasp iridescent emerald",60,.10,.008,.24),
 ("wasp blue thorax",52,.12,.010,.30),
 ("forest floor",17,.30,.05,.90)]:
 material=bpy.data.materials.get(name)
 if not material or not material.use_nodes:continue
 nodes=material.node_tree.nodes;links=material.node_tree.links
 bsdf=nodes.get("Principled BSDF")
 if not bsdf:continue
 bsdf.inputs["Roughness"].default_value=roughness
 noise=nodes.new("ShaderNodeTexNoise");noise.inputs["Scale"].default_value=scale
 bump=nodes.new("ShaderNodeBump");bump.inputs["Strength"].default_value=strength
 bump.inputs["Distance"].default_value=distance
 links.new(noise.outputs["Fac"],bump.inputs["Height"])
 links.new(bump.outputs["Normal"],bsdf.inputs["Normal"])

wing=bpy.data.materials.get("wing pale cyan")
if wing and wing.use_nodes:
 p=wing.node_tree.nodes.get("Principled BSDF")
 p.inputs["Base Color"].default_value=(.18,.46,.42,1)
 p.inputs["Roughness"].default_value=.28
 p.inputs["Alpha"].default_value=.52
 if "Transmission Weight" in p.inputs:
  p.inputs["Transmission Weight"].default_value=.45
 if hasattr(wing,"surface_render_method"):
  wing.surface_render_method="DITHERED"

# Narrow distant tree trunks, leaf clusters and organic fern undergrowth.
random.seed(164+chapter)
bark=mat("V5 bark",(.065,.048,.033),0,.92)
foliage=mat("V5 canopy",(.025,.075,.038),0,.91)
fern=mat("V5 leaf",(.08,.16,.055),0,.84)
fern2=mat("V5 leaf shadow",(.04,.11,.045),0,.87)
for i in range(24):
 side=-1 if i%2 else 1
 x=side*(3.5+(i%6)*.82)
 y=-1.8+(i//2)*.92
 height=2.9+(i%5)*.44
 bpy.ops.mesh.primitive_cone_add(vertices=11,radius1=.18,radius2=.065,depth=height,location=(x,y,height/2))
 ob=bpy.context.object;ob.name="V5 tapered forest trunk";ob.data.materials.append(bark)
 for k in range(4):
  z=height*(.62+k*.085)
  link("V5 thin branch",(x,y,z),(x+side*(.42+k*.10),y+.14,z+.32),.027,bark,None)
  for j in range(4):
   leaf=ell("V5 irregular canopy",(x+side*(.33+j*.16),y+.12*j,z+.30),(.22,.11,.07),foliage)
   leaf.rotation_euler[1]=.3*side
for i in range(60):
 side=-1 if i%2 else 1
 x=side*(1.8+(i%7)*.38)
 y=-3.0+(i//2)*.24
 h=.20+.09*(i%4)
 link("V5 fern stalk",(x,y,.035),(x,y,.035+h),.009,fern2,None)
 for j in range(4):
  z=.10+j*h/5
  for sign in (-1,1):
   leaf=ell("V5 narrow fern leaf",(x+sign*(.08+j*.018),y+.03*j,z),(.13,.033,.009),fern if j%2 else fern2)
   leaf.rotation_euler[2]=sign*.23

# Anatomical leg spikes and wing veins to improve silhouette at close range.
dark=mat("V5 dark leg spines",(.045,.026,.015),.05,.78)
for side in (-1,1):
 for i in range(3):
  y=-.55+i*.42
  for j in range(3):
   base=(side*(.56+j*.075),y+.09+j*.03,.20-j*.042)
   tip=(side*(.60+j*.08),y+.14+j*.025,.28-j*.044)
   link("V5 cockroach tibia spines",base,tip,.008,dark,roach)
 for i in range(3):
  link("V5 wasp wing veins",(side*(.18+i*.10),-.02,.59),(side*(.52+i*.12),.10,.60),.006,dark,wasp)

# Burrow, egg and larva are critical story beats: increase their screen presence.
if chapter in (10,11,12,13):
 position,target,lens=ctx["camera_specs"][chapter]
 cam.animation_data_clear()
 for frame,dolly in ((1,1.18),(120,1.08),(240,1.03)):
  cam.location=Vector(target)+(Vector(position)-Vector(target))*dolly
  aim(cam,target)
  cam.keyframe_insert(data_path="location",frame=frame)
  cam.keyframe_insert(data_path="rotation_euler",frame=frame)
 cam.data.lens=28

# Natural contrast, without sacrificing insect visibility.
world=scene.world
if world and world.use_nodes:
 world.node_tree.nodes["Background"].inputs["Color"].default_value=(.075,.11,.075,1)
bpy.ops.object.light_add(type="AREA",location=(2.0,1.0,3.6))
bpy.context.object.data.energy=310
bpy.context.object.data.size=3.2

scene.render.image_settings.file_format="PNG"
scene.render.filepath=os.getenv("BLENDER_OUTPUT","/tmp/jewel_v5_proof.png")
scene.frame_set(int(os.getenv("PROOF_FRAME","120")))
print("JEWEL_V5_PROOF_FRAME",chapter,scene.frame_current,flush=True)
bpy.ops.render.render(write_still=True)
print("JEWEL_V5_RENDER_DONE",chapter,flush=True)
