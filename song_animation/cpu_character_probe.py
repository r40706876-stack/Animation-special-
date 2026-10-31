"""Actual local image generation, not texture painted onto an icon silhouette."""
import json,time
from pathlib import Path
from PIL import Image

def main():
    from rembg import new_session,remove
    from .local_image import generate_image
    from .environments import MODEL,REVISION
    from .flux_layers import prompt_for_asset
    out=Path('cpu_character_probe');out.mkdir(exist_ok=True)
    fixture=json.loads((Path(__file__).parent/'examples/illustration_probe.json').read_text())
    fixture['asset']['subject_kind']='human'
    prompt=prompt_for_asset(fixture['asset'],fixture['bible'],separate_limbs=True)
    start=time.monotonic();path=generate_image(prompt,out/'raw_images',6620)
    image=Image.open(path).convert('RGB')
    image.save(out/'character.png')
    cutout=remove(image,session=new_session('u2netp',providers=['CPUExecutionProvider']));cutout.save(out/'character_cutout.png')
    (out/'probe.json').write_text(json.dumps({'model':MODEL,'revision':REVISION,'prompt':prompt,'seconds':round(time.monotonic()-start,2),'source':'local_text_to_image','quality_certified':False},indent=2))

if __name__=='__main__':main()
