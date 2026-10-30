"""Song-specific storyboards and original layered SVG artwork, not a scene menu."""
import copy,hashlib,json,math,re
from pathlib import Path
from .provider import generate_json
from .vector import validate_vector,sanitize_svg
from .lyrics import cues_from_lyrics

PROTOCOL='open-vector-v3-quality'
ART_GUIDE='''Create original, elegant illustrated 2D film artwork, not icons, slides or text cards. Use carefully drawn expressive silhouettes, curved paths, detailed clothing/hair, attractive cohesive colours, light and shadow shapes, rich environmental detail and clear focal contrast. Fill the vertical composition with a real setting, foreground and depth; do not leave most of the image blank. Keep the story action mostly in y=80..750; a separate lyric panel may cover y=770..850. Use bright, legible, balanced editorial colours and softly lit daylight by default. Sadness can use muted warm daylight; do not make the whole frame near-black. Faces, hands and props must stay visible. Maintain the same character identity, clothing, recurring objects and art style across shots.
Each SVG is one independent asset drawn in its OWN local viewBox. SVG must be self-contained, no scripts, text, images, use, foreignObject, style, filters, URLs or external resources. Allowed elements: svg,g,path,rect,circle,ellipse,line,polyline,polygon,defs,linearGradient,radialGradient,stop,clipPath. Inline fill/stroke/transform attributes only. Use xmlns="http://www.w3.org/2000/svg". Gradients may reference local #ids only. A detailed full setting can be a background asset at width=540,height=960 with pivot [0,0] at x=0,y=0. Characters/props use tight local viewBoxes with transparent background, raster widths/heights matching their intended pixel size. Do not put a full character AND its separately animated arm into both assets: rig separate body/head/limbs where useful. Draw enough paths/shapes to look illustrated rather than geometric placeholder art.'''


NUMBER={'type':'NUMBER'}
KEY_SCHEMA={'type':'OBJECT','properties':{k:NUMBER for k in ('t','x','y','rotation','scale','opacity')},'required':['t','x','y','rotation','scale','opacity']}
PACKAGE_SCHEMA={'type':'OBJECT','properties':{
 'background':{'type':'STRING'},
 'assets':{'type':'ARRAY','items':{'type':'OBJECT','properties':{'id':{'type':'STRING'},'description':{'type':'STRING'},'width':NUMBER,'height':NUMBER,'reusable':{'type':'BOOLEAN'},'svg':{'type':'STRING'}},'required':['id','width','height','svg']}},
 'nodes':{'type':'ARRAY','items':{'type':'OBJECT','properties':{'id':{'type':'STRING'},'asset':{'type':'STRING','nullable':True},'parent':{'type':'STRING','nullable':True},'role':{'type':'STRING','enum':['background','foreground']},'pivot':{'type':'ARRAY','items':NUMBER,'minItems':2,'maxItems':2},'easing':{'type':'STRING'},'keys':{'type':'ARRAY','items':KEY_SCHEMA},'wave':{'type':'OBJECT','properties':{k:NUMBER for k in ('x','y','rotation','cycles','phase')}}},'required':['id','keys']}}},'required':['background','assets','nodes']}

def storyboard(lyrics,music,out,fps=24):
    duration=lyrics['duration']
    prompt=f'''Direct an ORIGINAL connected {duration:.3f}-second vertical illustrated music film for THIS audio analysis and lyrics. There is NO fixed genre, object, character or scene menu. Romantic, devotional, celebratory, folk, rap, comic, motivational, narrative, sad and instrumental music must each get their own suitable world. Never force roses/hearts onto unrelated songs. Use the actual language, genre, mood, musical energy and meaning. Literal words alone are insufficient: construct a visual setup, action, consequence and ending. Avoid inventing claims about real people.
Return JSON: {{"title":"short title","bible":{{"style":"detailed shared art direction","palette":"shared colours","characters":"consistent identities/clothes","locations":"settings","motifs":"recurring objects","arc":"connected emotional progression"}},"scenes":[{{"start":0.0,"label":"shot meaning","visual":"precise original illustration composition","action":"what visibly happens; describe independently moving parts/objects and their causal interaction","lyric_ids":[0]}}]}}.
Plan about 5..8 shots for 30 seconds, fewer for a short input. First start=0, strictly increasing start seconds, each shot 1..8 seconds, final shot ends automatically at {duration:.3f}. Every lyric id must be referenced at least once. Empty ids allowed for instrumental shots. Include breathing space for instruments and a resolved ending, not an unrelated outro. Choose meaningful phrase/nearby beat boundaries. No captions in the artwork; those are added separately. Your setting and assets will be newly generated as layered vector art, so invent appropriate objects freely, but motions must be achievable by layered articulated 2D animation. No impossible promises of photorealistic 3D.
Style direction: elegant richly illustrated 2D, expressive human figures where appropriate, detailed custom settings, balanced bright colours and layered depth. Sad songs may use muted warm daylight; avoid near-black whole frames. IMPORTANT: visual must be a PROSE description, never SVG/code. The illustration assets will be generated in the next stage.
AUDIO ANALYSIS: {json.dumps(lyrics,ensure_ascii=False)}
MUSIC: {json.dumps(music)}'''
    data=generate_json(prompt,out=out,tag='storyboard',prefer_quality=True)
    return compile_storyboard(data,lyrics,fps)

