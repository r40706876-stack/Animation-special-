"""Reusable story-event props and animation for five distinct underwater shots.

All objects are generated procedurally with Blender primitives; no paid assets.
Coordinates are in the common underwater stage, camera facing toward +Y.
"""
import math
import bpy


def material(name, color, glow=0):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    bs = m.node_tree.nodes.get("Principled BSDF")
    bs.inputs["Base Color"].default_value = (*color, 1)
    bs.inputs["Roughness"].default_value = .32
    if glow:
        em = bs.inputs.get("Emission Color") or bs.inputs.get("Emission")
        if em is not None:
            em.default_value = (*color, 1)
        strength = bs.inputs.get("Emission Strength")
        if strength is not None:
            strength.default_value = glow
    return m


def sphere(name, pos, scale, mat, parent=None):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=20, ring_count=12, location=pos)
    ob = bpy.context.object
    ob.name = name
    ob.scale = scale
    ob.data.materials.append(mat)
    bpy.ops.object.shade_smooth()
    if parent is not None:
        ob.parent = parent
        ob.matrix_parent_inverse.identity()
    return ob


def controller(name):
    root = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(root)
    return root


def animate(root, keys):
    """keys: frame, x, y, z, yaw; coordinates remain world-stage positions."""
    for frame, x, y, z, yaw in keys:
        root.location = (x, y, z)
        root.rotation_euler.z = yaw
        root.keyframe_insert(data_path="location", frame=frame)
        root.keyframe_insert(data_path="rotation_euler", index=2, frame=frame)
    if root.animation_data and root.animation_data.action:
        for fc in root.animation_data.action.fcurves:
            for kp in fc.keyframe_points:
                kp.interpolation = "BEZIER"


def make_pearl(name="Magic pearl"):
    root = controller(name + " controller")
    pearl_mat = material(name + " ivory", (.72, .97, 1.0), 2.5)
    sphere(name, (0, 0, 0), (.19, .19, .19), pearl_mat, root)
    ring_mat = material(name + " halo", (.08, .65, 1.0), 1.8)
    bpy.ops.mesh.primitive_torus_add(major_radius=.28, minor_radius=.012,
                                    location=(0, 0, 0))
    ring = bpy.context.object
    ring.name = name + " luminous halo"
    ring.rotation_euler.x = math.pi / 2
    ring.data.materials.append(ring_mat)
    ring.parent = root
    ring.matrix_parent_inverse.identity()
    return root


def make_fish():
    root = controller("Reusable golden reef fish rig")
    gold = material("Fish golden body", (1.0, .52, .07))
    fin = material("Fish orange fins", (1.0, .22, .10))
    eye = material("Fish dark eye", (.01, .03, .06))
    sphere("Fish body", (0, 0, 0), (.43, .20, .25), gold, root)
    sphere("Fish left eye", (.27, -.187, .075), (.055, .034, .06), eye, root)
    sphere("Fish right eye", (.27, .187, .075), (.055, .034, .06), eye, root)
    # Triangle tail: a real mesh rather than separate spheres.
    mesh = bpy.data.meshes.new("Fish tail mesh")
    mesh.from_pydata([(-.35,0,0),(-.76,0,.32),(-.76,0,-.32),
                      (-.35,.04,0),(-.76,.04,.32),(-.76,.04,-.32)], [],
                     [(0,1,2),(3,5,4),(0,3,4,1),(1,4,5,2),(2,5,3,0)])
    mesh.update()
    tail = bpy.data.objects.new("Fish forked tail", mesh)
    bpy.context.collection.objects.link(tail)
    tail.data.materials.append(fin)
    tail.parent = root
    bpy.ops.mesh.primitive_cone_add(vertices=3, radius1=.22, radius2=0,
                                    depth=.38, location=(-.05,0,.22))
    dorsal = bpy.context.object
    dorsal.name = "Fish dorsal fin"
    dorsal.data.materials.append(fin)
    dorsal.parent = root
    dorsal.matrix_parent_inverse.identity()
    return root


def sparkle_field(index):
    glow = material("Reusable sparkle blue", (.18, .82, 1), 2.2)
    for i in range(12):
        angle = i * math.tau / 12
        radius = .50 + .16 * (i % 3)
        ob = sphere("Celebration sparkle %02d" % i,
                    (radius * math.cos(angle), -.9,
                     1.4 + radius * math.sin(angle)),
                    (.035, .035, .035), glow)
        for frame, scale in ((1, .01), (25, 1), (55, .15),
                             (85, 1), (120, .01)):
            ob.scale = (.035 * scale,) * 3
            ob.keyframe_insert(data_path="scale", frame=frame)


def add_story_event(scene, index):
    """Add a clear visual event to each chapter; avoid five identical swims."""
    if index == 0:
        pearl = make_pearl("Discovered pearl")
        animate(pearl, [(1, 1.35, -.7, -.15, 0),
                        (45, 1.22, -.7, .65, 0),
                        (90, 1.05, -.7, 1.15, 0),
                        (120, 1.00, -.7, 1.35, 0)])
    elif index == 1:
        fish = make_fish()
        animate(fish, [(1, -2.4, -.85, 1.75, 0),
                       (45, -.7, -.85, 1.45, -.10),
                       (80, .9, -.85, 1.15, -.16),
                       (120, 2.5, -.85, 1.85, .18)])
        pearl = make_pearl("Stolen pearl")
        animate(pearl, [(1, 1.12, -.75, 1.05, 0),
                        (70, 1.12, -.75, 1.05, 0),
                        (90, 1.55, -.75, 1.27, 0),
                        (120, 2.12, -.75, 1.73, 0)])
    elif index == 2:
        fish = make_fish()
        animate(fish, [(1, 2.15, -.85, 1.55, math.pi),
                       (40, 1.10, -.85, 1.75, math.pi),
                       (85, -.7, -.85, 1.25, math.pi),
                       (120, -2.2, -.85, 1.65, math.pi)])
        pearl = make_pearl("Chased pearl")
        animate(pearl, [(1, 1.55, -.8, 1.40, 0),
                        (40, .5, -.8, 1.60, 0),
                        (85, -1.3, -.8, 1.10, 0),
                        (120, -2.8, -.8, 1.5, 0)])
    elif index == 3:
        fish = make_fish()
        animate(fish, [(1, 2.1, -.9, 1.55, math.pi),
                       (65, 1.12, -.9, 1.25, math.pi),
                       (120, 1.25, -.9, 1.35, math.pi)])
        pearl = make_pearl("Returned pearl")
        animate(pearl, [(1, 1.55, -.95, 1.38, 0),
                        (45, 1.0, -.95, 1.25, 0),
                        (90, .28, -.95, 1.12, 0),
                        (120, .16, -.95, 1.3, 0)])
    elif index == 4:
        fish = make_fish()
        animate(fish, [(1, 1.55, -.9, 1.35, math.pi),
                       (60, 1.12, -.9, 1.75, math.pi),
                       (120, 1.55, -.9, 1.35, math.pi)])
        pearl = make_pearl("Friendship pearl")
        animate(pearl, [(1, .60, -.85, .95, 0),
                        (60, .60, -.85, 1.45, 0),
                        (120, .60, -.85, .95, 0)])
        sparkle_field(index)
    else:
        raise ValueError("Unknown story event: %s" % index)
    scene.frame_set(1)
    print("STORY_EVENT_READY", index)
