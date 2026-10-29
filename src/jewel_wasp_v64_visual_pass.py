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


# V6.5: direct correction from V6.4 proof 40796041871
# Verified 14-still contact and all five motion strips: chapters 3/5 have no
# legible needle insertion, 10 shows no visible hole, 12 shows a floating
# emerald gaster, and 0/7 are composition duplicates.
if chapter in (3,5):
    # Rebuild the already-created needle's actual world-space trajectory from
    # evaluated rig transforms. A static green abdomen is not a sting.
    shaft=next((ob for ob in bpy.data.objects
                if ob.name.startswith("V6.3 visible articulated stinger")),None)
    if shaft is not None:
        shaft.animation_data_clear()
        for frame,reach in ((1,.015),(84,.015),(90,.10),(96,.36),
                            (102,.67),(110,1.0),(118,1.0),(126,.60),
                            (140,.12),(170,.015),(240,.015)):
            scene.frame_set(frame)
            start=wasp.matrix_world @ Vector((0,.94,.31))
            target_point=roach.matrix_world @ Vector((0,-.54 if chapter==3 else -.91,.69))
            tip=start.lerp(target_point,reach)
            delta=tip-start
            shaft.location=(start+tip)*.5
            shaft.rotation_euler=delta.to_track_quat('Z','Y').to_euler()
            shaft.scale=(1.30,1.30,max(.003,delta.length))
            for path in ("location","rotation_euler","scale"):
                shaft.keyframe_insert(data_path=path,frame=frame)
    wound=mat("V6.5 dark amber sting entry",(.12,.026,.008),.10,.56)
    contact=ell("V6.5 visible sting contact",
                (0,-.54 if chapter==3 else -.91,.70),
                (.045,.047,.012),wound,roach)
    for frame,scale in ((1,.001),(96,.001),(108,.40),(114,1.0),
                        (138,1.0),(240,.60)):
        contact.scale=(.045*scale,.047*scale,.012*scale)
        contact.keyframe_insert(data_path="scale",frame=frame)
    if chapter==3:
        pos,target,lens=(1.65,-1.95,1.25),(-.06,-.57,.64),36
    else:
        pos,target,lens=(-1.65,-2.08,1.26),(-.06,-.92,.64),36

if chapter==7:
    # Change visual grammar to a high oblique inspection, not another pursuit
    # profile that the automated audit correctly flags as chapter-0 duplicate.
    pos,target,lens=(-1.45,-1.65,3.20),(-.25,-.68,.50),34

if chapter==10:
    # The entrance was outside the close-up motion framing. Move the mouth
    # and low rim together into the head-first approach, then keep it on screen.
    for ob in bpy.data.objects:
        if ob.name.startswith(("V6.3 burrow dark opening",
                               "V6.3 uneven burrow lip")):
            ob.location.y-=.40
    for frame,loc in ((1,(.40,-.45,.03)),(120,(1.12,.35,.03)),
                      (240,(1.52,1.35,.03))):
        roach.location=loc
        roach.rotation_euler.z=math.pi
        roach.keyframe_insert(data_path="location",frame=frame)
        roach.keyframe_insert(data_path="rotation_euler",frame=frame)
    pos,target,lens=(3.30,-3.45,3.15),(1.42,1.18,.20),25
    # Clear only foreground geometry that obstructs this actual sightline.
    dx=target[0]-pos[0]
    dy=target[1]-pos[1]
    denom=dx*dx+dy*dy
    for ob in bpy.data.objects:
        if ob.name.startswith(("V6 irregular trunk","V6 branch",
                               "V6 asymmetrical canopy")):
            ox=ob.location.x-pos[0]
            oy=ob.location.y-pos[1]
            q=(ox*dx+oy*dy)/denom
            if .08<q<1.0 and math.hypot(ox-q*dx,oy-q*dy)<.95:
                ob.hide_render=True

if chapter==12:
    # V6.4 created a NEW gaster after the older chapter-12 hide pass. It
    # remained visible as a detached turquoise oval over the larva.
    for ob in bpy.data.objects:
        ancestor=ob
        while ancestor is not None:
            if ancestor==wasp:
                ob.hide_render=True
                break
            ancestor=ancestor.parent
    for ob in bpy.data.objects:
        if ob.name.startswith("V6.1 growing larva segment"):
            base=ob.location.copy()
            for frame in (90,95,100,105,110,115,120,126,138,162,192,240):
                phase=frame*.29+base.y*11
                ob.location=(base.x+.032*math.sin(phase),
                             base.y+.036*math.cos(phase),
                             base.z+.022*math.sin(phase+.8))
                ob.keyframe_insert(data_path="location",frame=frame)
    pos,target,lens=(2.20,-.70,1.42),(1.52,1.22,.75),38

scene.frame_set(120)


