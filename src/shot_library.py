"""Reusable shot choreography and camera framing for 9:16 Blender stories."""
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

def _text(name, message, position, size, color):
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
        strength.default_value = 1.2
    curve = bpy.data.curves.new(name, "FONT")
    curve.body = message
    curve.size = size
    curve.extrude = 0.004
    curve.bevel_depth = 0.002
    obj = bpy.data.objects.new(name, curve)
    bpy.context.collection.objects.link(obj)
    obj.location = position
    obj.rotation_euler = (math.radians(66), 0, 0)
    obj.data.materials.append(material)
    return obj

def apply_story_shot(scene, index):
    """Use one rig and environment with five independently directed shots."""
    if index not in range(len(SHOT_TITLES)):
        raise ValueError("Invalid story shot: %s" % index)
    title, subtitle = SHOT_TITLES[index]
    camera = scene.camera
    rig = bpy.data.objects.get("Octopus Rig")
    if camera is None or rig is None:
        raise RuntimeError("Base octopus scene has no camera or motion rig")

    # Stable full-body framing. Camera pans and modest variations add direction
    # without cropping tentacles in the narrow portrait frame.
    offsets = [(-.18, 0.0), (.12, -.10), (0.0, .06), (.22, -.10), (-.12, .04)]
    cx, cy = offsets[index]
    camera.data.ortho_scale = [8.8, 8.7, 8.45, 8.9, 8.8][index]
    for frame, delta in ((1, -.12), (60, .10), (120, -.12)):
        camera.location = (cx + delta, -8.0, 6.0 + cy)
        aim = Vector((0, 0, 1.55)) - camera.location
        camera.rotation_euler = aim.to_track_quat("-Z", "Y").to_euler()
        camera.keyframe_insert(data_path="location", frame=frame)
        camera.keyframe_insert(data_path="rotation_euler", frame=frame)

    # Root animation is independent of the environmental objects.
    shifts = [(-.12, .12), (.12, -.12), (0, 0), (-.22, .22), (.10, -.10)]
    start, end = shifts[index]
    for frame, x in ((1, start), (60, (start+end)/2), (120, end)):
        rig.location.x = x
        rig.rotation_euler[2] = .05 * math.sin(index + frame/30)
        rig.keyframe_insert(data_path="location", frame=frame)
        rig.keyframe_insert(data_path="rotation_euler", frame=frame)

    # Text is placed as actual 3D typography, not burned into a static image.
    _text("Story title", title, (-1.72, -2.8, 3.95), .38, (.91, .98, 1.0))
    _text("Story caption", subtitle, (-1.72, -2.8, -.73), .20, (.72, .94, 1.0))
    scene.frame_start = 1
    scene.frame_end = 120
    scene.frame_set(1)
    print("STORY_SHOT_READY", index, title)
