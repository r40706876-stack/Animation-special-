"""Isolated V6.7 focused proof; V6.6 source and completed artifacts untouched.

Inject the new action pass just before the final V6 camera keyframes and render.
The canonical V6 proof remains the source of all original scene setup.
"""
import pathlib

source = pathlib.Path(__file__).with_name("jewel_wasp_v6_proof.py")
code = source.read_text()
boundary = "\ncam.animation_data_clear()\n"
assert code.count(boundary) == 1, "V6 camera boundary changed; review before rendering"
injection = """
_v67 = pathlib.Path(__file__).with_name("jewel_wasp_v67_focus_pass.py")
exec(compile(_v67.read_text(),str(_v67),"exec"),globals())
"""
code = code.replace(boundary, "\n"+injection+boundary)
# For the burrow, inspect actual entry at the end of the shot, not the approach.
old_motion = "scene.frame_start=48 if chapter==0 else (90 if chapter in (3,5) else (185 if chapter==10 else (95 if chapter==12 else 1)))"
assert code.count(old_motion)==1, "V6 motion timing changed"
code = code.replace(old_motion, "scene.frame_start=(210 if chapter==10 else (90 if chapter in (3,5) else (95 if chapter==12 else 48)))")
ctx = {"__name__":"__main__","__file__":str(source)}
exec(compile(code,str(source),"exec"),ctx)
