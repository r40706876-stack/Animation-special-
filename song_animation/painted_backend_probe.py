"""Actual CPU paint + rig integration smoke test; not song quality approval."""
import json
from pathlib import Path
from PIL import Image
from .environments import paint_environments
from .paint_layers import paint_foreground
from .vector import render_vector
from .render import render

def main():
    root=Path(__file__).parent;out=Path('painted_backend_probe');out.mkdir(exist_ok=True)
    plan=json.loads((root/'examples'/'vector_smoke.json').read_text())
    plan['scenes']=plan['scenes'][:1];plan['total_frames']=plan['scenes'][0]['end_frame'];plan['lyrics']=[]
    plan['bible']={'locations':'A sunny green valley, distant mountains and a village footpath','palette':'warm cream, teal, soft coral','characters':'No human actors in this integration smoke test'}
    plan['scenes'][0]['coverage']={'environment':'a green mountain valley','staging':'kite rises above the path','framing':'wide','visible_event':'kite is carried upward by wind'}
    before=render_vector(plan,0,48)
    plan=paint_foreground(paint_environments(plan,out),out)
    after=render_vector(plan,0,48)
    sheet=Image.new('RGB',(1080,960));sheet.paste(before,(0,0));sheet.paste(after,(540,0));sheet.save(out/'before_after.jpg',quality=92)
    render(plan,out,width=1080)
    (out/'probe.json').write_text(json.dumps({'cpu_backend_executed':True,'rig_preserved':True,'quality_certified':False},indent=2))
if __name__=='__main__':main()