def compile_storyboard(data,lyrics,fps=24):
    duration=lyrics['duration']
    scenes=copy.deepcopy(data.get('scenes',[]))
    adjustments=[]
    if len(scenes)>1 and 0<duration-float(scenes[-1].get('start',duration))<1:
        ending=scenes.pop()
        scenes[-1]['action']+=' Ending: '+ending.get('action','Hold the resolved composition')
        scenes[-1]['lyric_ids']=list(dict.fromkeys(scenes[-1].get('lyric_ids',[])+ending.get('lyric_ids',[])))
        adjustments.append({'start':ending['start'],'reason':'Sub-second ending merged into previous readable shot'})
    if not 1<=len(scenes)<=12:raise ValueError('Storyboard needs 1..12 shots')
    starts=[s.get('start') for s in scenes]
    if any(type(v) not in (int,float) or not math.isfinite(v) or not 0<=v<duration for v in starts) or starts[0]!=0 or starts!=sorted(set(starts)):raise ValueError('Invalid storyboard shot starts')
    total=math.ceil(duration*fps);compiled=[];covered=set()
    for i,s in enumerate(scenes):
        a=round(starts[i]*fps);b=round(starts[i+1]*fps) if i+1<len(scenes) else total
        if not fps<=b-a<=8*fps:raise ValueError('Storyboard shot must last 1..8 seconds')
        refs=s.get('lyric_ids',[])
        if not isinstance(refs,list) or any(type(n) is not int or not 0<=n<len(lyrics['words']) for n in refs):raise ValueError('Invalid lyric references')
        covered.update(refs)
        for key in ('label','visual','action'):
            if not isinstance(s.get(key),str) or len(s[key].strip())<8:raise ValueError('Storyboard lacks '+key)
        compiled.append(dict(s,start_frame=a,end_frame=b,kind='vector'))
    if covered!=set(range(len(lyrics['words']))):raise ValueError('Storyboard omitted a lyric phrase')
    if not isinstance(data.get('bible'),dict):raise ValueError('Missing shared visual bible')
    return {'version':2,'title':data.get('title','Song film'),'bible':data['bible'],'fps':fps,'total_frames':total,
        'lyrics':cues_from_lyrics(lyrics,fps),'timing_granularity':lyrics.get('timing_granularity','phrase'),
        'timing_verified':False,'scenes':compiled,'assets':{},'planner':'generated_vector','review_status':'draft',
        'open_vocabulary':True,'protocol':PROTOCOL,'timeline_adjustments':adjustments,'allow_night':bool(re.search(r'रात|रैन|चाँद|चांद|अंधेर|अँधेर|\bnight\b|\bmoon\b|\bdarkness\b',' '.join(w['text'] for w in lyrics['words']),re.I))}



