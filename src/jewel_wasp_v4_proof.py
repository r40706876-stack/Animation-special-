"""V4 visual-story pass for the 14 x 10s Jewel Wasp film.
Runs the existing proven chapter blocking without rendering, then applies cinematic
chapter-specific staging. Default: one QA still; JEWEL_V4_FULL=1: 240-frame MP4.
No paid assets or external Blender plugins.
"""
import os, pathlib, math
import bpy
from mathutils import Vector

base=pathlib.Path(__file__).with_name("jewel_wasp_full.py")
source=base.read_text()
marker="bpy.ops.render.render(animation=True)"
assert source.count(marker)==1, "Original chapter render boundary changed; review wrapper"
context={"__name__":"__main__","__file__":str(base)}
exec(compile(source.split(marker)[0],str(base),"exec"),context)
scene=context["scene"];cam=context["cam"];roach=context["roach"];wasp=context["wasp"]
ell=context["ell"];link=context["link"];mat=context["mat"];aim=context["aim"]
chapter=context["chapter"]
green=context["ns"]["green"];black=context["ns"]["black"]

# Less toy-like silhouettes: cockroach pronotum, wing ridges, antenna joints;
# wasp narrow waist, segmented metallic abdomen and thin antennae.
bronze=mat("V4 dark bronze carapace",(.12,.045,.018),.3,.31)
gold=mat("V4 warm carapace highlights",(.43,.22,.075),.28,.35)
iridescent=mat("V4 metallic teal",(.006,.36,.32),.85,.16)
nerve_mat=mat("V4 scientific nerve overlay",(.98,.26,.015),.2,.23)
ivory=mat("V4 larva ivory",(.87,.81,.60),0,.55)
ell("V4 pronotum shield",(0,-.64,.59),(.38,.28,.09),gold,roach)
for side in (-1,1):
 for idx in range(3):
  y=-.05+idx*.24
  link("V4 wing cover seam",(.06*side,y,.68),(.31*side,y+.13,.66),.009,bronze,roach)
 link("V4 articulated roach antenna",(side*.1,-1.14,.44),(side*.32,-1.52,.48),.012,bronze,roach)
 link("V4 articulated roach antenna tip",(side*.32,-1.52,.48),(side*.56,-2.08,.31),.007,black,roach)
 link("V4 wasp antenna",(side*.09,-.59,.48),(side*.19,-.91,.61),.011,black,wasp)
ell("V4 wasp waist",(0,.18,.38),(.085,.18,.085),iridescent,wasp)
for i in range(3):
 ell("V4 wasp abdomen segment %d"%i,(0,.34+i*.16,.35),(.18-i*.022,.095,.17-i*.016),iridescent,wasp)

