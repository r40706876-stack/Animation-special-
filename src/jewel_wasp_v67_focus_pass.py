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