def normalize_package(data):
    """Remove decorative art text and regularize an invisible zero-scale endpoint.
    Everything else still passes the strict SVG and motion contracts.
    """
    from xml.etree import ElementTree as ET
    data=copy.deepcopy(data);changes=[]
    for asset in data.get('assets',[]):
        svg=asset.get('svg','')
        if re.search(r'<(?:[A-Za-z_]+:)?text(?:\s|>)',svg) and '<!' not in svg:
            try:root=ET.fromstring(svg)
            except ET.ParseError:continue
            removed=0
            for parent in root.iter():
                for child in list(parent):
                    if child.tag.split('}')[-1]=='text':parent.remove(child);removed+=1
            if removed:
                ET.register_namespace('', 'http://www.w3.org/2000/svg')
                asset['svg']=ET.tostring(root,encoding='unicode')
                changes.append({'asset':asset.get('id'),'removed_decorative_text':removed})
    for node in data.get('nodes',[]):
        keys=node.get('keys',[])
        ts=[k.get('t') for k in keys]
        if keys and len(keys)<=10 and all(type(t) in (int,float) and math.isfinite(t) and 0<=t<=1 for t in ts) and ts==sorted(set(ts)):
            if ts[0]>0:
                keys.insert(0,dict(keys[0],t=0))
                changes.append({'node':node.get('id'),'held_first_pose_from':0})
            if ts[-1]<1:
                keys.append(dict(keys[-1],t=1))
                changes.append({'node':node.get('id'),'held_last_pose_until':1})
        for key in node.get('keys',[]):
            if key.get('scale')==0 and key.get('opacity')==0:
                key['scale']=.05
                changes.append({'node':node.get('id'),'invisible_zero_scale_endpoint':key.get('t')})
    if changes:data['normalizations']=data.get('normalizations',[])+changes
    return data


