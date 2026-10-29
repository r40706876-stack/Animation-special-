"""V6.4 visual corrections from actual V6.3 proof 40789821190.

The current proof shows a bead-shaped wasp, slab-shaped roach, a nearly static
pursuit, hidden sting, a separate flat burrow and barely changing larva.
This pass changes real geometry, staging and motion, not QA flags.
"""
import math
import random
from mathutils import Vector

# Replace separated teal beads with one tapered, subtly segmented gaster.
for ob in bpy.data.objects:
    if ob.name.startswith(("V6.1 sculpted gaster", "cockroach abdomen segment",
                           "V4 pronotum shield")):
        ob.hide_render = True
rings = 13
sides = 16
verts = []
faces = []
for i in range(rings):
    t = i / (rings-1)
    y = .29 + .78*t
    radius = (.075 + .155 * math.sin(math.pi*t)**.72) * (1-.23*t)
    for j in range(sides):
        a = 2*math.pi*j/sides
        verts.append((radius*math.cos(a), y,
                      .37 + radius*.78*math.sin(a)))
for i in range(rings-1):
    for j in range(sides):
        k = i*sides+j
        faces.append((k, i*sides+(j+1)%sides,
                      (i+1)*sides+(j+1)%sides, (i+1)*sides+j))
faces.append(tuple(reversed(tuple(range(sides)))))
faces.append(tuple((rings-1)*sides+j for j in range(sides)))
mesh=bpy.data.meshes.new("V6.4 tapered jewel wasp abdomen mesh")
mesh.from_pydata(verts,[],faces)
mesh.update()
gaster=bpy.data.objects.new("V6.4 continuous tapered gaster",mesh)
scene.collection.objects.link(gaster)
gaster.parent=wasp
gaster.data.materials.append(metal)
for poly in mesh.polygons:
    poly.use_smooth=True
# Dark, fine segment seams are placed along the taper, not giant spherical beads.
seam=mat("V6.4 narrow abdominal seam",(.008,.07,.062),.40,.48)
for t in (.23,.40,.57,.73,.87):
    y=.29+.78*t
    r=(.075+.155*math.sin(math.pi*t)**.72)*(1-.23*t)
    for j in range(20):
        a=math.tau*j/20
        b=math.tau*(j+1)/20
        p=(r*math.cos(a),y,.37+r*.78*math.sin(a))
        q=(r*math.cos(b),y,.37+r*.78*math.sin(b))
        link("V6.4 gaster articulation",p,q,.0035,seam,wasp)

# Hide stacked abdominal plates; the original paired wing covers are the shell.
# Make the elytra more tapered, less bread-slab shaped, and give them a seam.
for ob in bpy.data.objects:
    if ob.name.startswith("cockroach wing cover"):
        ob.scale=(.20,.68,.052)
        ob.rotation_euler[1]=(-.09 if ob.location.x<0 else .09)
for ob in bpy.data.objects:
    if ob.name.startswith("cockroach head"):
        ob.scale=(.235,.29,.13)
for ob in bpy.data.objects:
    if ob.name.startswith("wasp head"):
        ob.scale=(.125,.175,.125)
    elif ob.name.startswith("wasp thorax"):
        ob.scale=(.19,.31,.15)
# Reduce studio-beige floor and add low moss/seedling clusters away from actors.
soil_nodes=soil.node_tree.nodes
for n in soil_nodes:
    if n.type=="VALTORGB":
        n.color_ramp.elements[0].color=(.014,.018,.010,1)
        n.color_ramp.elements[1].color=(.075,.065,.035,1)
        break
moss=organic_material("V6.4 damp forest moss",
                      (.012,.045,.014),(.045,.13,.028),14,.98)
rng64=random.Random(6400+chapter)
for i in range(72):
    x=rng64.uniform(-6.8,6.8)
    y=rng64.uniform(-4.2,7.5)
    if abs(x)<1.7 and -2.8<y<3.4:
        continue
    ob=ell("V6.4 uneven moss cluster",(x,y,.036),
           (rng64.uniform(.11,.34),rng64.uniform(.07,.19),.018),moss)
    ob.rotation_euler.z=rng64.uniform(0,math.tau)

# Sting close-ups: the old broad flapping wings obscure the actual needle.
# Fold the wings along the thorax during contact, and show a side-on insert.
if chapter in (3,5):
    for ob in bpy.data.objects:
        if ob.name.startswith(("V6.1 articulated forewing",
                               "V6.1 articulated hindwing")):
            ob.animation_data_clear()
            ob.scale=(.60,.36,1)
            ob.rotation_euler=(.0,.0,0)
    if chapter==3:
        pos,target,lens=(1.65,-1.15,1.06),(-.03,-.73,.60),31
    else:
        pos,target,lens=(-1.65,-1.05,1.10),(-.02,-.93,.60),31
    # A small, dark insertion point should stay visible when the tip arrives.
    for ob in bpy.data.objects:
        if ob.name.startswith("V6.3 visible articulated stinger"):
            ob.data.materials.clear()
            ob.data.materials.append(dark)
            ob.show_in_front=False

# The cockroach head points along local -Y. Earlier scenes put the burrow
# at +Y, behind the roach, so it never visibly entered. Turn it toward +Y,
# and animate both insects into the aperture during chapter 10.
if chapter==10:
    for f,loc in ((1,(.40,-.45,.03)),(120,(1.12,.35,.03)),
                  (240,(1.52,1.14,.03))):
        roach.location=loc
        roach.keyframe_insert(data_path="location",frame=f)
        roach.rotation_euler.z=math.pi
        roach.keyframe_insert(data_path="rotation_euler",frame=f)
    for f,loc in ((1,(.6,.25,.45)),(120,(1.45,1.42,.38)),
                  (240,(1.54,2.05,.32))):
        wasp.location=loc
        wasp.keyframe_insert(data_path="location",frame=f)
        wasp.rotation_euler.z=math.pi
        wasp.keyframe_insert(data_path="rotation_euler",frame=f)
    pos,target,lens=(3.0,-2.0,2.10),(1.45,1.12,.40),28

# Motion proof 0 was six near-identical frames. The camera must see the
# approach rather than an empty clearing; chapter 7 is a different angle.
if chapter==0:
    pos,target,lens=(2.45,-3.65,1.95),(-.70,-.70,.67),29
elif chapter==7:
    pos,target,lens=(-2.35,-3.10,1.65),(-.20,-.50,.52),29
elif chapter==13:
    pos,target,lens=(2.75,-2.65,2.20),(1.55,1.25,1.30),30

# Larva: visible slow crawling/respiration wave instead of a frozen white
# caterpillar; keep the scale keyframes from the existing growth pass.
if chapter==12:
    for ob in bpy.data.objects:
        if ob.name.startswith("V6.1 growing larva segment"):
            base=ob.location.copy()
            for f in (90,96,102,108,114,120,126,138,162,192,240):
                phase=f*.14+base.y*9
                ob.location=(base.x+.014*math.sin(phase),
                             base.y+.020*math.cos(phase),
                             base.z+.012*math.sin(phase))
                ob.keyframe_insert(data_path="location",frame=f)

scene.frame_set(120)
