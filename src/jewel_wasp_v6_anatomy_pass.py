"""V6.1 anatomical and narrative corrections from direct review of proof 40767077776.
This is Blender scene-building code executed inside jewel_wasp_v6_proof.py.
It must not change V4 or approve the expensive full render automatically.
"""
import math
from mathutils import Vector

# Fix the bright, rounded 'stack of bread' cockroach back seen in all macros.
for ob in bpy.data.objects:
    if ob.name.startswith("V4 pronotum shield"):
        ob.scale=(.29,.24,.055)
        ob.data.materials.clear()
        ob.data.materials.append(roachskin)
    elif ob.name.startswith("cockroach wing cover"):
        ob.scale=(.195,.59,.047)
        ob.data.materials.clear()
        ob.data.materials.append(roachskin)
    elif ob.name.startswith("cockroach abdomen segment"):
        ob.scale=(ob.scale.x,ob.scale.y,ob.scale.z*.74)
    elif ob.name.startswith("V5 cockroach tibia spines"):
        # V5 spines did not follow the articulated V6 leg pivots.
        ob.hide_render=True

# Replace toy-like three emerald balls with a visibly separated head,
# thorax, petiole, tapered gaster, and surface-segmented abdomen.
for ob in bpy.data.objects:
    if ob.name.startswith(("wasp abdomen","V4 wasp abdomen segment","V4 wasp waist")):
        ob.hide_render=True
for i in range(5):
    t=i/4
    gaster=ell("V6.1 sculpted gaster %02d"%i,
        (0,.38+i*.14,.37+.015*math.sin(i*.8)),
        (.135+.08*math.sin(math.pi*t),.103,.135+.055*math.sin(math.pi*t)),
        metal,wasp)
    gaster.rotation_euler[0]=-.06*math.sin(i*.8)
petiole=link("V6.1 narrow wasp petiole",(0,.08,.38),(0,.34,.38),.052,metal,wasp)
# A small tapered head, prominent dark compound eyes and antennae.
for ob in bpy.data.objects:
    if ob.name.startswith("wasp head"):
        ob.scale=(.16,.16,.145)
    if ob.name.startswith("wasp eye"):
        ob.scale=(.064,.073,.075)
for side in (-1,1):
    for j in range(9):
        a=math.tau*j/9
        # Tiny dark facets follow the visible side of the eye.
        ell("V6.1 compound eye facet",
            (side*(.195+.007*math.cos(a)),-.49+.047*math.sin(a),.45+.048*math.cos(a)),
            (.012,.011,.012),dark,wasp)
    link("V6.1 articulated antenna",
         (side*.09,-.58,.45),(side*.18,-.77,.52),.009,dark,wasp)
    link("V6.1 antenna tip",
         (side*.18,-.77,.52),(side*.24,-.92,.59),.006,dark,wasp)

# Transparent, pointed fore/hind wings with vein paths replace broad opaque
# white ellipsoids that looked like crossed paddles.
for ob in bpy.data.objects:
    if ob.name.startswith(("animated wasp wing","V5 wasp wing veins")):
        ob.hide_render=True
wingmat=mat("V6.1 translucent membrane",(.13,.27,.28),.04,.37)
p=wingmat.node_tree.nodes.get("Principled BSDF")
p.inputs["Alpha"].default_value=.35
if "Transmission Weight" in p.inputs:
    p.inputs["Transmission Weight"].default_value=.24
if hasattr(wingmat,"surface_render_method"):
    wingmat.surface_render_method="DITHERED"
veinmat=mat("V6.1 fine wing venation",(.018,.085,.08),.12,.45)
for side in (-1,1):
    for pair in range(2):
        span=.83 if pair==0 else .58
        yshift=-.015 if pair==0 else .17
        points=[
            (0,0,0),
            (side*.18,-.085,0),
            (side*.52,-.12,0),
            (side*span,.015,0),
            (side*.58,.11,0),
            (side*.30,.15,0),
            (side*.10,.08,0)]
        mesh=bpy.data.meshes.new("V6.1 wing membrane mesh")
        mesh.from_pydata(points,[],[(0,1,2,3,4,5,6)])
        mesh.update()
        ob=bpy.data.objects.new("V6.1 articulated forewing" if pair==0 else "V6.1 articulated hindwing",mesh)
        scene.collection.objects.link(ob)
        ob.parent=wasp
        ob.location=(side*.15,yshift,.56)
        ob.data.materials.append(wingmat)
        # Veins are children of each wing so they flap with the membrane.
        for endpoint in ((side*.50,-.035,.002),(side*.35,.095,.002)):
            link("V6.1 wing vein",(0,0,.002),endpoint,.0035,veinmat,ob)
        for frame in range(1,242,4):
            phase=frame*math.tau/12+(pair*.4)
            ob.rotation_euler=(.03*math.sin(phase),side*(.26+.46*math.sin(phase)),side*.05)
            ob.keyframe_insert(data_path="rotation_euler",frame=frame)
        if ob.animation_data and ob.animation_data.action:
            for fc in ob.animation_data.action.fcurves:
                fc.modifiers.new("CYCLES")

