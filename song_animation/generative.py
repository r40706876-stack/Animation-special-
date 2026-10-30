"""Song-specific storyboards and original layered SVG artwork, not a scene menu."""
import copy,hashlib,json,math
from pathlib import Path
from .provider import generate_json
from .vector import validate_vector,sanitize_svg
from .lyrics import cues_from_lyrics

PROTOCOL='open-vector-v1'
ART_GUIDE='''Create original, elegant illustrated 2D film artwork, not icons, slides or text cards. Use carefully drawn expressive silhouettes, curved paths, detailed clothing/hair, attractive cohesive colours, light and shadow shapes, rich environmental detail and clear focal contrast. Fill the vertical composition with a real setting, foreground and depth; do not leave most of the image blank. Keep the story action mostly in y=80..750; a separate lyric panel may cover y=770..850. Bright balanced colours preferred, with night palettes only when the story calls for them. Maintain the same character identity, clothing, recurring objects and art style across shots.
Each SVG is one independent asset drawn in its OWN local viewBox. SVG must be self-contained, no scripts, text, images, use, foreignObject, style, filters, URLs or external resources. Allowed elements: svg,g,path,rect,circle,ellipse,line,polyline,polygon,defs,linearGradient,radialGradient,stop,clipPath. Inline fill/stroke/transform attributes only. Use xmlns="http://www.w3.org/2000/svg". Gradients may reference local #ids only. A detailed full setting can be a background asset at width=540,height=960 with pivot [0,0] at x=0,y=0. Characters/props use tight local viewBoxes with transparent background, raster widths/heights matching their intended pixel size. Do not put a full character AND its separately animated arm into both assets: rig separate body/head/limbs where useful. Draw enough paths/shapes to look illustrated rather than geometric placeholder art.'''


def storyboard(lyrics,music,out,fps=24):
    duration=lyrics['duration']
    prompt=f'''Direct an ORIGINAL connected {duration:.3f}-second vertical illustrated music film for THIS audio analysis and lyrics. There is NO fixed genre, object, character or scene menu. Romantic, devotional, celebratory, folk, rap, comic, motivational, narrative, sad and instrumental music must each get their own suitable world. Never force roses/hearts onto unrelated songs. Use the actual language, genre, mood, musical energy and meaning. Literal words alone are insufficient: construct a visual setup, action, consequence and ending. Avoid inventing claims about real people.
Return JSON: {{"title":"short title","bible":{{"style":"detailed shared art direction","palette":"shared colours","characters":"consistent identities/clothes","locations":"settings","motifs":"recurring objects","arc":"connected emotional progression"}},"scenes":[{{"start":0.0,"label":"shot meaning","visual":"precise original illustration composition","action":"what visibly happens; describe independently moving parts/objects and their causal interaction","lyric_ids":[0]}}]}}.
Plan about 5..8 shots for 30 seconds, fewer for a short input. First start=0, strictly increasing start seconds, each shot 1..8 seconds, final shot ends automatically at {duration:.3f}. Every lyric id must be referenced at least once. Empty ids allowed for instrumental shots. Include breathing space for instruments and a resolved ending, not an unrelated outro. Choose meaningful phrase/nearby beat boundaries. No captions in the artwork; those are added separately. Your setting and assets will be newly generated as layered vector art, so invent appropriate objects freely, but motions must be achievable by layered articulated 2D animation. No impossible promises of photorealistic 3D.
{ART_GUIDE}
AUDIO ANALYSIS: {json.dumps(lyrics,ensure_ascii=False)}
MUSIC: {json.dumps(music)}'''
    data=generate_json(prompt,out=out,tag='storyboard')
    scenes=data.get('scenes',[])
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
        'open_vocabulary':True,'protocol':PROTOCOL}


