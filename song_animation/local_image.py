"""Self-hosted original cutouts: no public generation endpoint or GPU quota."""
import hashlib,json,re
from pathlib import Path
from PIL import Image
from .environments import inference_pipeline,MODEL,REVISION

def compact_prompt(prompt):
    if '. Premium detailed' in prompt:
        subject=prompt.split('. Premium detailed',1)[0]
        identity=prompt.split('Character identity and clothing: ',1)[-1].split('. Palette:',1)[0] if 'Character identity and clothing: ' in prompt else ''
        part=prompt.split('Show ONLY ',1)[-1].split('.',1)[0] if 'Show ONLY ' in prompt else ''
        # A short encoder otherwise drops rig constraints at the end of the
        # full prompt, painting duplicate hands beneath animated hand layers.
        rig='Arms folded behind the back. ' if 'hands are hidden behind the body' in prompt else ''
        if rig:identity=re.sub(r'\bexpressive hands\b[, ]*','',identity,flags=re.I)
        return (' '.join(subject.split()[:24])+'. '+rig+('Only '+' '.join(part.split()[:10])+'. ' if part else '')+'Isolated, pure white background. '+' '.join(identity.split()[:12])+'. Detailed natural watercolor illustration, organic contours and expressive features.')
    if ' viewpoint.' in prompt:
        framing,rest=prompt.split(' viewpoint.',1)
        location=rest.split('. Background supporting',1)[0]
        close=any(x in framing.lower() for x in ('close','macro','overhead','top-down','top down'))
        treatment='Softly lit neutral supporting surface, distant setting blurred. ' if close else ''
        return ('Empty setting, no people, no animals, no letters. '+' '.join(framing.split()[:6])+' viewpoint. '+treatment+' '.join(location.split()[:18])+'. Detailed warm watercolor illustration, readable depth.')
    return ' '.join(prompt.split()[:55])

def generate_image(prompt,out,seed,width=768,height=1024):
    import torch
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    # SD Turbo's useful native scale is 512px; retain portrait scenery detail.
    w,h=(512,896) if height/width>1.6 else (512,768)
    # The local CLIP encoder has a short context. Keep the subject FIRST.
    short=compact_prompt(prompt)
    params={'model':MODEL,'revision':REVISION,'prompt':short,'seed':seed,'width':w,'height':h,'steps':4}
    key=hashlib.sha256(json.dumps(params,sort_keys=True).encode()).hexdigest();path=out/(key+'.png');record=out/(key+'.json')
    if path.exists() and record.exists():
        try:
            data=json.loads(record.read_text())
            if data.get('sha256')==hashlib.sha256(path.read_bytes()).hexdigest():
                with Image.open(path) as im:
                    im.load()
                    if im.size==(w,h):return path
        except (OSError,ValueError):pass
    print('Drawing original local artwork',key[:12],flush=True)
    image=inference_pipeline()(prompt=short,num_inference_steps=4,guidance_scale=0,height=h,width=w,generator=torch.Generator(device='cpu').manual_seed(seed)).images[0]
    if image.convert('RGB').getextrema()==((0,0),(0,0),(0,0)):raise ValueError('Local image generation returned a blank image')
    temporary=path.with_suffix('.partial.png');image.save(temporary);temporary.replace(path)
    record.write_text(json.dumps(dict(params,sha256=hashlib.sha256(path.read_bytes()).hexdigest(),quality_certified=False),indent=2))
    return path
