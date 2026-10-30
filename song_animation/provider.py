"""Bounded provider transport; safe diagnostics, no model code execution."""
import json,os
from pathlib import Path

def parse_object(raw):
    start=raw.find('{')
    if start<0:raise ValueError('Provider returned no JSON object')
    data,_=json.JSONDecoder().raw_decode(raw[start:])
    if not isinstance(data,dict):raise ValueError('Provider response must be an object')
    return data

def generate_json(prompt,out=None,tag="planner",audio_part=None,schema=None,extra_parts=None,max_tokens=32768,prefer_quality=False):
    import requests
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
        return ('preview' in m or 'exp' in m, 'lite' not in m, -float(v.group(1)) if v else 0,m)
    models=sorted(set(models),key=rank)
    if prefer_quality:
        full=[m for m in models if 'lite' not in m]
        lite=[m for m in models if 'lite' in m]
        models=list(dict.fromkeys(full[:1]+lite[:1]+full[1:2]+models))
    pinned=os.environ.get('GEMINI_MODEL','')
    if pinned in models:models=[pinned]+[m for m in models if m!=pinned]
    parts=[{'text':prompt}]
    if audio_part:parts.insert(0,audio_part)
    if extra_parts:parts=list(extra_parts)+parts
    config={'responseMimeType':'application/json','temperature':.15 if audio_part else .35,'maxOutputTokens':max_tokens}
    if schema:config['responseSchema']=schema
    raw=None
    attempts=[]
    for model in models[:3]:
        try:
            r=requests.post('https://generativelanguage.googleapis.com/v1beta/models/'+model+':generateContent',
                headers={'x-goog-api-key':key},json={'contents':[{'parts':parts}],
                'generationConfig':config},timeout=90)
        except requests.RequestException:continue
        attempts.append({'model':model,'http_status':r.status_code})
        if out:Path(out,tag+'_attempts.json').write_text(json.dumps(attempts,indent=2))
        if r.status_code==200:
            response_parts=(r.json().get('candidates') or [{}])[0].get('content',{}).get('parts',[])
            raw=''.join(p.get('text','') for p in response_parts if not p.get('thought'))
            if raw:break
        print('Planner unavailable:',model,'HTTP',r.status_code,flush=True)
    if not raw:raise RuntimeError('Planner unavailable after at most three discovered models')
    if out:Path(out,tag+'_response.txt').write_text(raw,encoding='utf-8')
    # Decode exactly the first complete object; trailing prose/duplicate objects
    # cannot make a valid package unparsable. The caller still validates fields.
    data=parse_object(raw)
    if out:Path(out,tag+'_raw.json').write_text(json.dumps(data,ensure_ascii=False,indent=2))
    return data
