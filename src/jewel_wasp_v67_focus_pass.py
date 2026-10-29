"""V6.7 isolated action proof from direct visual review of V6.6 motion clips.
This is intentionally a *new* file: V6.6's successful artifacts are not cancelled.
Never interpret a passing render as visual approval of the full film.
"""
import math
from mathutils import Vector

if chapter in (3, 5):
    # Replace the old largely occluded shaft, not just its camera.
    for ob in bpy.data.objects:
        if ob.name.startswith(("V6.3 visible articulated stinger",
                               "V6.3 roach sting entry",
                               "V6.5 visible sting contact")):
            ob.hide_render = True

    # Side-separated actors leave a clear silhouette of the actual contact.
    wasp.animation_data_clear()
    x = -.91 if chapter == 3 else -.83
    y = -1.76 if chapter == 3 else -1.86
    for f, z, dx in ((1,.79,-.12),(84,.73,-.08),(90,.70,-.04),
                     (96,.63,-.02),(102,.59,0),(110,.57,0),
                     (118,.57,0),(126,.60,0),(140,.68,-.04),
                     (180,.78,-.10),(240,.82,-.14)):
        wasp.location = (x+dx, y, z)
        wasp.rotation_euler = (0,0,0)
        wasp.keyframe_insert(data_path="location", frame=f)
        wasp.keyframe_insert(data_path="rotation_euler", frame=f)

    # A slender tapered ovipositor is attached to the posterior gaster tip,
    # advancing toward the cockroach flank. Both ends are evaluated in world
    # coordinates at every keyframe; there is no stale static needle.
    needle_mat = mat("V6.7 visible amber ovipositor",(.24,.075,.017),.30,.34)
    bpy.ops.mesh.primitive_cone_add(vertices=16,radius1=.017,radius2=.003,
                                    depth=1)
    shaft = bpy.context.object
    shaft.name = "V6.7 world-space extending ovipositor"
    shaft.data.materials.append(needle_mat)
    tip = ell("V6.7 sting needle tip",(0,0,0),(.021,.021,.021),needle_mat)
    target_local = Vector((-.31, -.58 if chapter==3 else -.91, .64))
    for f, reach in ((1,.03),(84,.03),(90,.07),(96,.26),
                     (102,.55),(108,.85),(114,1.0),(120,1.0),
                     (126,.72),(138,.20),(160,.03),(240,.03)):
        scene.frame_set(f)
        start = wasp.matrix_world @ Vector((0,1.00,.37))
        target_world = roach.matrix_world @ target_local
        end = start.lerp(target_world,reach)
        delta = end-start
        shaft.location = (start+end)*.5
        shaft.rotation_euler = delta.to_track_quat('Z','Y').to_euler()
        shaft.scale = (1.0,1.0,max(.005,delta.length))
        tip.location = end
        tip.scale = (.021,.021,.021)
        for prop in ("location","rotation_euler","scale"):
            shaft.keyframe_insert(data_path=prop,frame=f)
        tip.keyframe_insert(data_path="location",frame=f)

    contact_mat = mat("V6.7 subtle cuticle contact",(.10,.032,.009),.07,.65)
    contact = ell("V6.7 roach flank entry",tuple(target_local),
                  (.030,.030,.008),contact_mat,roach)
    for f, size in ((1,.01),(105,.01),(114,1),(126,1),(240,.65)):
        contact.scale = (.030*size,.030*size,.008*size)
        contact.keyframe_insert(data_path="scale",frame=f)
    # Contact-focused macro composition; the second sting uses a distinct
    # opposing camera rather than repeating the same wide two-insect shot.
    if chapter==3:
        pos,target,lens = (1.20,-2.75,1.42),(-.50,-.84,.68),42
    else:
        pos,target,lens = (-1.90,-2.42,1.28),(-.52,-1.03,.67),41

