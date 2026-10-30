"""Original song-specific painted sets, with independently animated vector actors.

CPU inference is an art backend, not a quality certificate. Existing actual-MP4
meaning, action, anatomy, variety and finish reviews still decide acceptance.
"""
import base64,hashlib,io,json,copy
from functools import lru_cache
from pathlib import Path
from PIL import Image

MODEL='stabilityai/sd-turbo'
REVISION='b261bac6fd2cf515557d5d0707481eafa0485ec2'

@lru_cache(maxsize=1)
def inference_pipeline():
    import torch
    from diffusers import AutoPipelineForText2Image
    torch.set_num_threads(2)
    pipe=AutoPipelineForText2Image.from_pretrained(MODEL,revision=REVISION,variant='fp16',torch_dtype=torch.float32,use_safetensors=True,low_cpu_mem_usage=True)
    pipe.to('cpu');pipe.enable_attention_slicing('max')
    return pipe

def environment_prompt(plan,scene):
    coverage=scene.get('coverage',{})
    # CLIP's short text window must see the requested world FIRST. Long style
    # preambles previously truncated the location and turned a valley into arches.
    location=str(coverage.get('environment',scene.get('visual','a sunlit open landscape')))[:150]
    palette=str(plan.get('bible',{}).get('palette','bright natural colors'))[:65]
    return (location+'. Colorful watercolor painting, '+palette+
        '. Bright daylight, layered depth, clear central action area, empty setting, '
        'no people, no animals, no hero props, no text.')

def cache_key(prompt):return hashlib.sha256((MODEL+REVISION+prompt).encode()).hexdigest()

def paint_environments(plan,out,pipeline=None):
    """Generate once per concrete location; retain actors, props and motion rigs."""
    out=Path(out);folder=out/'painted_environments';folder.mkdir(parents=True,exist_ok=True)
    candidate=copy.deepcopy(plan);pipe=pipeline;report=[]
    for index,scene in enumerate(candidate['scenes']):
        prompt=environment_prompt(candidate,scene);key=cache_key(prompt);path=folder/(key+'.png')
        if not path.exists():
            import torch
            if pipe is None:
                pipe=inference_pipeline()
            image=pipe(prompt=prompt,num_inference_steps=4,guidance_scale=0.0,height=896,width=512,
                generator=torch.Generator(device='cpu').manual_seed(int(key[:8],16))).images[0]
            if image.convert('RGB').getextrema()==((0,0),(0,0),(0,0)):raise RuntimeError('Painted set is blank')
            image.save(path)
        with Image.open(path) as im:
            im.load();im=im.convert('RGB');buf=io.BytesIO();im.save(buf,format='PNG')
        aid='painted_set_'+key[:16]
        candidate['assets'][aid]={'width':540,'height':960,'description':'Original painted environment, no actors',
            'raster_png':base64.b64encode(buf.getvalue()).decode(),'reusable':False}
        # Disable old background artwork without deleting parents of actor rigs.
        nodes=[n for n in scene['nodes'] if not n.get('painted_set')]
        for node in nodes:
            if node.get('role')=='background' and node.get('asset'):
                node['asset']=None
                # Keep transform-only parents; unused leaves can be discarded.
        nodes=[n for n in nodes if n.get('asset') or any(c.get('parent')==n['id'] for c in nodes)]
        node={'id':'painted_environment','asset':aid,'role':'background','painted_set':True,'pivot':[0,0],
            'keys':[dict(t=t,x=0,y=0,scale=1,rotation=0,opacity=1) for t in (0,1)]}
        scene['nodes']=[node]+nodes
        if len(scene['nodes'])>24:raise ValueError('Painted set exceeds scene layer budget')
        report.append({'shot':index,'key':key,'model':MODEL,'revision':REVISION,'file':path.name,'prompt':prompt})
    (out/'painted_environments.json').write_text(json.dumps({'backend':'cpu-sd-turbo','quality_certified':False,'shots':report},ensure_ascii=False,indent=2))
    from .vector import validate_vector
    return validate_vector(candidate)
