"""Reusable directed 9:16 Blender story shots and camera-locked typography.

Each five-second chapter has its own framing and choreography. Titles are
parented to the camera, so they stay readable during pans and close-ups.
"""
import math
import bpy
from mathutils import Vector

SHOT_TITLES = [
    ("A MAGIC PEARL!", "Ollie finds an ocean treasure"),
    ("HEY! MY PEARL!", "A cheeky fish steals the glow"),
    ("THE CHASE!", "Catch that speedy little fish"),
    ("A SURPRISE...", "The fish returns the pearl"),
    ("BEST FRIENDS!", "A new friendship begins"),
]

# The face close-up intentionally crops the arms; wide shots show all eight.
# (orthographic scale, camera start X, camera end X, camera height, target Z,
#  rig start X, rig end X, start yaw, end yaw)
# Camera zoom progression per five-second story beat. Orthographic scale is
# animated, not held static, so each chapter has a purposeful push or pull.
SHOT_ZOOMS = [
    (1.08, 1.00, .92),  # discover: push toward the pearl
    (.94, 1.02, 1.12),  # theft: reveal the fish's getaway
    (.90, 1.04, 1.18),  # chase: open up the playing field
    (1.12, 1.00, .92),  # return: focus on the reveal
    (1.04, .97, .90),  # friends: warm final push-in
]

SHOT_PLANS = [
    (7.2, -.25, .15, 5.5, 1.40, -.16, .08, -.08, .08),
    (6.1, .38, -.24, 4.9, 1.35, .16, -.14, .18, -.20),
    (8.0, .48, -.65, 5.7, 1.47, .30, -.65, -.09, -.28),
    (6.5, -.45, .28, 5.0, 1.40, -.35, .20, -.18, .12),
    (7.0, .20, -.16, 5.2, 1.45, .10, -.10, .18, -.08),
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
    zooms = SHOT_ZOOMS[index]
    for key_index, (frame, fraction) in enumerate(((1, 0.0), (61, .5), (120, 1.0))):
        camera.data.ortho_scale = scale * zooms[key_index]
        camera.data.keyframe_insert(data_path="ortho_scale", frame=frame)
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
    _camera_text("Story title", title, camera, True, .080, (.94, .99, 1.0))
    _camera_text("Story caption", subtitle, camera, False, .057, (.72, .95, 1.0))
    scene.frame_start = 1
    scene.frame_end = 120
    scene.frame_set(1)
    print("STORY_SHOT_READY", index, title, "scale", scale)