if chapter == 10:
    # Actual V6.6 motion_10.mp4 still shows a detached black tyre-shaped
    # burrow. Move its opening into the path of the approaching cockroach.
    for ob in bpy.data.objects:
        if ob.name.startswith(("V6 burrow deep entrance","V6 soil clod rim",
                               "V4 deep burrow cavity","V4 soil rim",
                               "burrow entrance","burrow edge pebble")):
            ob.hide_render=True
        if ob.name.startswith(("V6.6 excavated earth mound",
                               "V6.6 vertical shadowed tunnel entrance",
                               "V6.6 uneven arched earthen rim")):
            ob.location.y -= .37
        if ob.name.startswith("V6.6 uneven arched earthen rim"):
            ob.hide_render=True
    # Replace the regular circular clods with asymmetric broken earth.
    local_rng = random.Random(6710)
    for i in range(13):
        a = math.pi*i/12
        px = 1.48 + (.58+.035*math.sin(i*2.1))*math.cos(a)
        pz = .27 + (.34+.035*math.cos(i*1.9))*math.sin(a)
        clod = ell("V6.7 asymmetric excavated rim",(px,2.01,pz),
                   (local_rng.uniform(.055,.105),
                    local_rng.uniform(.07,.12),
                    local_rng.uniform(.035,.095)),soil)
        clod.rotation_euler.y = local_rng.uniform(-.35,.35)
    roach.animation_data_clear()
    for f, p in ((1,(.40,-.45,.03)),(120,(1.15,.43,.03)),
                 (185,(1.42,1.02,.03)),(205,(1.48,1.33,.02)),
                 (220,(1.48,1.58,-.02)),(240,(1.48,1.93,-.12))):
        roach.location = p
        roach.rotation_euler = (0,0,math.pi)
        roach.keyframe_insert(data_path="location",frame=f)
        roach.keyframe_insert(data_path="rotation_euler",frame=f)
    wasp.animation_data_clear()
    for f,p in ((1,(.18,-.40,.60)),(120,(.28,.30,.48)),
                (185,(.40,.90,.45)),(240,(.50,1.28,.48))):
        wasp.location=p
        wasp.rotation_euler=(0,0,math.pi)
        wasp.keyframe_insert(data_path="location",frame=f)
        wasp.keyframe_insert(data_path="rotation_euler",frame=f)
    pos,target,lens=(3.0,-1.90,1.85),(1.44,1.71,.32),28

if chapter == 12:
    # Give the larva a visible peristaltic wave rather than white rigid beads.
    for ob in bpy.data.objects:
        if ob.name.startswith("V6.1 growing larva segment"):
            base_loc = ob.location.copy()
            base_scale = ob.scale.copy()
            for f in (90,95,100,105,110,115,120,126,140,160,200,240):
                phase = f*.23 + base_loc.y*15
                ob.location = (base_loc.x+.023*math.sin(phase),
                               base_loc.y+.035*math.cos(phase),
                               base_loc.z+.018*math.sin(phase+1.2))
                ob.scale = (base_scale.x*(1+.13*math.sin(phase)),
                            base_scale.y*(1-.09*math.sin(phase)),
                            base_scale.z*(1+.11*math.sin(phase+.8)))
                ob.keyframe_insert(data_path="location",frame=f)
                ob.keyframe_insert(data_path="scale",frame=f)
    pos,target,lens=(2.05,-.78,1.50),(1.53,1.21,.76),39

scene.frame_set(120)


