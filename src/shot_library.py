"""Reusable directed 9:16 Blender story shots and camera-locked typography.

Each five-second chapter has its own framing and choreography. Titles are
parented to the camera, so they stay readable during pans and close-ups.
"""
import math
import bpy
from mathutils import Vector

SHOT_TITLES = [
    ("WHAT IS THAT?", "A mysterious glow appears"),
    ("FOLLOW THE LIGHT", "Ollie spots a strange pearl"),
    ("OH NO!", "A shadow blocks the treasure"),
    ("QUICK ESCAPE!", "Eight arms spring into action"),
    ("THE BIG REVEAL", "A tiny glowing ocean friend!"),
]

# The face close-up intentionally crops the arms; wide shots show all eight.
# (orthographic scale, camera start X, camera end X, camera height, target Z,
#  rig start X, rig end X, start yaw, end yaw)
SHOT_PLANS = [
    (7.4, -.32, .10, 5.7, 1.40, -.16, .08, -.08, .08),
    (7.3, .30, -.22, 5.3, 1.35, .16, -.14, .18, -.20),
    (7.6, -.12, .12, 5.3, 1.47, -.08, .08, -.09, .09),
    (7.2, -.48, .52, 5.8, 1.40, -.35, .38, -.18, .20),
    (7.4, .32, -.22, 5.9, 1.45, .10, -.10, .18, -.08),
]

def _camera_text(name, message, camera, top, size_fraction, color):
    """3D type at a fixed camera-relative screen position (not world-space)."""
    material = bpy.data.materials.new(name + " material")
    material.diffuse_color = (*color, 1)
    material.use_nodes = True
    bsdf = material.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*color, 1)
    emission = bsdf.inputs.get("Emission Color") or bsdf.inputs.get("Emission")
    if emission is not None:
        emission.default_value = (*color, 1)
    strength = bsdf.inputs.get("Emission Strength")
    if strength is not None:
        strength.default_value = 1.4
    curve = bpy.data.curves.new(name, "FONT")
    curve.body = message
    screen_width = camera.data.ortho_scale * 540 / 960
    curve.size = screen_width * size_fraction
    curve.extrude = .002
    obj = bpy.data.objects.new(name, curve)
    bpy.context.collection.objects.link(obj)
    obj.parent = camera
    obj.location = (-.41 * screen_width,
                    (.38 if top else -.40) * camera.data.ortho_scale,
                    -3.0)
    obj.rotation_euler = (0, 0, 0)
    obj.data.materials.append(material)
    return obj

def _story_prop(name, location, radius, material_color, emission=0):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=12, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.scale = (radius, radius, radius)
    bpy.ops.object.shade_smooth()
    mat = bpy.data.materials.new(name + " glow")
    mat.use_nodes = True
    shader = mat.node_tree.nodes.get("Principled BSDF")
    shader.inputs["Base Color"].default_value = (*material_color, 1)
    glow = shader.inputs.get("Emission Color") or shader.inputs.get("Emission")
    if glow is not None:
        glow.default_value = (*material_color, 1)
    strength = shader.inputs.get("Emission Strength")
    if strength is not None:
        strength.default_value = emission
    obj.data.materials.append(mat)
    return obj

def _animate_prop(obj, frames):
    for frame, xyz, scale in frames:
        obj.location = xyz
        obj.scale = (scale, scale, scale)
        obj.keyframe_insert(data_path="location", frame=frame)
        obj.keyframe_insert(data_path="scale", frame=frame)

def apply_story_shot(scene, index):
    """Direct one distinct chapter with reusable camera, rig and titles."""
    if index not in range(len(SHOT_TITLES)):
        raise ValueError("Invalid story shot: %s" % index)
    camera = scene.camera
    rig = bpy.data.objects.get("Octopus Rig")
    if camera is None or rig is None:
        raise RuntimeError("Base octopus scene has no camera or motion rig")
    scale, camera_start, camera_end, height, target_z, x_start, x_end, yaw_start, yaw_end = SHOT_PLANS[index]
    camera.data.ortho_scale = scale
    for frame, fraction in ((1, 0.0), (61, .5), (120, 1.0)):
        camera.location = (camera_start + (camera_end - camera_start) * fraction,
                           -8.0, height)
        aim = Vector((0, 0, target_z)) - camera.location
        camera.rotation_euler = aim.to_track_quat("-Z", "Y").to_euler()
        camera.keyframe_insert(data_path="location", frame=frame)
        camera.keyframe_insert(data_path="rotation_euler", frame=frame)
    # Match the five base animation keys to avoid stray interpolation keys.
    # Only X and yaw are changed: the original Z bobbing is preserved.
    for frame in (1, 31, 61, 91, 120):
        fraction = (frame - 1) / 119
        rig.location.x = x_start + (x_end - x_start) * fraction
        rig.rotation_euler.z = yaw_start + (yaw_end - yaw_start) * fraction
        rig.keyframe_insert(data_path="location", index=0, frame=frame)
        rig.keyframe_insert(data_path="rotation_euler", index=2, frame=frame)

    # Story beats: visible event/action in each shot, not just changing headings.
    if index in (0, 1, 2, 3, 4):
        pearl = _story_prop("Mysterious luminous pearl", (1.0, -1.8, 1.1), .22, (.06, .86, 1.0), 3.0)
        pearl_paths = [
            [(1,(3.4,-1.8,1.2),.06),(61,(1.4,-1.8,1.2),.20),(120,(.95,-1.8,1.35),.27)],
            [(1,(1.5,-1.8,1.2),.22),(61,(.55,-1.8,1.5),.30),(120,(-.35,-1.8,1.7),.24)],
            [(1,(.0,-1.8,1.6),.27),(61,(.0,-1.8,1.2),.18),(120,(1.6,-1.8,1.2),.14)],
            [(1,(-.4,-1.8,1.0),.26),(61,(1.3,-1.8,2.3),.20),(120,(3.2,-1.8,3.2),.08)],
            [(1,(2.0,-1.8,1.2),.12),(61,(.9,-1.8,1.8),.28),(120,(.15,-1.8,1.6),.32)],
        ]
        _animate_prop(pearl, pearl_paths[index])
    if index == 2:
        shadow = _story_prop("Sudden looming shadow", (1.0, -2.5, 1.4), .5, (.025,.035,.12))
        _animate_prop(shadow, [(1,(3.5,-2.5,1.4),.15),(61,(1.2,-2.5,1.5),.85),(120,(.3,-2.5,1.5),1.1)])
    if index == 3:
        for frame, fraction in ((1,0.0),(31,.08),(61,.40),(91,.78),(120,1.0)):
            rig.location.x = -1.1 + 3.1*fraction
            rig.location.z = .12 + .48*fraction
            rig.rotation_euler.z = -.2 + .65*fraction
            rig.keyframe_insert(data_path="location",frame=frame)
            rig.keyframe_insert(data_path="rotation_euler",frame=frame)
    if index == 4:
        friend = _story_prop("Tiny friendly sea creature", (1.7,-1.6,1.45), .17, (1.0,.62,.18), 2.0)
        _animate_prop(friend, [(1,(2.7,-1.6,1.2),.07),(61,(1.1,-1.6,1.55),.19),(120,(.6,-1.6,1.85),.24)])

    title, subtitle = SHOT_TITLES[index]
    _camera_text("Story title", title, camera, True, .073, (.94, .99, 1.0))
    _camera_text("Story caption", subtitle, camera, False, .040, (.72, .95, 1.0))
    scene.frame_start = 1
    scene.frame_end = 120
    scene.frame_set(1)
    print("STORY_SHOT_READY", index, title, "scale", scale)