# Give the burrow a legible dark opening rather than a pile of stones.
if chapter>=10:
    for ob in bpy.data.objects:
        if ob.name.startswith(("burrow edge pebble","V4 soil rim","V4 deep burrow cavity","burrow entrance","V6 soil clod rim","V6 burrow deep entrance")):
            ob.hide_render=True
    cavity=organic_material("V6.1 cavity near-black",(.002,.002,.001),(.018,.011,.006),8,.98)
    ell("V6.1 clearly visible burrow aperture",(1.9,1.5,.10),(.86,.61,.017),cavity)
    for i in range(24):
        a=math.tau*i/24
        x=1.9+(.94+.055*math.sin(i*2.7))*math.cos(a)
        y=1.5+(.69+.045*math.cos(i*1.7))*math.sin(a)
        ell("V6.1 low earth rim",(x,y,.105),
            (.10+.04*abs(math.sin(i)),.085,.055),soil)

# Make the development stage readable as its own shot: no hovering wasp
# hiding the larva, and a segmented, grounded larva on the roach cuticle.
if chapter==12:
    for ob in bpy.data.objects:
        if ob==wasp or ob.parent==wasp or ob.name.startswith("V6.1 wing"):
            ob.hide_render=True
    for ob in bpy.data.objects:
        if ob.name.startswith(("V6 segmented larva","wasp egg on cockroach")):
            ob.hide_render=True
    larva_skin=organic_material("V6.1 larva cuticle",(.48,.37,.23),(.85,.75,.54),12,.65)
    for i in range(9):
        t=i/8
        taper=.32+.68*math.sin(math.pi*t)**.6
        seg=ell("V6.1 growing larva segment %02d"%i,
            (.035,-.12+i*.087,.74+.014*math.sin(i*.65)),
            (.115*taper,.063,.104*taper),larva_skin,roach)
        seg.rotation_euler[0]=.12*math.sin(i*.7)
        for f,s in ((1,.20),(95,.55),(175,.82),(240,1)):
            seg.scale=(.115*taper*s,.063*s,.104*taper*s)
            seg.keyframe_insert(data_path="scale",frame=f)


# V6.2 visual correction from the actual 40775022479 stills/motion strips:
# a readable ground aperture must NOT be hidden under the roach in chapter 10.
if chapter >= 10:
    for ob in bpy.data.objects:
        if ob.name.startswith(("V6.1 clearly visible burrow aperture", "V6.1 low earth rim")):
            ob.hide_render = True
    opening = (2.05, 2.60)
    cavity = organic_material("V6.2 burrow deep shadow", (.0015,.0012,.0008),(.014,.009,.005),11,.99)
    ell("V6.2 visible dark burrow mouth",
        (opening[0],opening[1],.09),(.87,.63,.018),cavity)
    for i in range(32):
        a=math.tau*i/32
        x=opening[0]+(.98+.04*math.sin(3*a))*math.cos(a)
        y=opening[1]+(.72+.04*math.cos(5*a))*math.sin(a)
        clod=ell("V6.2 irregular low earth lip",
            (x,y,.10),(.085+.025*abs(math.sin(a*2)),.075,.038),soil)
        clod.rotation_euler[2]=a

# Actual motion proof sampled frames 95..118, where the old sting was held
# motionless. Animate a needle extension and withdrawal through that window.
if chapter in (3,5):
    for ob in bpy.data.objects:
        if ob.name.startswith(("V4 visible sting needle","sting tip")):
            ob.hide_render=True
    needle_mat=mat("V6.2 dark chitin stinger",(.025,.013,.010),.12,.39)
    needle=ell("V6.2 animated contact needle",(0,.94,.30),(.017,.26,.017),needle_mat,wasp)
    for f,extension in ((1,.03),(78,.03),(94,.22),(107,1.0),(121,1.0),(145,.18),(175,.03),(240,.03)):
        needle.scale=(.017,.26*extension,.017)
        needle.location=(0,.83+.11*extension,.30)
        needle.keyframe_insert(data_path="scale",frame=f)
        needle.keyframe_insert(data_path="location",frame=f)

# The insect antennae should not look like unrelated floating black rods
# around the developing larva in the extreme-macro chapter.
if chapter == 12:
    for ob in bpy.data.objects:
        if ob.name.startswith(("cockroach antenna","V4 articulated roach antenna")):
            ob.hide_render=True
