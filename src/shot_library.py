"""Reusable directed 9:16 Blender story shots and camera-locked typography.

Each five-second chapter has its own framing and choreography. Titles are
parented to the camera, so they stay readable during pans and close-ups.
"""
import math
import bpy
from mathutils import Vector

SHOT_TITLES = [
    ("MEET OLLIE", "A curious ocean explorer"),
    ("EIGHT ARMS", "One incredible swimmer"),
    ("OCEAN HELLO!", "Blink and say hi"),
    ("REEF ADVENTURE", "Gliding through the blue"),
    ("KEEP EXPLORING", "The ocean is full of wonder"),
]

# The face close-up intentionally crops the arms; wide shots show all eight.
# (orthographic scale, camera start X, camera end X, camera height, target Z,
#  rig start X, rig end X, start yaw, end yaw)
SHOT_PLANS = [
    (8.7, -.32, .10, 5.7, 1.55, -.16, .08, -.08, .08),
    (7.7, .30, -.22, 5.3, 1.30, .16, -.14, .18, -.20),
    (5.9, -.12, .12, 4.6, 1.47, -.08, .08, -.09, .09),
    (8.0, -.48, .52, 5.8, 1.55, -.35, .38, -.18, .20),
    (8.9, .32, -.22, 5.9, 1.55, .10, -.10, .18, -.08),
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

    title, subtitle = SHOT_TITLES[index]
    _camera_text("Story title", title, camera, True, .073, (.94, .99, 1.0))
    _camera_text("Story caption", subtitle, camera, False, .040, (.72, .95, 1.0))
    scene.frame_start = 1
    scene.frame_end = 120
    scene.frame_set(1)
    print("STORY_SHOT_READY", index, title, "scale", scale)
