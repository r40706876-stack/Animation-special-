"""Render one five-second chapter of a reusable 25-second 3D story.

Run with:
  STORY_SHOT=0 BLENDER_OUTPUT=/tmp/story_00.mp4 blender -b -t 2 --python src/blender_story.py
"""
import os
import runpy
import sys

here = os.path.dirname(os.path.abspath(__file__))
if here not in sys.path:
    sys.path.insert(0, here)

# Build the shared octopus character, animation rig and underwater world.
# The base demo explicitly supports scene-only construction.
os.environ["BLENDER_BUILD_ONLY"] = "1"
runpy.run_path(os.path.join(here, "blender_octopus_demo.py"), run_name="__main__")

import bpy
from shot_library import apply_story_shot, SHOT_TITLES

index = int(os.environ.get("STORY_SHOT", "0"))
apply_story_shot(bpy.context.scene, index)
output = os.environ.get("BLENDER_OUTPUT", "/tmp/octopus_story_%02d.mp4" % index)
bpy.context.scene.render.filepath = output
bpy.context.scene.render.resolution_x = 540
bpy.context.scene.render.resolution_y = 960
bpy.context.scene.render.resolution_percentage = 100
bpy.context.scene.render.fps = 24
bpy.ops.render.render(animation=True)
print("STORY_SEGMENT_RENDER_COMPLETE", index, output, SHOT_TITLES[index][0])