# Foreground depth cues, deliberately outside the central insect corridor.
leaf_mat=mat("V4 fern leaves",(.055,.21,.095),0,.77)
stem_mat=mat("V4 forest stems",(.10,.16,.045),0,.8)
for i in range(10):
 x=(-3.2 if i%2 else 3.2)+.28*math.sin(i*2.4)
 y=-2.5+(i//2)*1.1
 height=.38+.11*(i%3)
 link("V4 fern stem %d"%i,(x,y,.06),(x,y,.06+height),.018,stem_mat,None)
 for side in (-1,1):
  for j in range(3):
   z=.18+j*.11
   ob=ell("V4 fern leaflet",(x+side*(.13+j*.045),y,z),(.19,.075,.018),leaf_mat)
   ob.rotation_euler[1]=side*.34

# A clear visual grammar: different scale, angle and focal action for each chapter.
# Each camera location looks toward a specific event, not the same generic center.
camera_specs=[
 ((3.3,-5.5,2.7),(0,-.25,.4),34),     # 0 forest encounter
 ((-3.2,-4.3,2.0),(-.35,-.65,.5),42), # 1 pursuit
 ((2.5,-3.7,1.5),(0,-.95,.45),50),   # 2 chase
 ((1.55,-2.8,1.15),(0,-.70,.46),57), # 3 thoracic sting
 ((-1.35,-2.65,1.15),(0,-.45,.48),61),# 4 leg nerve effect
 ((1.35,-2.65,1.20),(0,-1.02,.48),64),# 5 head sting
 ((-1.25,-2.6,1.22),(0,-.95,.46),65), # 6 neural signaling
 ((3.1,-4.1,2.0),(-.15,-.65,.43),42), # 7 altered behavior
 ((1.45,-2.85,1.12),(0,-1.25,.45),59),# 8 antenna guidance
 ((-3.2,-4.2,2.35),(.25,.10,.38),38), # 9 journey
 ((3.15,-2.4,2.15),(1.52,1.0,.25),45),# 10 burrow
 ((2.55,-.65,1.36),(1.58,1.19,.69),62),# 11 egg
 ((2.48,-.60,1.43),(1.60,1.25,.77),67),# 12 larva
 ((3.5,-3.25,2.65),(1.50,1.2,.6),40),# 13 next generation
]
position,target,lens=camera_specs[chapter]
cam.animation_data_clear()
for frame,factor in ((1,1.10),(120,1.0),(240,.92)):
 cam.location=Vector(target)+(Vector(position)-Vector(target))*factor
 aim(cam,target)
 cam.keyframe_insert(data_path="location",frame=frame)
 cam.keyframe_insert(data_path="rotation_euler",frame=frame)
cam.data.lens=lens
cam.data.clip_start=.015

# Event-specific blocking: don't let two insects overlap in the close-ups.
if chapter in (3,5):
 wasp.animation_data_clear()
 offset=(-.13,-1.39,.23) if chapter==3 else (-.13,-1.85,.24)
 for f,z in ((1,.42),(95,.23),(165,.22),(240,.39)):
  wasp.location=(offset[0],offset[1],z)
  wasp.keyframe_insert(data_path="location",frame=f)
 needle=ell("V4 visible sting needle",(0,1.00,.30),(.022,.21,.023),black,wasp)
 for f,s in ((1,.04),(95,1),(165,1),(240,.04)):
  needle.scale=(.022,.21*s,.023)
  needle.keyframe_insert(data_path="scale",frame=f)
if chapter in (4,6):
 # A deliberately schematic nerve pathway: bright points and connecting lines.
 # It is a visual explanation, not an anatomical claim about exact nerve locations.
 for ob in [wasp]+[o for o in bpy.data.objects if o.parent==wasp]:
  ob.hide_render=True
 coords=[(0,-.95,.62),(0,-.65,.68),(0,-.30,.72),(0,.02,.70),(0,.36,.65)]
 for i,p in enumerate(coords):
  node=ell("V4 neural node %d"%i,p,(.055,.055,.052),nerve_mat,roach)
  for f,scale in ((1,.15),(50+i*20,1),(120+i*10,1.2),(240,.2)):
   node.scale=(.055*scale,.055*scale,.052*scale)
   node.keyframe_insert(data_path="scale",frame=f)
  if i:
   link("V4 neural pathway",coords[i-1],p,.014,nerve_mat,roach)
if chapter==8:
 wasp.animation_data_clear()
 for f,pos in ((1,(-.75,-1.05,.40)),(120,(-.47,-.85,.28)),(240,(-.4,-.70,.3))):
  wasp.location=pos
  wasp.keyframe_insert(data_path="location",frame=f)
if chapter in (10,11,12,13):
 # Give the burrow an unmistakable opening, earthen rim and visual depth.
 earth=mat("V4 burrow earth",(.10,.07,.045),0,.95)
 dark=mat("V4 burrow interior",(.008,.007,.005),0,.98)
 ell("V4 deep burrow cavity",(1.9,1.5,.026),(.75,.55,.05),dark)
 for i in range(16):
  a=i*math.tau/16
  ell("V4 soil rim",(1.9+.77*math.cos(a),1.5+.58*math.sin(a),.12),(.15,.13,.10),earth)
if chapter==11:
 # Egg should be seen clearly on the cockroach without becoming gigantic.
 for ob in bpy.data.objects:
  if ob.name.startswith("wasp egg on cockroach"):
   ob.hide_render=False
if chapter==12:
 # A segmented larva reads better than a single white ball.
 for i in range(4):
  ell("V4 larva segment %d"%i,(.05,.02+i*.11,.80),(.09,.085,.09),ivory,roach)
if chapter==13:
 # Flight away from the burrow closes the lifecycle instead of another sting shot.
 wasp.animation_data_clear()
 for f,p in ((1,(1.35,.9,.65)),(120,(1.5,.5,1.7)),(240,(.9,-.2,2.5))):
  wasp.location=p;wasp.keyframe_insert(data_path="location",frame=f)

# Soft fill and rim light to separate metallic insects from the ground.
bpy.ops.object.light_add(type="AREA",location=(-2,1.5,3.2))
bpy.context.object.data.energy=410
bpy.context.object.data.size=3.0

out=os.getenv("BLENDER_OUTPUT","/tmp/jewel_v4_proof.png")
scene.render.filepath=out
if os.getenv("JEWEL_V4_FULL","0")=="1":
 scene.render.image_settings.file_format="FFMPEG"
 scene.render.ffmpeg.format="MPEG4";scene.render.ffmpeg.codec="H264"
 print("JEWEL_V4_FULL_RENDER",chapter,out,flush=True)
 bpy.ops.render.render(animation=True)
else:
 scene.render.image_settings.file_format="PNG"
 scene.frame_set(int(os.getenv("PROOF_FRAME","120")))
 print("JEWEL_V4_PROOF_FRAME",chapter,scene.frame_current,out,flush=True)
 bpy.ops.render.render(write_still=True)
print("JEWEL_V4_RENDER_DONE",chapter,flush=True)