# V6.6: correct actual V6.5 proof 40802877587 (14 stills + 5 motion clips).
# The previous needle began almost exactly on its roach target, so it could
# never read as a penetrating stinger. Separate the insects and use a lateral
# camera; place the burrow mouth ahead of the roach, not beneath its head.
if chapter in (3, 5):
    side = -1 if chapter == 3 else 1
    wasp.animation_data_clear()
    for frame, height in ((1,.64),(84,.58),(90,.54),(96,.49),
                          (102,.46),(110,.44),(118,.44),(126,.47),
                          (140,.54),(170,.60),(240,.66)):
        wasp.location = (side*.53, -2.18 if chapter==3 else -2.55, height)
        wasp.rotation_euler = (0,0,0)
        wasp.keyframe_insert(data_path="location", frame=frame)
        wasp.keyframe_insert(data_path="rotation_euler", frame=frame)
    shaft = next((ob for ob in bpy.data.objects
                  if ob.name.startswith("V6.3 visible articulated stinger")), None)
    if shaft:
        shaft.hide_render = False
        shaft.animation_data_clear()
        shaft.data.materials.clear()
        shaft.data.materials.append(
            mat("V6.6 copper ovipositor readable in side light",
                (.26,.105,.023),.20,.30))
        for frame, reach in ((1,.02),(84,.02),(90,.10),(96,.34),
                             (102,.72),(110,1.0),(118,1.0),
                             (126,.72),(140,.12),(170,.02),(240,.02)):
            scene.frame_set(frame)
            start = wasp.matrix_world @ Vector((0,.94,.31))
            tip_target = roach.matrix_world @ Vector(
                (side*.23,-.54 if chapter==3 else -.91,.69))
            tip = start.lerp(tip_target, reach)
            direction = tip-start
            shaft.location = (start+tip)*.5
            shaft.rotation_euler = direction.to_track_quat('Z','Y').to_euler()
            shaft.scale = (1.65,1.65,max(.004,direction.length))
            for path in ("location","rotation_euler","scale"):
                shaft.keyframe_insert(data_path=path,frame=frame)
    for ob in bpy.data.objects:
        if ob.name.startswith("V6.5 visible sting contact"):
            ob.location.x = side*.23
    if chapter == 3:
        pos,target,lens = (-2.45,-2.85,1.42),(-.29,-1.02,.65),33
    else:
        pos,target,lens = (2.50,-3.00,1.47),(.27,-1.26,.65),33

if chapter == 10:
    # The V6.5 opening was an invisible flat oval directly under the insect.
    # Build an elevated, camera-facing tunnel mouth with a true dark interior.
    for ob in bpy.data.objects:
        if ob.name.startswith(("V6.3 burrow dark opening",
                               "V6.3 uneven burrow lip")):
            ob.hide_render = True
    hole_x, hole_y = 1.48, 2.52
    cave = organic_material("V6.6 deep tunnel black",
                            (.0005,.0004,.0003),(.009,.006,.004),10,.98)
    ell("V6.6 excavated earth mound",(hole_x,hole_y+.36,.23),
        (.92,.52,.37),soil)
    ell("V6.6 vertical shadowed tunnel entrance",(hole_x,hole_y-.08,.27),
        (.57,.055,.32),cave)
    for j in range(19):
        a = math.pi*j/18
        x = hole_x+.60*math.cos(a)
        z = .27+.34*math.sin(a)
        ell("V6.6 uneven arched earthen rim",(x,hole_y-.14,z),
            (.065,.09,.065),soil)
    # Clear foliage from the entrance itself; leave the rest of the forest.
    for ob in bpy.data.objects:
        if ob.name.startswith(("V6 fern frond","V6 natural fern stem",
                               "V6 irregular leaf litter",
                               "V6.4 uneven moss cluster")):
            if (ob.location.x-hole_x)**2+(ob.location.y-hole_y)**2 < 1.05**2:
                ob.hide_render = True
    roach.animation_data_clear()
    for frame,loc in ((1,(.40,-.45,.03)),(120,(1.10,.40,.03)),
                      (185,(1.28,.97,.01)),(240,(1.48,1.66,-.08))):
        roach.location=loc
        roach.rotation_euler.z=math.pi
        roach.keyframe_insert(data_path="location",frame=frame)
        roach.keyframe_insert(data_path="rotation_euler",frame=frame)
    wasp.animation_data_clear()
    for frame,loc in ((1,(.30,-.25,.48)),(120,(.55,.40,.44)),
                      (185,(.65,.83,.41)),(240,(.76,1.25,.35))):
        wasp.location=loc
        wasp.rotation_euler.z=math.pi
        wasp.keyframe_insert(data_path="location",frame=frame)
        wasp.keyframe_insert(data_path="rotation_euler",frame=frame)
    pos,target,lens=(3.25,-2.85,2.80),(1.36,1.30,.30),24

scene.frame_set(120)
