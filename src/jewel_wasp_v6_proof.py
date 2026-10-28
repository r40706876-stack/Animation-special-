"""V6 one-pass cinematic proof: anatomy, forest, action cameras and motion.
Build on the verified V5 setup, but do not run its final still render.
Default 14-scene still proof; V6_MOTION=1 renders 48 animated frames.
This is a visual prototype, not an approved final 140-second film.
"""
import os, math, random, pathlib
import bpy
from mathutils import Vector
source=pathlib.Path(__file__).with_name("jewel_wasp_v5_proof.py")
code=source.read_text()
boundary='scene.render.image_settings.file_format="PNG"'
assert code.count(boundary)==1, "V5 setup boundary changed"
ctx={"__name__":"__main__","__file__":str(source)}
exec(compile(code.split(boundary)[0],str(source),"exec"),ctx)
scene,cam,chapter=ctx["scene"],ctx["cam"],ctx["chapter"]
roach,wasp=ctx["roach"],ctx["wasp"]
ell,link,mat,aim=ctx["ell"],ctx["link"],ctx["mat"],ctx["aim"]
rng=random.Random(601+chapter)
# Anatomy: replace conspicuous spherical eyes with small dark compound-eye clusters.
for obj in bpy.data.objects:
 if obj.name in ("cockroach eye","wasp eye"):
  obj.scale=tuple(v*.55 for v in obj.scale)
 if obj.name=="cockroach abdomen":
  obj.scale=(.41,.88,.24)
 if obj.name=="cockroach head":
  obj.scale=(.26,.21,.16)
 if obj.name=="wasp head":
  obj.scale=(.165,.17,.16)
 if obj.name=="wasp thorax":
  obj.scale=(.22,.28,.18)
 if obj.name=="animated wasp wing":
  obj.scale=(.43,.105,.009)
 if obj.name in ("V5 narrow fern leaf","V5 irregular canopy"):
  obj.hide_render=True

# Deep, natural pigment variation: noise-based colors, not flat toy surfaces.
def organic_material(name,lo,hi,scale,rough=.72,metal=0):
 m=mat(name,lo,metal,rough);n=m.node_tree.nodes;l=m.node_tree.links
 p=n.get("Principled BSDF")
 tex=n.new("ShaderNodeTexNoise");tex.inputs["Scale"].default_value=scale
 tex.inputs["Detail"].default_value=3.0
 ramp=n.new("ShaderNodeValToRGB")
 ramp.color_ramp.elements[0].position=.24
 ramp.color_ramp.elements[0].color=(*lo,1)
 ramp.color_ramp.elements[1].position=.78
 ramp.color_ramp.elements[1].color=(*hi,1)
 l.new(tex.outputs["Fac"],ramp.inputs["Fac"])
 l.new(ramp.outputs["Color"],p.inputs["Base Color"])
 bump=n.new("ShaderNodeBump");bump.inputs["Strength"].default_value=.12
 bump.inputs["Distance"].default_value=.022
 l.new(tex.outputs["Fac"],bump.inputs["Height"])
 l.new(bump.outputs["Normal"],p.inputs["Normal"])
 return m
soil=organic_material("V6 textured dark earth",(.048,.035,.024),(.18,.12,.07),4.2,.97)
bark=organic_material("V6 bark relief",(.025,.025,.018),(.13,.09,.045),12,.96)
deep=organic_material("V6 forest undergrowth",(.016,.042,.018),(.075,.14,.043),9,.89)
leaf1=organic_material("V6 broadleaf",(.035,.09,.027),(.13,.24,.055),7,.72)
leaf2=organic_material("V6 fallen leaf",(.12,.06,.026),(.29,.18,.06),13,.88)
metal=organic_material("V6 iridescent cuticle",(.003,.11,.12),(.012,.48,.31),23,.25,.72)
roachskin=organic_material("V6 cockroach chitin",(.055,.016,.007),(.26,.085,.028),18,.42,.23)
for ob in bpy.data.objects:
 if ob.name=="forest floor":
  ob.data.materials.clear();ob.data.materials.append(soil)
 if ob.name.startswith(("cockroach abdomen","cockroach thorax","cockroach wing cover","cockroach head","cockroach abdomen segment")):
  ob.data.materials.clear();ob.data.materials.append(roachskin)
 if ob.name.startswith(("wasp abdomen","wasp thorax","wasp head","V4 wasp abdomen segment")):
  ob.data.materials.clear();ob.data.materials.append(metal)
