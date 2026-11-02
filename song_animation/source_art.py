"""Source-bound original-art checkpoints; byte integrity is not visual approval."""
import base64,copy,hashlib,json
from pathlib import Path
from .vector import validate_vector,decode_painted

ROOT=Path(__file__).parent/'source_art'

def fingerprint(plan):
    data=copy.deepcopy(plan)
    for asset in data.get('assets',{}).values():asset.pop('raster_png',None)
    return hashlib.sha256(json.dumps(data,sort_keys=True,ensure_ascii=False).encode()).hexdigest()

def scene_fingerprint(scene):
    return hashlib.sha256(json.dumps(scene,sort_keys=True,ensure_ascii=False).encode()).hexdigest()

def apply(plan,source_sha256,root=ROOT):
    folder=Path(root)/source_sha256;manifest=folder/'manifest.json'
    if not manifest.is_file():return plan,set(),set()
    data=json.loads(manifest.read_text())
    if data.get('source_clip_sha256')!=source_sha256:return plan,set(),set()
    exact_plan=fingerprint(plan) in data.get('plan_fingerprints',[])
    targets=data.get('scene_fingerprints',{})
    # Repairs elsewhere in the film must not discard an unchanged completed
    # scene. Changed poses, story states or review corrections invalidate it.
    exact_scenes=bool(targets) and all(str(i).isdigit() and 0<=int(i)<len(plan['scenes']) and scene_fingerprint(plan['scenes'][int(i)]) in allowed for i,allowed in targets.items())
    if not (exact_plan or exact_scenes):return plan,set(),set()
    candidate=copy.deepcopy(plan);locked=set();scenes=set()
    for aid,item in data.get('assets',{}).items():
        path=(folder/item['file']).resolve()
        if not path.is_relative_to(folder.resolve()):raise ValueError('Source artwork path leaves its source folder')
        raw=path.read_bytes()
        if hashlib.sha256(raw).hexdigest()!=item['sha256']:raise ValueError('Source artwork bytes changed')
        encoded=base64.b64encode(raw).decode();image=decode_painted(encoded)
        if list(image.size)!=[item['width'],item['height']]:raise ValueError('Source artwork dimensions changed')
        asset=candidate['assets'].setdefault(aid,{})
        asset.update(width=item['width'],height=item['height'],raster_png=encoded,raster_art_provider=item['provider'])
        locked.add(aid)
    for patch in data.get('scenes',[]):
        index=patch['index']
        if type(index) is not int or not 0<=index<len(candidate['scenes']):raise ValueError('Invalid source scene patch')
        candidate['scenes'][index]['nodes']=copy.deepcopy(patch['nodes']);scenes.add(index)
    # These still go through the same composition, motion, story and export gates.
    return validate_vector(candidate),locked,scenes