# V6.7.1 focused corrections from the *actual* 4-still/4-motion evidence
# in run 40814728556. Never treat technical green as a visual pass.
if chapter in (3, 5):
    # The V6.7 close-up cropped the wasp and the roach so far that a viewer
    # could not identify the sting. Keep both bodies and the moving tip in view.
    scene.frame_set(114)
    start = wasp.matrix_world @ Vector((0, 1.00, .37))
    flank = roach.matrix_world @ Vector((-.24, -.58 if chapter == 3 else -.83, .73))
    midpoint = (start + flank) * .5
    target = tuple(midpoint)
    offset = Vector((1.55 if chapter == 3 else -1.55, -3.2, 1.25))
    pos = tuple(midpoint + offset)
    lens = 25
    # A second, more readable needle targets the exposed upper flank.
    shaft = bpy.data.objects.get("V6.7 world-space extending ovipositor")
    tip = bpy.data.objects.get("V6.7 sting needle tip")
    if shaft and tip:
        shaft.animation_data_clear()
        tip.animation_data_clear()
        for frame, reach in ((1, .02), (84, .02), (90, .08),
                             (96, .28), (102, .56), (108, .82),
                             (114, 1.0), (120, 1.0), (126, .70),
                             (138, .12), (160, .02), (240, .02)):
            scene.frame_set(frame)
            base = wasp.matrix_world @ Vector((0, 1.00, .37))
            hit = roach.matrix_world @ Vector(
                (-.24, -.58 if chapter == 3 else -.83, .73))
            endpoint = base.lerp(hit, reach)
            delta = endpoint - base
            shaft.location = (base + endpoint) * .5
            shaft.rotation_euler = delta.to_track_quat('Z', 'Y').to_euler()
            shaft.scale = (1.0, 1.0, max(.003, delta.length))
            tip.location = endpoint
            for path in ("location", "rotation_euler", "scale"):
                shaft.keyframe_insert(data_path=path, frame=frame)
            tip.keyframe_insert(data_path="location", frame=frame)
    mark = bpy.data.objects.get("V6.7 roach flank entry")
    if mark:
        mark.location = (-.24, -.58 if chapter == 3 else -.83, .73)
    scene.frame_set(120)

if chapter == 10:
    # V6.7 frames 210–233 showed almost no readable entry. Move the roach
    # decisively through the aperture, with a downward burrow trajectory.
    roach.animation_data_clear()
    for frame, loc in ((1, (.40, -.45, .03)),
                       (120, (1.15, .43, .03)),
                       (185, (1.43, 1.02, .03)),
                       (205, (1.48, 1.35, .02)),
                       (215, (1.48, 1.55, -.02)),
                       (225, (1.48, 1.95, -.18)),
                       (240, (1.48, 2.65, -.46))):
        roach.location = loc
        roach.rotation_euler = (0, 0, math.pi)
        roach.keyframe_insert(data_path="location", frame=frame)
        roach.keyframe_insert(data_path="rotation_euler", frame=frame)
    # Center the arched mouth and animal rather than an empty floor.
    pos, target, lens = (3.10, -1.55, 1.70), (1.48, 1.80, .20), 29

