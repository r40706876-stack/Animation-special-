"""Source-bound original-art checkpoints; byte integrity is not visual approval."""
import base64,copy,hashlib,json
from pathlib import Path
from .vector import validate_vector,decode_painted
ROOT=Path(__file__).parent/'source_art'

def fingerprint(plan):
    data=copy.deepcopy(plan)
    for asset in data.get('assets',{}).values():
        asset.pop('raster_png',None);asset.pop('raster_frames',None)
    return hashlib.sha256(json.dumps(data,sort_keys=True,ensure_ascii=False).encode()).hexdigest()

def scene_fingerprint(scene):
    return hashlib.sha256(json.dumps(scene,sort_keys=True,ensure_ascii=False).encode()).hexdigest()

def apply(plan,source_sha256,root=ROOT):
    folder=Path(root)/source_sha256;manifest=folder/'manifest.json'
    if not manifest.is_file():return plan,set(),set()
    data=json.loads(manifest.read_text())
    if data.get('source_clip_sha256')!=source_sha256:return plan,set(),set()
    exact_plan=fingerprint(plan) in data.get('plan_fingerprints',[])
    # A changed scene may share an asset name with a completed scene. Preserve
    # the completed art under a stable alias rather than overwriting the repair.
    aliases={aid[:60]+'_src_'+item['sha256'][:8]:aid for aid,item in data.get('assets',{}).items()}
    matched=set()
    for index,allowed in data.get('scene_fingerprints',{}).items():
        if not str(index).isdigit() or not 0<=int(index)<len(plan['scenes']):continue
        scene=copy.deepcopy(plan['scenes'][int(index)])
        for node in scene['nodes']:
            if node.get('asset') in aliases:node['asset']=aliases[node['asset']]
        if scene_fingerprint(scene) in allowed:matched.add(int(index))
    patches=[p for p in data.get('scenes',[]) if exact_plan or p.get('index') in matched]
    if not exact_plan and not patches:return plan,set(),set()
    candidate=copy.deepcopy(plan);locked=set();scenes={p['index'] for p in patches}
    used={n.get('asset') for p in patches for n in p['nodes'] if n.get('asset')}
    # Old single-asset packs may have no scene patch at all.
    if exact_plan and not patches:used=set(data.get('assets',{}))
    outside={n.get('asset') for i,s in enumerate(plan['scenes']) if i not in scenes for n in s['nodes'] if n.get('asset')}
    rename={}
    for aid,item in data.get('assets',{}).items():
        if aid not in used:continue
        path=(folder/item['file']).resolve()
        if not path.is_relative_to(folder.resolve()):raise ValueError('Source artwork path leaves its source folder')
        raw=path.read_bytes()
        if hashlib.sha256(raw).hexdigest()!=item['sha256']:raise ValueError('Source artwork bytes changed')
        encoded=base64.b64encode(raw).decode();image=decode_painted(encoded)
        if list(image.size)!=[item['width'],item['height']]:raise ValueError('Source artwork dimensions changed')
        target=aid if aid not in outside else aid[:60]+'_src_'+item['sha256'][:8]
        if target!=aid:rename[aid]=target
        asset=candidate['assets'].setdefault(target,copy.deepcopy(candidate['assets'].get(aid,{})))
        asset.update(width=item['width'],height=item['height'],raster_png=encoded,raster_art_provider=item['provider']);locked.add(target)
        if item.get('frames'):
            frames=[]
            for frame in item['frames']:
                frame_path=(folder/frame['file']).resolve()
                if not frame_path.is_relative_to(folder.resolve()):raise ValueError('Pose file leaves its source folder')
                frame_raw=frame_path.read_bytes()
                if hashlib.sha256(frame_raw).hexdigest()!=frame['sha256']:raise ValueError('Source pose bytes changed')
                frame_encoded=base64.b64encode(frame_raw).decode()
                if decode_painted(frame_encoded).size!=(item['width'],item['height']):raise ValueError('Source pose dimensions changed')
                frames.append(frame_encoded)
            asset.update(raster_frames=frames,frame_hold=item.get('frame_hold',3))
    for patch in patches:
        index=patch['index']
        if type(index) is not int or not 0<=index<len(candidate['scenes']):raise ValueError('Invalid source scene patch')
        nodes=copy.deepcopy(patch['nodes'])
        for node in nodes:
            if node.get('asset') in rename:node['asset']=rename[node['asset']]
        candidate['scenes'][index]['nodes']=nodes
    return validate_vector(candidate),locked,scenes
