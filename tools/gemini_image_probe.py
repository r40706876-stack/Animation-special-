"""One-off check: can this GEMINI_API_KEY generate images for free? Prints facts only."""
import base64,json,os,sys,requests
key=os.environ['GEMINI_API_KEY'].strip();H={'x-goog-api-key':key}
B='https://generativelanguage.googleapis.com/v1beta/'
models=requests.get(B+'models',headers=H,params={'pageSize':1000},timeout=30).json().get('models',[])
image=[m for m in models if any(w in m['name'] for w in ('image','imagen'))]
print('IMAGE MODELS VISIBLE:',[m['name'].split('/')[-1]+' '+','.join(m.get('supportedGenerationMethods',[])) for m in image])
prompt='Warm watercolor illustration of an Indian village clay stove (chulha) at dusk, brass pots, soft lamp light, no people, vertical.'
ok=False
for m in image:
    name=m['name'].split('/')[-1];methods=m.get('supportedGenerationMethods',[])
    if 'generateContent' in methods:
        r=requests.post(B+'models/'+name+':generateContent',headers=H,timeout=120,json={'contents':[{'parts':[{'text':prompt}]}],'generationConfig':{'responseModalities':['TEXT','IMAGE']}})
    elif 'predict' in methods:
        r=requests.post(B+'models/'+name+':predict',headers=H,timeout=120,json={'instances':[{'prompt':prompt}],'parameters':{'sampleCount':1}})
    else:continue
    got=False
    if r.status_code==200:
        text=json.dumps(r.json());got='inlineData' in text or 'bytesBase64Encoded' in text
        if got:
            d=r.json()
            data=(d.get('predictions') or [{}])[0].get('bytesBase64Encoded') or next(p['inlineData']['data'] for p in d['candidates'][0]['content']['parts'] if 'inlineData' in p)
            os.makedirs('probe_out',exist_ok=True);open('probe_out/'+name+'.png','wb').write(base64.b64decode(data))
    err='' if r.status_code==200 else r.text[:300].replace('\n',' ')
    print('RESULT',name,'HTTP',r.status_code,'IMAGE_RETURNED' if got else 'NO_IMAGE',err)
    ok=ok or got
print('VERDICT: FREE IMAGE GENERATION WORKS' if ok else 'VERDICT: NO FREE IMAGE GENERATION ON THIS KEY')