# Remove the overly regular V5 pencil trunks and geometric leaf ladders.
for ob in bpy.data.objects:
 if ob.name.startswith(("V5 tapered forest trunk","V5 thin branch","V5 fern stalk","V5 narrow fern leaf","V5 irregular canopy")):
  ob.hide_render=True

# Dense asymmetric trees at multiple distances; clear central action corridor.
for i in range(46):
 side=-1 if i%2 else 1
 x=side*(2.7+rng.uniform(0,7.3))
 y=rng.uniform(-4.8,11.5)
 h=rng.uniform(3.8,9.5)
 points=[(x,y,0),(x+rng.uniform(-.3,.3),y+rng.uniform(-.2,.3),h*.38),
         (x+rng.uniform(-.6,.6),y+rng.uniform(-.5,.5),h*.75)]
 for j in range(2):
  link("V6 irregular trunk",points[j],points[j+1],.13 if j==0 else .09,bark,None)
 for j in range(5):
  a=rng.uniform(0,math.tau);z=h*rng.uniform(.55,.96)
  start=(x,y,z)
  end=(x+math.cos(a)*rng.uniform(.55,1.4),y+math.sin(a)*rng.uniform(.35,1.1),z+rng.uniform(.1,.7))
  link("V6 branch",start,end,.028,bark,None)
  for k in range(6):
   q=k/6
   pos=tuple(start[t]*(1-q)+end[t]*q for t in range(3))
   ob=ell("V6 asymmetrical canopy",pos,(rng.uniform(.19,.38),rng.uniform(.07,.18),rng.uniform(.025,.07)),leaf1)
   ob.rotation_euler=(rng.uniform(-.6,.6),rng.uniform(-.6,.6),rng.uniform(-math.pi,math.pi))
# More natural broad leaves and leaf litter, with varied orientation and size.
for i in range(150):
 x=rng.uniform(-8,8);y=rng.uniform(-5.5,9)
 if abs(x)<1.65 and -2.7<y<3:continue
 z=rng.uniform(.02,.08)
 leaf=ell("V6 irregular leaf litter",(x,y,z),(rng.uniform(.08,.35),rng.uniform(.025,.12),.009),leaf2 if i%3 else leaf1)
 leaf.rotation_euler=(rng.uniform(-.4,.4),rng.uniform(-.3,.3),rng.uniform(0,math.tau))
for i in range(65):
 side=-1 if i%2 else 1
 x=side*rng.uniform(1.9,6.8);y=rng.uniform(-4.3,7)
 height=rng.uniform(.25,.95)
 link("V6 natural fern stem",(x,y,.04),(x+rng.uniform(-.07,.07),y,height),.009,deep,None)
 for j in range(7):
  z=.09+j*height/8
  for sign in (-1,1):
   dx=sign*(.12+.12*math.sin((j+1)*math.pi/8))
   ob=ell("V6 fern frond",(x+dx,y+.06*j,z),(.14,.027,.012),leaf1)
   ob.rotation_euler[2]=sign*rng.uniform(.1,.45)

# Background wall avoids a hard horizon cut to black in low-angle macro shots.
back=organic_material("V6 far forest backdrop",(.012,.025,.014),(.07,.12,.06),1.5,.98)
bpy.ops.mesh.primitive_plane_add(size=2,location=(0,17,5))
wall=bpy.context.object;wall.name="V6 distant forest backdrop"
wall.scale=(40,10,1);wall.rotation_euler[0]=math.pi/2
wall.data.materials.append(back)

# Articulated legs: original straight cylinders are hidden, animated replacements
# use independent body-local hip pivots and alternating tripod phase.
for ob in bpy.data.objects:
 if ob.name in ("cockroach leg upper","cockroach leg lower","wasp leg"):
  ob.hide_render=True
