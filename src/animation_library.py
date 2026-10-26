"""Reusable Blender keyframe helpers for cartoon characters and environmental motion."""
import math
from mathutils import Vector

def animate_character_float(bpy, objects, name="Octopus Rig"):
    """Parent a model's meshes to a reusable motion controller."""
    root=bpy.data.objects.new(name,None)
    bpy.context.collection.objects.link(root)
    for obj in objects:
        if obj.type=="MESH":
            obj.parent=root
    for frame,z,yaw in [(1,0,0),(31,.09,.035),(61,.16,0),(91,.07,-.035),(120,0,0)]:
        root.location.z=z
        root.rotation_euler[2]=yaw
        root.keyframe_insert(data_path="location",frame=frame)
        root.keyframe_insert(data_path="rotation_euler",frame=frame)
    return root

def animate_rising_bubble(bubble,index):
    start=bubble.location.copy()
    for frame in (1,60,120):
        bubble.location=start+Vector((.09*math.sin(frame*.045+index),0,.65*(frame-1)/119))
        bubble.keyframe_insert(data_path="location",frame=frame)