def scene_package(plan,index,out,previous_assets):
    shot=plan['scenes'][index];folder=Path(out)/'vector_assets';folder.mkdir(parents=True,exist_ok=True)
    # Reuse established character assets exactly when practical; scenery remains shot-specific.
    reusable={k:{'width':v['width'],'height':v['height'],'description':v.get('description',''),'svg':v['svg']} for k,v in previous_assets.items() if v.get('reusable')}
    if len(json.dumps(reusable))>40000:reusable={k:{x:v[x] for x in ('width','height','description')} for k,v in reusable.items()}
    prompt=f'''You are the illustrator AND 2D rig animator for shot {index+1} of this music film. Generate NEW layered vector assets suitable for the shot; no fixed object list. Return ONLY JSON.
LIGHTING: Keep subjects and story props legible. Warm daylight is preferred for natural settings. A coherent neon/celestial/night world may keep its own lighting; give faces and moving parts enough contrast. Do not turn the main action into near-black silhouettes.
FILM BIBLE: {json.dumps(plan['bible'],ensure_ascii=False)}
FULL STORY: {json.dumps([{k:s[k] for k in ('label','visual','action')} for s in plan['scenes']],ensure_ascii=False)}
THIS SHOT: {json.dumps(shot,ensure_ascii=False)}
AVAILABLE REUSABLE ASSETS: {json.dumps(reusable,ensure_ascii=False)}
{ART_GUIDE}
JSON shape: {{"background":"#RRGGBB","assets":[{{"id":"unique_safe_id","description":"what this artwork depicts","width":180,"height":260,"reusable":true,"svg":"<svg ...>...</svg>"}}],"nodes":[{{"id":"hero_body","asset":"asset_id","parent":null,"role":"foreground","pivot":[0.5,0.8],"easing":"smooth","keys":[{{"t":0,"x":270,"y":550,"rotation":0,"scale":1,"opacity":1}},{{"t":1,"x":300,"y":530,"rotation":0,"scale":1,"opacity":1}}],"wave":{{"rotation":0,"x":0,"y":0,"cycles":1,"phase":0}}}}]}}.
Use about 5..14 nodes, no more than 24. PREFER parent=null and animate each part in CANVAS coordinates, including heads and arms. This avoids accidental double translations. If parenting is necessary, child x/y MUST be SMALL LOCAL OFFSETS from its parent pivot (e.g. head x=0,y=-100, NEVER x=270,y=480 for a parent already at 270,580). Parent must appear BEFORE child. A group node may have asset=null with children. Node x/y are its PIVOT position in canvas pixels, or relative to the parent pivot when parent exists. Rotation is degrees around its pivot; scale is uniform. Keys at normalized shot time t=0..1, 2..8 ordered keys, MUST start at 0 and end at 1. Each key has x,y,rotation,scale,opacity. Scale must be 0.05..4 (never zero); opacity 0..1. Use opacity=0 for invisible endpoints. Decorative symbols must use paths, never SVG text or font attributes. Wave adds optional sinusoidal x/y/rotation movement, cycles per shot, phase in cycles. Keep amplitudes small/readable. At least TWO foreground assets need INDEPENDENT object/limb movement, not identical whole-picture pans. Animate the story action (handing, walking, bowing, dancing, a machine operating, water flowing, flight, etc.) with appropriate parts and trajectories. Background movement or camera zoom does not satisfy this. Static environment layers are fine. Art fills the frame and the main subject must remain legible at phone size. Do not place faces in the lyric safe area. Nodes have role=background or foreground only.
At most 14 newly drawn assets. Each asset SVG under 14000 characters. Choose clear curves and rich detail over hundreds of tiny shapes. Reuse an existing id without redefining it, or return its IDENTICAL SVG. New pose variant must have a new id. Do not draw text or watermarks. All geometry and ids must be valid. Avoid clipping the main action. Asset dimensions 4..1080 wide, 4..1920 tall.'''
    key=hashlib.sha256((PROTOCOL+prompt).encode()).hexdigest();cache=folder/f'scene_{index}_{key[:12]}.json'
    error=None
    for attempt in range(3):
        try:
            if cache.exists() and attempt==0:data=json.loads(cache.read_text())
            else:data=generate_json(prompt+('\nPREVIOUS PACKAGE FAILED VALIDATION: '+str(error)+'\nReturn a corrected complete JSON package, keeping the same meaning.' if error else ''),out=out,tag=f'scene_{index}_attempt_{attempt}',schema=PACKAGE_SCHEMA,prefer_quality=True)

            data=normalize_package(data)
            additions={a['id']:a for a in data.get('assets',[])}
            if len(additions)>14:raise ValueError('Scene asset budget exceeded')
            assets=copy.deepcopy(previous_assets)
            variants={}
            for aid,a in list(additions.items()):
                if aid in assets and any(assets[aid].get(k)!=a.get(k) for k in ('svg','width','height')):
                    identity=json.dumps([a.get(k) for k in ('svg','width','height')])
                    new_id=aid[:65]+'_'+hashlib.sha256(identity.encode()).hexdigest()[:10]
                    variants[aid]=new_id
                    additions.pop(aid);additions[new_id]=dict(a,id=new_id)
            for node in data['nodes']:
                if node.get('asset') in variants:node['asset']=variants[node['asset']]
            if variants:data['normalizations']=data.get('normalizations',[])+[{'asset_variants':variants}]
            data['assets']=list(additions.values())
            for aid,a in additions.items():
                sanitize_svg(a['svg'])
                if aid in assets and assets[aid]['svg']!=a['svg']:raise ValueError('Existing asset identity changed: '+aid)
                assets[aid]=a
            s=dict(shot,background=data['background'],nodes=data['nodes'],normalizations=data.get('normalizations',[]))
            check=dict(plan,assets=assets,scenes=[dict(s,start_frame=0,end_frame=s['end_frame']-s['start_frame'])],total_frames=s['end_frame']-s['start_frame'])
            validate_vector(check)
            from .vector import invisible_foreground_nodes
            hidden=invisible_foreground_nodes(check)
            if hidden:raise ValueError("Foreground layers never enter the frame: "+str(hidden)+". Prefer parent=null and CANVAS coordinates; parented children must use local offsets, never repeated canvas positions.")
            from .vector import render_vector
            import numpy as np
            sample=render_vector(check,0,check['total_frames']//2)
            sample.save(folder/f'preflight_{index}.png')
            luminance=float(np.asarray(sample.convert('L')).mean())
            s['visibility_review']={'mean_luminance':round(luminance,2),'check_contrast':luminance<65,'advisory_only':True}
            # A neon or night composition can be legible with a dark average.
            # Never reject an entire musical genre from a global brightness mean.
            cache.write_text(json.dumps(data,ensure_ascii=False,indent=2))
            return s,assets
        except (ValueError,KeyError,TypeError) as e:error=str(e)
    raise ValueError(f'Custom shot {index+1} could not be generated: {error}')


def build(lyrics,music,out):
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    checkpoint=out/'vector_checkpoint.json'
    key=hashlib.sha256((PROTOCOL+json.dumps([lyrics,music],sort_keys=True,ensure_ascii=False)).encode()).hexdigest()
    if checkpoint.exists() and (out/'storyboard.json').exists() and json.loads(checkpoint.read_text()).get('key')==key:
        plan=json.loads((out/'storyboard.json').read_text())
    else:
        plan=storyboard(lyrics,music,out)
        checkpoint.write_text(json.dumps({'key':key}))
    (out/'storyboard.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2))
    for i in range(len(plan['scenes'])):
        print(f'Generating custom illustrated shot {i+1}/{len(plan["scenes"])}',flush=True)
        scene,assets=scene_package(plan,i,out,plan['assets'])
        plan['scenes'][i]=scene;plan['assets']=assets
        (out/'partial_plan.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2))
    return validate_vector(plan)