dark=mat("V6 insect joint dark",(.028,.017,.012),.13,.52)
def leg_rig(rig,side,idx,hip,span,front):
 pivot=bpy.data.objects.new("V6 animated leg pivot",None)
 scene.collection.objects.link(pivot);pivot.parent=rig;pivot.location=hip
 knee=(side*span,front,-.13)
 foot=(side*(span+.22),front+.10,-.30)
 link("V6 femur",(0,0,0),knee,.024 if rig==roach else .012,dark,pivot)
 link("V6 tibia",knee,foot,.014 if rig==roach else .007,dark,pivot)
 ell("V6 joint",knee,(.026,.026,.026),dark,pivot)
 phase=(idx+int(side>0))%2
 for f in range(1,241,8):
  angle=.16*math.sin((f-1)*math.tau/24+phase*math.pi)
  pivot.rotation_euler=(angle,side*.05*math.cos((f-1)*math.tau/24+phase*math.pi),0)
  pivot.keyframe_insert(data_path="rotation_euler",frame=f)
 if pivot.animation_data and pivot.animation_data.action:
  for fc in pivot.animation_data.action.fcurves:
   fc.modifiers.new("CYCLES")
for side in (-1,1):
 for idx in range(3):
  leg_rig(roach,side,idx,(side*.29,-.56+idx*.42,.35),.31,.05)
  leg_rig(wasp,side,idx,(side*.17,-.27+idx*.29,.32),.21,.04)

# Burrow must read as a dark cavity with a raised earthen rim.
if chapter>=10:
 cavity=organic_material("V6 burrow dark",(.003,.002,.001),(.025,.014,.006),10,.99)
 ell("V6 burrow deep entrance",(1.9,1.5,.08),(.72,.56,.055),cavity)
 for i in range(28):
  a=math.tau*i/28
  p=(1.9+.75*math.cos(a),1.5+.59*math.sin(a),.14)
  ob=ell("V6 soil clod rim",p,(rng.uniform(.09,.19),rng.uniform(.07,.16),rng.uniform(.07,.15)),soil)
  ob.rotation_euler[2]=a

# Stronger, story-specific portrait compositions with visible action.
shots=[
 ((3.5,-6.2,3.2),(-.3,-.7,.55),27),
 ((-3.2,-4.8,2.1),(-.4,-.65,.5),27),
 ((2.7,-3.9,1.6),(-.25,-.8,.48),30),
 ((2.4,-3.6,1.5),(-.05,-1.0,.42),31),
 ((-2.9,-4.0,2.0),(0,-.25,.48),28),
 ((1.8,-3.5,1.5),(-.1,-1.2,.43),30),
 ((-2.2,-3.7,1.7),(0,-.25,.50),30),
 ((-3.3,-5.1,2.1),(-.3,-.75,.52),27),
 ((2.8,-3.8,1.45),(-.1,-1.0,.45),29),
 ((3.4,-5.1,2.3),(.3,-.2,.43),27),
 ((3.6,-3.4,2.1),(1.6,1.1,.30),28),
 ((3.1,-2.7,1.7),(1.55,1.15,.65),29),
 ((-1.2,-2.6,1.6),(1.55,1.15,.72),30),
 ((4.0,-3.8,2.6),(1.5,.7,1.25),28)]
pos,target,lens=shots[chapter]
cam.animation_data_clear()
for f,factor in ((1,1.14),(120,1.0),(240,.92)):
 cam.location=Vector(target)+(Vector(pos)-Vector(target))*factor
 aim(cam,target)
 cam.keyframe_insert(data_path="location",frame=f)
 cam.keyframe_insert(data_path="rotation_euler",frame=f)
cam.data.lens=lens
cam.data.sensor_fit="VERTICAL"
# Avoid high-contrast overexposure while preserving metallic specular response.
scene.view_settings.view_transform="AgX"
scene.render.image_settings.color_mode="RGB"
scene.render.filepath=os.getenv("BLENDER_OUTPUT","/tmp/jewel_v6_proof.png")
motion=os.getenv("V6_MOTION","0")=="1"
if motion:
 scene.frame_start=1;scene.frame_end=48
 scene.render.image_settings.file_format="FFMPEG"
 scene.render.ffmpeg.format="MPEG4";scene.render.ffmpeg.codec="H264"
 print("JEWEL_V6_MOTION_START",chapter,flush=True)
 bpy.ops.render.render(animation=True)
else:
 scene.render.image_settings.file_format="PNG"
 scene.frame_set(int(os.getenv("PROOF_FRAME","120")))
 print("JEWEL_V6_STILL_START",chapter,flush=True)
 bpy.ops.render.render(write_still=True)
print("JEWEL_V6_RENDER_DONE",chapter,flush=True)