if chapter == 12:
    # Replace nine separated spherical beads with a continuous tapered,
    # lightly ribbed mesh that can contract and extend organically.
    for ob in bpy.data.objects:
        if ob.name.startswith("V6.1 growing larva segment"):
            ob.hide_render = True
    rings, sides = 65, 20
    verts, faces = [], []
    for i in range(rings):
        t = i / (rings - 1)
        radius = .013 + .096 * (math.sin(math.pi * t) ** .65)
        radius *= 1.0 - .105 * (math.sin(t * 9 * math.pi) ** 10)
        for j in range(sides):
            a = 2 * math.pi * j / sides
            verts.append((.035 + radius * math.cos(a),
                          -.12 + .72 * t,
                          .75 + .014 * math.sin(math.pi * t) +
                          .82 * radius * math.sin(a)))
    for i in range(rings - 1):
        for j in range(sides):
            faces.append((i * sides + j,
                          i * sides + (j + 1) % sides,
                          (i + 1) * sides + (j + 1) % sides,
                          (i + 1) * sides + j))
    faces.append(tuple(reversed(range(sides))))
    faces.append(tuple((rings - 1) * sides + j for j in range(sides)))
    larva_mesh = bpy.data.meshes.new("V6.7.1 continuous larva mesh")
    larva_mesh.from_pydata(verts, [], faces)
    larva_mesh.update()
    larva_body = bpy.data.objects.new("V6.7.1 continuous crawling larva", larva_mesh)
    scene.collection.objects.link(larva_body)
    larva_body.parent = roach
    larva_body.data.materials.append(
        organic_material("V6.7.1 warm larval cuticle",
                         (.28, .19, .105), (.66, .51, .29), 9, .78))
    for polygon in larva_mesh.polygons:
        polygon.use_smooth = True
    larva_body.shape_key_add(name="Basis")
    wave_a = larva_body.shape_key_add(name="Peristalsis A")
    wave_b = larva_body.shape_key_add(name="Peristalsis B")
    for key, phase in ((wave_a, 0.0), (wave_b, math.pi)):
        for index, vertex in enumerate(key.data):
            t = (index // sides) / (rings - 1)
            x, y, z = verts[index]
            bulge = 1 + .16 * math.sin(t * 4 * math.pi + phase)
            vertex.co = (x + (x - .035) * (bulge - 1),
                         y + .020 * math.sin(t * 3 * math.pi + phase),
                         .75 + (z - .75) * bulge)
    for frame in (90, 98, 106, 114, 122, 130, 138, 154, 180, 210, 240):
        wave_a.value = .5 + .5 * math.sin(frame * .24)
        wave_b.value = 1 - wave_a.value
        wave_a.keyframe_insert(data_path="value", frame=frame)
        wave_b.keyframe_insert(data_path="value", frame=frame)
    pos, target, lens = (1.88, -.65, 1.55), (1.53, 1.20, .77), 42

scene.frame_set(120)

# V6.7.2 corrections from actual V6.7.1 4-still/4-motion review:
# technical pass but no legible sting, no credible burrow entry, oval larva.
if chapter in (3, 5):
    shaft = bpy.data.objects.get("V6.7 world-space extending ovipositor")
    if shaft:
        copper = mat("V6.7.2 visible amber ovipositor", (.47,.21,.055),.35,.30)
        shaft.data.materials.clear()
        shaft.data.materials.append(copper)
        # Thicken actual taper mesh, not an overlay, for 540x960 visibility.
        for vertex in shaft.data.vertices:
            vertex.co.x *= 1.9
            vertex.co.y *= 1.9
    near = 1 if chapter == 3 else -1
    mark = bpy.data.objects.get("V6.7 roach flank entry")
    if mark:
        mark.location = (-.24,-.58 if chapter==3 else -.83,.73)
    # Compose around the actual evaluated needle endpoints.
    scene.frame_set(114)
    a = wasp.matrix_world @ Vector((0,.97,.36))
    b = roach.matrix_world @ Vector((-.24,-.58 if chapter==3 else -.83,.73))
    mid = (a+b)*.5
    pos = tuple(mid + Vector((near*1.8,-2.65,.86)))
    target = tuple(mid)
    lens = 32

if chapter == 10:
    # Previous shot shows a disconnected gray ring, not a recessed tunnel.
    for ob in bpy.data.objects:
        if ob.name.startswith(("V6.2 visible dark burrow mouth",
          "V6.2 irregular low earth lip", "V6.6 excavated earth mound",
          "V6.6 vertical shadowed tunnel entrance",
          "V6.6 uneven arched earthen rim", "V6.7 asymmetric excavated rim")):
            ob.hide_render = True
    earth = organic_material("V6.7.2 compacted forest soil",
        (.027,.021,.013),(.12,.071,.034),16,.97)
    hole = mat("V6.7.2 deep dark tunnel",(.001,.001,.001),0,.98)
    ell("V6.7.2 integrated mound",(1.48,2.61,.30),(.96,.68,.46),earth)
    ell("V6.7.2 recessed opening",(1.48,2.02,.32),(.52,.034,.34),hole)
    for i in range(23):
        angle=math.pi*i/22
        x=1.48+(.56+.025*math.sin(i*2.3))*math.cos(angle)
        z=.30+(.38+.02*math.cos(i*1.7))*math.sin(angle)
        ell("V6.7.2 broken soil lip",(x,1.99,z),
            (.053,.071,.047),earth)
    roach.animation_data_clear()
    for frame,p in ((1,(.40,-.45,.03)),(185,(1.44,1.03,.03)),
        (200,(1.48,1.28,.01)),(210,(1.48,1.49,-.06)),
        (220,(1.48,1.77,-.20)),(230,(1.48,2.05,-.36)),
        (240,(1.48,2.38,-.56))):
        roach.location=p
        roach.rotation_euler=(0,0,math.pi)
        roach.keyframe_insert(data_path="location",frame=frame)
        roach.keyframe_insert(data_path="rotation_euler",frame=frame)
    pos,target,lens=(2.85,-1.7,1.65),(1.48,1.97,.34),30

if chapter == 12:
    larva=bpy.data.objects.get("V6.7.1 continuous crawling larva")
    if larva:
        larva.scale=(.91,.91,.91)
        for frame,y in ((1,-.03),(90,-.03),(95,-.025),
                        (105,.015),(115,.055),(125,.095),
                        (135,.12),(160,.15),(240,.19)):
            larva.location=(.012*math.sin(frame*.22),y,
                            .012*math.sin(frame*.16))
            larva.keyframe_insert(data_path="location",frame=frame)
        skin=organic_material("V6.7.2 cream larval cuticle",
            (.34,.27,.16),(.81,.72,.52),15,.79)
        larva.data.materials.clear()
        larva.data.materials.append(skin)
        dots=mat("V6.7.2 spiracle pigment",(.12,.07,.035),0,.84)
        folds=mat("V6.7.2 subtle larval folds",(.35,.27,.17),0,.87)
        for i in range(1,9):
            t=i/9
            r=.013+.096*math.sin(math.pi*t)**.65
            y=-.12+.72*t
            for side in (-1,1):
                ell("V6.7.2 lateral spiracle",
                    (.035+side*r*.88,y,.77),
                    (.007,.009,.005),dots,larva)
            if i<8:
                ell("V6.7.2 dorsal cuticle fold",
                    (.035,y,.75+r*.78),
                    (r*.74,.006,.005),folds,larva)
    pos,target,lens=(1.92,-.92,1.62),(1.52,1.16,.77),39

# V6.7.3: evidence-led framing fix after independently viewing run 40831728886.
# V6.7.2 stills cropped both sting actors; do not crop the actual needle to
# create an artificial close-up. This changes composition, not anatomy.
if chapter in (3, 5):
    scene.frame_set(114)
    anchor = wasp.matrix_world @ Vector((0, 1.0, .37))
    contact_world = roach.matrix_world @ Vector(
        (-.24, -.58 if chapter == 3 else -.83, .73))
    center = (anchor + contact_world) * .5
    # Opposite viewing sides keep the two stings compositionally distinct.
    side = 1 if chapter == 3 else -1
    pos = tuple(center + Vector((side * 2.65, -4.65, 1.90)))
    target = tuple(center)
    lens = 24

if chapter == 12:
    scene.frame_set(120)
    # Frame the living larva rather than the entire cockroach wing cover.
    larva_center = roach.matrix_world @ Vector((.035, .25, .78))
    pos = tuple(larva_center + Vector((1.20, -1.48, .95)))
    target = tuple(larva_center)
    lens = 56
    larva = bpy.data.objects.get("V6.7.1 continuous crawling larva")
    if larva and larva.data.shape_keys:
        keys = larva.data.shape_keys.key_blocks
        basis = keys.get("Basis")
        if basis:
            for key in keys:
                if key.name == "Basis":
                    continue
                # Increase visible cuticle deformation without separating
                # body segments or replacing the continuous surface.
                for base_point, animated_point in zip(basis.data, key.data):
                    animated_point.co = base_point.co + (
                        animated_point.co - base_point.co) * 1.7

scene.frame_set(120)

# V6.7.4 focused: actual 40844741407 evidence review; keep V4 untouched.
if chapter in (3, 5):
    # The old needle spans an implausibly large gap. Stage a shorter,
    # posterior-to-flank insertion with two clearly separated views.
    wx, wy = (-.59, -1.56) if chapter == 3 else (.58, -1.73)
    hx, hy = (-.24, -.58) if chapter == 3 else (.24, -.83)
    wasp.animation_data_clear()
    for f, z in ((1,.70),(90,.68),(102,.63),(114,.59),
                 (126,.60),(145,.67),(240,.70)):
        wasp.location = (wx,wy,z)
        wasp.rotation_euler = (0,0,0)
        wasp.keyframe_insert(data_path="location",frame=f)
        wasp.keyframe_insert(data_path="rotation_euler",frame=f)
    shaft = bpy.data.objects.get("V6.7 world-space extending ovipositor")
    tip = bpy.data.objects.get("V6.7 sting needle tip")
    mark = bpy.data.objects.get("V6.7 roach flank entry")
    if not shaft or not tip:
        raise RuntimeError("Missing sting objects")
    shaft.animation_data_clear()
    tip.animation_data_clear()
    for f, reach in ((1,.02),(90,.02),(96,.15),(102,.47),
                     (108,.85),(114,1.0),(120,1.0),
                     (126,.62),(138,.06),(160,.02),(240,.02)):
        scene.frame_set(f)
        base = wasp.matrix_world @ Vector((0,1.0,.37))
        hit = roach.matrix_world @ Vector((hx,hy,.73))
        endpoint = base.lerp(hit,reach)
        delta = endpoint-base
        shaft.location = (base+endpoint)*.5
        shaft.rotation_euler = delta.to_track_quat('Z','Y').to_euler()
        shaft.scale = (.50,.50,max(.003,delta.length))
        tip.location = endpoint
        tip.scale = (.013,.013,.013)
        for prop in ("location","rotation_euler","scale"):
            shaft.keyframe_insert(data_path=prop,frame=f)
        tip.keyframe_insert(data_path="location",frame=f)
        tip.keyframe_insert(data_path="scale",frame=f)
    if mark:
        mark.location = (hx,hy,.73)
    scene.frame_set(114)
    base = wasp.matrix_world @ Vector((0,1.0,.37))
    hit = roach.matrix_world @ Vector((hx,hy,.73))
    center = (base+hit)*.5
    side = 1 if chapter == 3 else -1
    pos = tuple(center + Vector((side*2.7,-4.05,1.75)))
    target = tuple(center)
    lens = 27

if chapter == 12:
    # No detached white protruding 'folds': sculpt grooves into the
    # continuous 65-ring mesh and mute the chalk-white cuticle.
    for ob in bpy.data.objects:
        if ob.name.startswith("V6.7.2 dorsal cuticle fold"):
            ob.hide_render = True
        elif ob.name.startswith("V6.7.2 lateral spiracle"):
            ob.scale = tuple(v*.45 for v in ob.scale)
    larva = bpy.data.objects.get("V6.7.1 continuous crawling larva")
    if not larva or not larva.data.shape_keys:
        raise RuntimeError("Missing animated continuous larva")
    skin = organic_material("V6.7.4 muted larval cuticle",
                            (.38,.28,.16),(.67,.54,.36),19,.86)
    larva.data.materials.clear()
    larva.data.materials.append(skin)
    scene.frame_set(120)
    center = roach.matrix_world @ Vector((.035,.25,.78))
    pos = tuple(center + Vector((1.35,-1.65,.90)))
    target = tuple(center)
    lens = 51
scene.frame_set(120)
