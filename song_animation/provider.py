"""Bounded provider transport; safe diagnostics, no model code execution."""
import json,os,time
from pathlib import Path

class ProviderUnavailable(RuntimeError):
    def __init__(self,attempts):
        super().__init__('No usable model response; provider quota or service availability blocked this stage')
        self.attempts=attempts
        delays=[]
        for item in attempts:
            try:delays.append(float(str(item.get('retry_delay','0s')).removesuffix('s')))
            except ValueError:pass
        self.retry_after_seconds=max(delays,default=0)

def parse_object(raw):
    start=raw.find('{')
    if start<0:raise ValueError('Provider returned no JSON object')
    data,_=json.JSONDecoder().raw_decode(raw[start:])
    if not isinstance(data,dict):raise ValueError('Provider response must be an object')
    return data

def generate_json(prompt,out=None,tag="planner",audio_part=None,schema=None,extra_parts=None,max_tokens=32768,prefer_quality=False,require_full_model=False,timeout_seconds=90,thinking_level=None):
    import requests
    key=os.environ.get('GEMINI_API_KEY','').strip()
    if not key:raise RuntimeError('GEMINI_API_KEY is missing')
    # Discover actual available models; never retry a retired model indefinitely.
    try:
        listing=requests.get('https://generativelanguage.googleapis.com/v1beta/models',headers={'x-goog-api-key':key},params={'pageSize':1000},timeout=25)
        listing.raise_for_status()
        models=[m['name'].removeprefix('models/') for m in listing.json().get('models',[]) if 'generateContent' in m.get('supportedGenerationMethods',[]) and ('flash' in m['name'] or (prefer_quality and 'pro' in m['name'])) and not any(x in m['name'] for x in ('image','tts','audio','live','robotics'))]
    except requests.RequestException:raise ProviderUnavailable([{'error':'model_discovery_unavailable'}]) from None
    import re
    def rank(m):
        v=re.search(r'gemini-(\d+(?:\.\d+)?)',m)
        return ('preview' in m or 'exp' in m, 'lite' not in m, -float(v.group(1)) if v else 0,m)
    models=sorted(set(models),key=rank)
    if prefer_quality:
        full=[m for m in models if 'lite' not in m]
        lite=[m for m in models if 'lite' in m]
        pro=[m for m in full if 'pro' in m]
        flash=[m for m in full if 'flash' in m]
        models=list(dict.fromkeys(pro[:1]+flash[:1]+lite[:1]+models))
    if require_full_model:models=[m for m in models if 'lite' not in m.lower()]
    if prefer_quality:
        preference_file=Path(__file__).with_name('provider_preferences.json')
        if preference_file.is_file():
            preferred=json.loads(preference_file.read_text()).get('preferred_full_models',[])
            known=[m for m in preferred if m in models and 'lite' not in m.lower()]
            models=list(dict.fromkeys(known+models))
    pinned=os.environ.get('GEMINI_MODEL','')
    if pinned in models:models=[pinned]+[m for m in models if m!=pinned]
    parts=[{'text':prompt}]
    if audio_part:parts.insert(0,audio_part)
    if extra_parts:parts=list(extra_parts)+parts
    config={'responseMimeType':'application/json','temperature':.15 if audio_part else .35,'maxOutputTokens':max_tokens}
    if schema:config['responseSchema']=schema
    raw=None
    attempts=[]
    for model_index,model in enumerate(models[:3]):
        model_config=dict(config)
        if thinking_level:
            if re.match(r'gemini-[3-9](?:\.|-)',model):model_config['thinkingConfig']={'thinkingLevel':thinking_level}
            elif model.startswith('gemini-2.5-'):model_config['thinkingConfig']={'thinkingBudget':2048}
        # One transient retry for the preferred available model. Never spin on
        # exhausted quota, auth failures or an actually retired model.
        for retry in range(2 if model_index==0 else 1):
            try:
                r=requests.post('https://generativelanguage.googleapis.com/v1beta/models/'+model+':generateContent',
                    headers={'x-goog-api-key':key},json={'contents':[{'parts':parts}],
                    'generationConfig':model_config},timeout=max(30,min(180,timeout_seconds)))
            except requests.RequestException:
                attempts.append({'model':model,'error':'transport','retry':retry})
                if out:Path(out,tag+'_attempts.json').write_text(json.dumps(attempts,indent=2))
                if retry==0 and model_index==0:time.sleep(3);continue
                break
            item={'model':model,'http_status':r.status_code,'retry':retry}
            if r.status_code!=200:
                try:
                    body=r.json()
                    error=body.get('error',{}) if isinstance(body,dict) else {}
                    if not isinstance(error,dict):error={}
                    if isinstance(error.get('status'),str):item['error_status']=error['status']
                    for detail in error.get('details',[]):
                        if not isinstance(detail,dict):continue
                        if isinstance(detail.get('retryDelay'),str):item['retry_delay']=detail['retryDelay']
                        limits=[{k:v[k] for k in ('quotaId','quotaValue') if k in v} for v in detail.get('violations',[]) if isinstance(v,dict)]
                        if limits:item['quota_limits']=limits[:6]
                except (ValueError,TypeError):pass
            attempts.append(item)
            if out:Path(out,tag+'_attempts.json').write_text(json.dumps(attempts,indent=2))
            if r.status_code==200:
                body=r.json();candidate=(body.get('candidates') or [{}])[0]
                response_parts=candidate.get('content',{}).get('parts',[])
                raw=''.join(p.get('text','') for p in response_parts if not p.get('thought'))
                if out:
                    Path(out,tag+'_response_meta.json').write_text(json.dumps({'model':model,'finish_reason':candidate.get('finishReason'),'usage':body.get('usageMetadata',{})},indent=2))
                    Path(out,tag+'_response.txt').write_text(raw,encoding='utf-8')
                if candidate.get('finishReason') not in (None,'STOP'):
                    raise ValueError('Provider response incomplete: '+str(candidate['finishReason'])+'. Regenerate a smaller complete package; never repair by closing truncated JSON.')
                break
            print('Planner unavailable:',model,'HTTP',r.status_code,flush=True)
            if r.status_code in (408,500,502,503,504) and retry==0 and model_index==0:
                time.sleep(3);continue
            break
        if raw:break
    if not raw:raise ProviderUnavailable(attempts)
    if out:Path(out,tag+'_response.txt').write_text(raw,encoding='utf-8')
    # Decode exactly the first complete object; trailing prose/duplicate objects
    # cannot make a valid package unparsable. The caller still validates fields.
    data=parse_object(raw)
    data['_provider_model']=model
    if out:Path(out,tag+'_raw.json').write_text(json.dumps(data,ensure_ascii=False,indent=2))
    return data