def scene_package(plan,index,out,previous_assets):
    shot=plan['scenes'][index];folder=Path(out)/'vector_assets';folder.mkdir(parents=True,exist_ok=True)
    # Reuse established character assets exactly when practical; scenery remains shot-specific.
    reusable={k:{'width':v['width'],'height':v['height'],'description':v.get('description',''),'svg':v['svg']} for k,v in previous_assets.items() if v.get('reusable')}
    if len(json.dumps(reusable))>40000:reusable={k:{x:v[x] for x in ('width','height','description')} for k,v in reusable.items()}
    prompt=f'''You are the illustrator AND 2D rig animator for shot {index+1} of this music film. Generate NEW layered vector assets suitable for the shot; no fixed object list. Return ONLY JSON.
FILM BIBLE: {json.dumps(plan['bible'],ensure_ascii=False)}
FULL STORY: {json.dumps([{k:s[k] for k in ('label','visual','action')} for s in plan['scenes']],ensure_ascii=False)}
THIS SHOT: {json.dumps(shot,ensure_ascii=False)}
AVAILABLE REUSABLE ASSETS: {json.dumps(reusable,ensure_ascii=False)}
{ART_GUIDE}
JSON shape: {{"background":"#RRGGBB","assets":[{{"id":"unique_safe_id","description":"what this artwork depicts","width":180,"height":260,"reusable":true,"svg":"<svg ...>...</svg>"}}],"nodes":[{{"id":"hero_body","asset":"asset_id","parent":null,"role":"foreground","pivot":[0.5,0.8],"easing":"smooth","keys":[{{"t":0,"x":270,"y":550,"rotation":0,"scale":1,"opacity":1}},{{"t":1,"x":300,"y":530,"rotation":0,"scale":1,"opacity":1}}],"wave":{{"rotation":0,"x":0,"y":0,"cycles":1,"phase":0}}}}]}}.
Use about 5..14 nodes, no more than 24. Parent must appear BEFORE child. A group node may have asset=null with children. Node x/y are its PIVOT position in canvas pixels, or relative to the parent pivot when parent exists. Rotation is degrees around its pivot; scale is uniform. Keys at normalized shot time t=0..1, 2..8 ordered keys, MUST start at 0 and end at 1. Each key has x,y,rotation,scale,opacity. Wave adds optional sinusoidal x/y/rotation movement, cycles per shot, phase in cycles. Keep amplitudes small/readable. At least TWO foreground assets need INDEPENDENT object/limb movement, not identical whole-picture pans. Animate the story action (handing, walking, bowing, dancing, a machine operating, water flowing, flight, etc.) with appropriate parts and trajectories. Background movement or camera zoom does not satisfy this. Static environment layers are fine. Art fills the frame and the main subject must remain legible at phone size. Do not place faces in the lyric safe area. Nodes have role=background or foreground only.
At most 14 newly drawn assets. Each asset SVG under 14000 characters. Choose clear curves and rich detail over hundreds of tiny shapes. Reuse an existing id without redefining it, or return its IDENTICAL SVG. New pose variant must have a new id. Do not draw text or watermarks. All geometry and ids must be valid. Avoid clipping the main action. Asset dimensions 4..1080 wide, 4..1920 tall.'''
    key=hashlib.sha256((PROTOCOL+prompt).encode()).hexdigest();cache=folder/f'scene_{index}_{key[:12]}.json'
    error=None
    for attempt in range(2):
        if cache.exists() and attempt==0:data=json.loads(cache.read_text())
        else:data=generate_json(prompt+('\nPREVIOUS PACKAGE FAILED VALIDATION: '+str(error)+'\nReturn a corrected complete JSON package, keeping the same meaning.' if error else ''),out=out,tag=f'scene_{index}_attempt_{attempt}')
        try:
            additions={a['id']:a for a in data.get('assets',[])}
            if len(additions)>14:raise ValueError('Scene asset budget exceeded')
            assets=copy.deepcopy(previous_assets)
            for aid,a in additions.items():
                sanitize_svg(a['svg'])
                if aid in assets and assets[aid]['svg']!=a['svg']:raise ValueError('Existing asset identity changed: '+aid)
                assets[aid]=a
            s=dict(shot,background=data['background'],nodes=data['nodes'])
            check=dict(plan,assets=assets,scenes=[dict(s,start_frame=0,end_frame=s['end_frame']-s['start_frame'])],total_frames=s['end_frame']-s['start_frame'])
            validate_vector(check)
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
