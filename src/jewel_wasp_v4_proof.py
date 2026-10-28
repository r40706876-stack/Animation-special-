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

# Depth-layered forest rather than a bare studio floor. Keep the insect corridor
# unobstructed and distribute trunks, moss and foliage outside its silhouette.
bark=mat("V4 damp tree bark",(.075,.055,.035),0,.96)
fern_dark=mat("V4 deep forest green",(.018,.095,.043),0,.81)
moss=mat("V4 moss patches",(.06,.13,.035),0,.93)
for i in range(18):
 side=-1 if i%2 else 1
 x=side*(2.8+(i%5)*.67)
 y=-2.1+(i//2)*.84
 h=2.5+(i%4)*.48
 link("V4 forest trunk %02d"%i,(x,y,0),(x+.12*math.sin(i),y+.08,h),.14+(i%3)*.035,bark,None)
 for j in range(3):
  ell("V4 layered forest foliage",(x+.21*math.sin(i+j),y+.16*math.cos(i+j),h-.24+j*.37),(.66,.50,.38),fern_dark)
for i in range(26):
 side=-1 if i%2 else 1
 x=side*(1.9+(i%6)*.53)
 y=-3.0+(i//2)*.56
 patch=ell("V4 forest moss", (x,y,.035),(.35,.25,.018),moss)
 patch.rotation_euler[2]=i*.67

# A clear visual grammar: different scale, angle and focal action for each chapter.
# Each camera location looks toward a specific event, not the same generic center.
# Portrait video has a narrow horizontal FOV. Prior 57-67 mm macro lenses
# cut away heads, wings and most of the action. Pull back and use 24-30 mm.
# Keep the action readable before attempting detail-only inserts.
camera_specs=[
 ((3.3,-5.5,2.7),(-.65,-.65,.65),24),
 ((-3.2,-4.3,2.0),(-.65,-.8,.60),25),
 ((2.5,-3.7,1.5),(-.25,-.85,.50),26),
 ((2.65,-4.0,1.75),(0,-.82,.48),25),
 ((-2.75,-3.9,1.65),(0,-.45,.48),24),
 ((2.65,-3.95,1.70),(0,-1.05,.50),25),
 ((-2.70,-3.85,1.65),(0,-.75,.52),24),
 ((3.1,-4.1,2.0),(-.25,-.65,.48),25),
 ((2.6,-4.1,1.65),(0,-1.15,.48),24),
 ((-3.2,-4.2,2.35),(.10,-.1,.48),24),
 ((4.4,-4.2,2.8),(1.35,.80,.36),24), # 10: full burrow and entering pair
 ((3.7,-3.5,2.6),(1.55,1.10,.69),24), # 11: egg and roach both in view
 ((-1.6,-3.6,2.6),(1.60,1.18,.76),24),# 12: larva on roach, different side
 ((4.6,-4.2,3.2),(1.45,.55,1.55),24), # 13: wasp flying above burrow
]
position,target,lens=camera_specs[chapter]
cam.animation_data_clear()
# Keep full bodies visible in portrait framing, especially for 3-6 and 10-13.
# The previous contact sheet still cropped roach/wasp wings and showed a tree
# completely blocking the burrow and the final take-off shot.
if chapter>=10:
 for ob in bpy.data.objects:
  if ob.name.startswith(("V4 forest trunk","V4 layered forest foliage")):
   ob.hide_render=True
dolly=1.52 if chapter in (3,4,5,6,8,10,11,12,13) else 1.34
for frame,factor in ((1,dolly*1.06),(120,dolly),(240,dolly*.97)):
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
