"""Original raster cutouts and viewpoint-specific sets; no geometric paint-over."""
import base64,copy,hashlib,json,re
from pathlib import Path
from PIL import Image
from .free_image import generate_image
from .vector import validate_vector

def seed_for(text):return int(hashlib.sha256(text.encode()).hexdigest()[:8],16)%(2**31)

def prompt_for_asset(asset,bible,separate_limbs=False):
    subject=str(asset.get('description') or asset['id'].replace('_',' '))
    isolation='One isolated subject on a pure white background, complete silhouette with margins. No scenery, lettering or watermark.'
    extra=''
    if separate_limbs and asset.get('subject_kind','human')=='human':extra='This is the head and torso of a layered animation rig: hands are hidden behind the body. Do not show detached hands or extra arms.'
    words=(asset['id']+' '+subject).lower().replace('_',' ')
    human=asset.get('subject_kind')=='human' if asset.get('subject_kind') else bool(re.search(r'\b(body|torso|head|face|arms?|hands?|person|poet|woman|man)\b',words))
    if human and re.search(r'\bhands?\b',words) and not separate_limbs:extra='Show ONLY the requested isolated hand with its cuff and the specified held prop. No face, torso or full person.'
    elif human and re.search(r'\barms?\b',words) and not separate_limbs:extra='Show ONLY one isolated sleeved arm and hand in the requested pose. No face, torso or full person.'
    elif human and re.search(r'\b(head|face)\b',words) and not separate_limbs:extra='Show ONLY the requested portrait head and neck. No full body or extra people.'
    identity=' Character identity and clothing: '+str(bible.get('characters',''))[:550] if human else ' No people or extra objects.'
    return (subject+'. Premium detailed painterly storybook illustration, expressive natural anatomy where appropriate, fine organic contours, rich modeled surfaces and restrained watercolor texture. '+extra+identity+'. Palette: '+str(bible.get('palette',''))[:160]+'. '+isolation)

def is_structural(asset):
    text=(asset['id']+' '+str(asset.get('description',''))).lower()
    return any(word in text for word in ('stroke','ripple','droplet','wind_line','breath_','goblet_fill','outline','petal'))

def cutout(image,session):
    from rembg import remove
    result=remove(image.convert('RGB'),session=session).convert('RGBA')
    bounds=result.getchannel('A').point(lambda a:255 if a>15 else 0).getbbox()
    if not bounds:raise ValueError('Generated foreground has no usable subject matte')
    if (bounds[2]-bounds[0])*(bounds[3]-bounds[1])<image.width*image.height*.015:raise ValueError('Generated foreground subject is too small')
    return result.crop(bounds)

def paint_foreground(plan,out):
    from rembg import new_session
    out=Path(out);folder=out/'flux_assets';folder.mkdir(parents=True,exist_ok=True)
    candidate=copy.deepcopy(plan);active={n.get('asset') for s in candidate['scenes'] for n in s['nodes'] if n.get('role')!='background'}
    session=None;report=[]
    for aid in sorted(active):
        a=candidate['assets'].get(aid)
        if not a or 'svg' not in a or min(a['width'],a['height'])<45 or is_structural(a):continue
        body='body' in aid.lower() or 'torso' in aid.lower()
        prompt=prompt_for_asset(a,plan.get('bible',{}),separate_limbs=body)
        seed=seed_for(str(plan.get('bible',{}).get('characters',''))+aid.split('_')[0])
        key=hashlib.sha256(('flux-cutout-v1'+prompt+str([a['width'],a['height']])).encode()).hexdigest();path=folder/(key+'.png')
        if not path.exists():
            raw=generate_image(prompt,out/'flux_images',seed)
            if session is None:session=new_session('u2netp',providers=['CPUExecutionProvider'])
            with Image.open(raw) as image:subject=cutout(image,session)
            canvas=Image.new('RGBA',(int(a['width']),int(a['height'])))
            subject.thumbnail(canvas.size,Image.Resampling.LANCZOS)
            canvas.alpha_composite(subject,((canvas.width-subject.width)//2,canvas.height-subject.height))
            canvas.save(path)
        with Image.open(path) as image:
            image.load()
            if image.size!=(int(a['width']),int(a['height'])) or not image.convert('RGBA').getchannel('A').getbbox():raise ValueError('Invalid cached raster cutout')
        a['raster_png']=base64.b64encode(path.read_bytes()).decode();a['raster_art_provider']='public-flux';a.pop('painted_actor',None)
        report.append({'asset':aid,'file':path.name,'quality_certified':False})
        (out/'flux_assets.json').write_text(json.dumps({'assets':report,'quality_certified':False},indent=2))
    return validate_vector(candidate)

def environment_prompt(plan,scene):
    coverage=scene.get('coverage',{})
    return (str(coverage.get('framing','wide'))+' viewpoint. '+str(coverage.get('environment',scene.get('visual','')))[:170]+'. Background supporting this staging: '+str(coverage.get('staging',scene.get('action','')))[:220]+'. Detailed warm daylight watercolor environment, cohesive palette '+str(plan.get('bible',{}).get('palette',''))[:100]+'. Match the stated viewpoint: an overhead desk insert shows the writing surface, not a wide balcony window. Empty setting with supporting surfaces, no people, no hero objects, no writing, no watermark.')

def paint_environments(plan,out):
    out=Path(out);candidate=copy.deepcopy(plan)
    for scene in candidate['scenes']:
        prompt=environment_prompt(plan,scene);path=generate_image(prompt,out/'flux_images',seed_for(prompt),768,1344)
        aid='flux_set_'+hashlib.sha256(prompt.encode()).hexdigest()[:16]
        candidate['assets'][aid]={'width':540,'height':960,'description':'Original viewpoint-specific painted setting','raster_png':base64.b64encode(path.read_bytes()).decode()}
        nodes=[n for n in scene['nodes'] if not n.get('painted_set')]
        for n in nodes:
            if n.get('role')=='background':n['asset']=None
        while True:
            kept=[n for n in nodes if n.get('asset') or any(c.get('parent')==n['id'] for c in nodes)]
            if len(kept)==len(nodes):break
            nodes=kept
        nid='flux_environment'
        while any(n['id']==nid for n in nodes):nid+='_' 
        scene['nodes']=[{'id':nid,'asset':aid,'role':'background','painted_set':True,'pivot':[0,0],'keys':[dict(t=t,x=0,y=0,scale=1,rotation=0,opacity=1) for t in (0,1)]}]+nodes
    used={n.get('asset') for s in candidate['scenes'] for n in s['nodes']}
    candidate['assets']={k:v for k,v in candidate['assets'].items() if not k.startswith(('painted_set_','flux_set_')) or k in used}
    return validate_vector(candidate)
