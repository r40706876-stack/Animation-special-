"""V6 full 10-second chapter render. Run only after visual/motion proof approval.
Reuses the exact V6 proof scene construction but replaces the proof render tail.
Does not mutate the verified V4 film or any previous artifact.
"""
import os
import pathlib
import bpy

source = pathlib.Path(__file__).with_name("jewel_wasp_v6_proof.py")
code = source.read_text()
# Use the same V6.7 action correction as the reviewed focused proof.
# Without this insertion the approved full render would silently use stale V6
# sting, burrow and larva scenes even if the focused V6.7 proof looked good.
camera_boundary = "\ncam.animation_data_clear()\n"
assert code.count(camera_boundary) == 1, "V6 camera injection point changed"
injection = """
_v67 = pathlib.Path(__file__).with_name("jewel_wasp_v67_focus_pass.py")
exec(compile(_v67.read_text(), str(_v67), "exec"), globals())
"""
code = code.replace(camera_boundary, "\n" + injection + camera_boundary)
boundary = 'motion=os.getenv("V6_MOTION","0")=="1"'
assert code.count(boundary) == 1, "V6 proof render boundary changed; review required"
ctx = {"__name__": "__main__", "__file__": str(source)}
exec(compile(code.split(boundary)[0], str(source), "exec"), ctx)

scene = ctx["scene"]
chapter = ctx["chapter"]
assert 0 <= chapter < 14
assert os.getenv("V6_FULL_APPROVED") == "YES", (
    "V6 full render blocked until visual and motion proof approval"
)
scene.frame_start = 1
scene.frame_end = 240
scene.render.fps = 24
scene.render.resolution_x = 540
scene.render.resolution_y = 960
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "FFMPEG"
scene.render.ffmpeg.format = "MPEG4"
scene.render.ffmpeg.codec = "H264"
scene.render.filepath = os.environ["BLENDER_OUTPUT"]
print("JEWEL_V6_FULL_START", chapter, scene.render.filepath, flush=True)
bpy.ops.render.render(animation=True)
print("JEWEL_V6_FULL_DONE", chapter, flush=True)
