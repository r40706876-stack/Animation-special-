"""Paint texture/detail into planned actors without losing their alpha or rigs.

This uses bounded image-to-image inference on the actual drawn asset, rather
than replacing a song character with an unrelated stock photograph.
"""
import base64,copy,hashlib,io,json
from pathlib import Path
from PIL import Image
from .environments import MODEL,REVISION,inference_pipeline
from .vector import raster,validate_vector

def prepared_asset(asset):
    original=raster(asset['svg'],int(asset['width']),int(asset['height'])).copy()
    w,h=original.size;ratio=min(448/w,448/h)
    size=(max(1,round(w*ratio)),max(1,round(h*ratio)))
    left=(512-size[0])//2;top=(512-size[1])//2
    canvas=Image.new('RGB',(512,512),'#fff8e9');small=original.resize(size,Image.Resampling.LANCZOS)
    canvas.paste(small,(left,top),small)
    return original,canvas,(left,top,left+size[0],top+size[1])

def restore_painted(image,original,box):
    painted=image.convert('RGBA').crop(box).resize(original.size,Image.Resampling.LANCZOS)
    painted.putalpha(original.getchannel('A'))
    return painted

def paint_foreground(plan,out,pipeline=None,budget=24):
    candidate=copy.deepcopy(plan);folder=Path(out)/'painted_actors';folder.mkdir(parents=True,exist_ok=True)
    active=set(n.get('asset') for s in candidate['scenes'] for n in s['nodes'] if n.get('role')!='background')
    eligible=[aid for aid in active if aid in candidate['assets'] and 'svg' in candidate['assets'][aid] and min(candidate['assets'][aid]['width'],candidate['assets'][aid]['height'])>=55]
    eligible=sorted(eligible,key=lambda aid:(-candidate['assets'][aid]['width']*candidate['assets'][aid]['height'],aid))[:budget]
    pipe=pipeline;report=[]
    for aid in eligible:
        a=candidate['assets'][aid]
        prompt=('Premium finely engraved watercolor illustration of precisely this isolated asset: '+a.get('description',aid)+
            '. Preserve the input silhouette, pose, orientation, scale, clothing and local composition. Add detailed organic ink contours, tactile watercolor modeling and beautiful legible surfaces. '
            'Do not add other people, extra limbs, extra objects, words or scenery. If this is a head or hand, show only that part, not a full person. '
            'Shared character identity and clothing: '+str(plan.get('bible',{}).get('characters',''))[:450]+
            '. Shared palette: '+str(plan.get('bible',{}).get('palette',''))[:200])
        key=hashlib.sha256((REVISION+'paint-v1'+prompt+a['svg']+json.dumps([a['width'],a['height']])).encode()).hexdigest();path=folder/(key+'.png')
        original,canvas,box=prepared_asset(a)
        if not path.exists():
            import torch
            if pipe is None:
                from diffusers import AutoPipelineForImage2Image
                pipe=AutoPipelineForImage2Image.from_pipe(inference_pipeline())
            image=pipe(prompt=prompt,image=canvas,strength=.62,num_inference_steps=8,guidance_scale=0,
                generator=torch.Generator(device='cpu').manual_seed(int(key[:8],16))).images[0]
            painted=restore_painted(image,original,box)
            if max(painted.convert('RGB').getextrema())[1]<5:raise RuntimeError('Foreground painting returned a blank image')
            painted.save(path)
        with Image.open(path) as im:
            im.load()
            if im.size!=original.size:raise ValueError('Cached actor changed its rig dimensions')
            if im.convert('RGBA').getchannel('A').tobytes()!=original.getchannel('A').tobytes():raise ValueError('Painted actor lost its original silhouette')
        a['raster_png']=base64.b64encode(path.read_bytes()).decode();a['painted_actor']=True
        report.append({'asset':aid,'model':MODEL,'revision':REVISION,'key':key,'file':path.name,'prompt':prompt})
    (Path(out)/'painted_actors.json').write_text(json.dumps({'quality_certified':False,'assets':report,'remaining_vector_assets':len(active)-len(eligible)},ensure_ascii=False,indent=2))
    return validate_vector(candidate)
