"""Bounded scene planner; no AI-written code is executed."""
import json,math,os,time
from pathlib import Path
from .contract import ACTIONS,validate,validate_lyrics
ROOT=Path(__file__).resolve().parents[1]

def make_plan(lyrics,music,fps=24):
    import requests
    validate_lyrics(lyrics['words'],lyrics['duration'])
    prompt='''Direct a connected illustrated music film. Hindi transcript below is imperfect ASR, not authoritative lyrics.
Understand the whole segment's emotional progression. Use only supported actions when their visible action fits the meaning. No invented unsupported assets/actions. If incompatible, return {"unsupported_reason":"reason"}.
Same rose recurs: gift transfers it, bloom opens it, crowd has a central rose owner, paths separates two people, heart holds a memory rose. This is a LIMITED visual vocabulary. Do not force rose romance onto incompatible devotional, comic, political or unrelated lyrics.
Return JSON: {"title":"short Hindi title","intent":"Hindi emotional arc","palette":"warm|hope|memory","scenes":[{"kind":"supported kind","start_word_id":0,"cue_word_id":3,"lyric_ids":[0,1,2,3],"reason":"Hindi meaning and actual visible action"}]}.
Use 3..10 readable shots where possible, >=1 second each. First starts at word 0, increasing start_word_id. Cover every word exactly once in contiguous lyric_ids ranges. Cue belongs to its shot; choose meaningful word for action. Group phrases rather than single words. Do not correct uncertain words. Code derives timestamps and covers instrumental gaps. No banners.
SUPPORTED: '''+json.dumps(ACTIONS)+'\nLYRICS: '+json.dumps(lyrics,ensure_ascii=False)+'\nMUSIC: '+json.dumps(music)
    key=os.environ.get('GEMINI_API_KEY','').strip()
    if not key:raise RuntimeError('GEMINI_API_KEY is missing')
    # Discover actual available models; never retry a retired model indefinitely.
    try:
        listing=requests.get('https://generativelanguage.googleapis.com/v1beta/models',headers={'x-goog-api-key':key},params={'pageSize':1000},timeout=25)
        listing.raise_for_status()
        models=[m['name'].removeprefix('models/') for m in listing.json().get('models',[]) if 'generateContent' in m.get('supportedGenerationMethods',[]) and 'flash' in m['name'] and not any(x in m['name'] for x in ('image','tts','audio','live','robotics'))]
    except requests.RequestException:raise RuntimeError('Could not discover available planner models') from None
    import re
    def rank(m):
        v=re.search(r'gemini-(\d+(?:\.\d+)?)',m)
        return ('lite' in m, 'preview' in m or 'exp' in m, -float(v.group(1)) if v else 0,m)
    models=sorted(set(models),key=rank)
    pinned=os.environ.get('GEMINI_MODEL','')
    if pinned in models:models=[pinned]+[m for m in models if m!=pinned]
    raw=None
    for model in models[:3]:
        try:
            r=requests.post('https://generativelanguage.googleapis.com/v1beta/models/'+model+':generateContent',
                headers={'x-goog-api-key':key},json={'contents':[{'parts':[{'text':prompt}]}],
                'generationConfig':{'responseMimeType':'application/json','temperature':.35}},timeout=90)
        except requests.RequestException:continue
        if r.status_code==200:
            parts=r.json().get('candidates',[{}])[0].get('content',{}).get('parts',[])
            raw=''.join(p.get('text','') for p in parts if not p.get('thought'))
            if raw:break
        print('Planner unavailable:',model,'HTTP',r.status_code,flush=True)
    if not raw:raise RuntimeError('Planner unavailable after at most three discovered models')
    return compile_plan(json.loads(raw[raw.find('{'):raw.rfind('}')+1]),lyrics,fps)

def compile_plan(data,lyrics,fps=24):
    if data.get('unsupported_reason'):raise ValueError('Unsupported song/story: '+str(data['unsupported_reason']))
    words=lyrics['words'];dur=lyrics['duration'];n=len(words);scenes=data.get('scenes',[])
    if not scenes or not 1<=len(scenes)<=10:raise ValueError('Invalid shot count')
    starts=[s.get('start_word_id') for s in scenes]
    if any(type(v) is not int or not 0<=v<n for v in starts) or starts[0]!=0 or starts!=sorted(set(starts)):raise ValueError('Invalid lyric boundaries')
    total=math.ceil(dur*fps);out=[]
    for i,s in enumerate(scenes):
        first=starts[i];last=starts[i+1] if i+1<len(starts) else n
        if s.get('lyric_ids')!=list(range(first,last)):raise ValueError('Every word must belong to exactly one contiguous shot')
        cue=s.get('cue_word_id')
        if type(cue) is not int or not first<=cue<last:raise ValueError('Cue outside its lyric phrase')
        a=0 if i==0 else round(words[first]['start']*fps);b=round(words[last]['start']*fps) if last<n else total;cf=round(words[cue]['start']*fps)
        if not a<=cf<b:raise ValueError('Cue outside shot after quantization')
        out.append({'kind':s['kind'],'start_frame':a,'end_frame':b,'cue_frame':cf,'lyric_ids':s['lyric_ids'],'reason':s['reason']})
    return validate({'version':1,'title':data.get('title','Song draft'),'intent':data.get('intent',''),'fps':fps,'total_frames':total,'palette':data.get('palette'),'scenes':out,'review_status':'draft','timing_method':lyrics.get('timing_method','supplied timings'),'timing_verified':False})
