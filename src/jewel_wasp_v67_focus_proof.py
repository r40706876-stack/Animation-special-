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
ctx = {"__name__":"__main__","__file__":str(source)}
exec(compile(code,str(source),"exec"),ctx)
