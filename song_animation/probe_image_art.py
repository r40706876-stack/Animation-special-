"""Bounded capability check for the existing Gemini key; never logs credentials.
Uses documented native IMAGE output, at most two discovered image models.
This is a backend probe, not proof of an automatic finished music video.
Docs: https://ai.google.dev/gemini-api/docs/generate-content/image-generation
"""
import base64,json,os,re
from pathlib import Path
import requests

def main():
 out=Path('image_art_probe');out.mkdir(exist_ok=True)
 key=os.environ.get('GEMINI_API_KEY','');report={'available':False,'attempts':[]}
 if not key:report['reason']='missing_key'
 else:
  headers={'x-goog-api-key':key}
  r=requests.get('https://generativelanguage.googleapis.com/v1beta/models',headers=headers,params={'pageSize':1000},timeout=30)
  r.raise_for_status()
  models=[m['name'].removeprefix('models/') for m in r.json().get('models',[]) if 'generateContent' in m.get('supportedGenerationMethods',[]) and any(x in m['name'] for x in ('image','banana')) and 'tts' not in m['name']]
  models=sorted(models,key=lambda m:('lite' not in m,'preview' in m,m))
  report['discovered_models']=models
  prompt='Create a premium botanical editorial illustration: a richly detailed crimson rose with organically curled petals, finely engraved ink contours and watercolor depth. Three-quarter overhead view, isolated single rose with short stem and two leaves, genuine transparent background if supported, no text or watermark, not a flat geometric icon. This artwork will be independently animated to illustrate the Hindi metaphor that flowers can cause emotional wounds.'
  for model in models[:2]:
   try:
    r=requests.post('https://generativelanguage.googleapis.com/v1/models/'+model+':generateContent',headers=headers,json={'contents':[{'parts':[{'text':prompt}]}],'generationConfig':{'responseModalities':['TEXT','IMAGE']}},timeout=120)
    item={'model':model,'http_status':r.status_code};report['attempts'].append(item)
    if r.status_code!=200:continue
    for candidate in r.json().get('candidates',[]):
     for part in candidate.get('content',{}).get('parts',[]):
      blob=part.get('inlineData',part.get('inline_data',{}));mime=blob.get('mimeType',blob.get('mime_type',''))
      if mime in ('image/png','image/jpeg') and blob.get('data'):
       raw=base64.b64decode(blob['data'],validate=True)
       if len(raw)>20000000:raise ValueError('Image exceeds bounded output size')
       p=out/('artwork.png' if mime=='image/png' else 'artwork.jpg');p.write_bytes(raw)
       from PIL import Image
       im=Image.open(p);im.verify();report.update(available=True,model=model,file=p.name)
       break
     if report['available']:break
    if report['available']:break
   except (requests.RequestException,ValueError) as e:report['attempts'].append({'model':model,'error_type':type(e).__name__})
  if not report['available']:report['reason']='No usable native image output from at most two discovered models'
 (out/'capability.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
if __name__=='__main__':main()
