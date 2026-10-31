"""Bounded, cached access to the public FLUX Space; quota is never bypassed."""
import hashlib,io,json,os,time
from pathlib import Path
from urllib.parse import urlparse
from PIL import Image
from .provider import ProviderUnavailable

BASE='https://black-forest-labs-flux-1-schnell.hf.space'
SPACE='black-forest-labs/FLUX.1-schnell'

def generate_image(prompt,out,seed,width=768,height=1024):
    import requests
    if not isinstance(prompt,str) or not prompt.strip() or len(prompt)>8000:raise ValueError('Image prompt must be nonempty and bounded')
    if not all(isinstance(n,int) and 256<=n<=1536 and n%32==0 for n in (width,height)):raise ValueError('Image dimensions must be bounded multiples of 32')
    if not isinstance(seed,int) or not 0<=seed<2**31:raise ValueError('Image seed must fit signed int32')
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    params={'space':SPACE,'prompt':prompt,'seed':seed,'width':width,'height':height,'steps':4}
    key=hashlib.sha256(json.dumps(params,sort_keys=True).encode()).hexdigest()
    path=out/(key+'.png');record=out/(key+'.json')
    if path.exists() and record.exists():
        try:
            data=json.loads(record.read_text())
            if data.get('sha256')==hashlib.sha256(path.read_bytes()).hexdigest():
                with Image.open(path) as image:
                    image.load()
                    if image.size==(width,height):return path
        except (OSError,ValueError):pass
    session=requests.Session()
    token=os.environ.get('HF_TOKEN','').strip()
    if token:session.headers.update({'Authorization':'Bearer '+token})
    def unavailable(message,status=503):
        opaque=message is None
        message=str(message or 'Public image service returned an unspecified error')[:500]
        quota=any(s in message.lower() for s in ('quota','rate limit','usage limit','sign in','authenticate'))
        attempts=[{'model':SPACE,'http_status':429 if quota else status,'error_status':'image_generation_unavailable'}]
        if opaque:attempts=[{'model':SPACE,'error':'opaque_image_provider_failure'}]
        (out/'image_provider_hold.json').write_text(json.dumps({'reason':message,'attempts':attempts,'universal_quality_certified':False},indent=2))
        raise ProviderUnavailable(attempts)
    try:
        response=session.post(BASE+'/gradio_api/call/infer',json={'data':[prompt,seed,False,width,height,4]},timeout=25)
        if response.status_code!=200:unavailable('Image service HTTP '+str(response.status_code),response.status_code)
        event=response.json()['event_id'];kind=None;result=None;started=time.monotonic()
        with session.get(BASE+'/gradio_api/call/infer/'+event,stream=True,timeout=(20,45)) as stream:
            if stream.status_code!=200:unavailable('Image queue HTTP '+str(stream.status_code),stream.status_code)
            for line in stream.iter_lines():
                if time.monotonic()-started>240:unavailable('Image generation deadline exceeded')
                if not line:continue
                text=line.decode('utf-8')
                if text.startswith('event:'):kind=text[6:].strip()
                elif text.startswith('data:'):
                    payload=json.loads(text[5:])
                    if kind=='error':unavailable(payload)
                    if kind=='complete':result=payload;break
        if not result:unavailable('Image queue ended without a completed image')
        url=result[0]['url']
        if urlparse(url).scheme!='https' or urlparse(url).netloc!=urlparse(BASE).netloc:raise ValueError('Image result must stay on the configured public service')
        with session.get(url,stream=True,timeout=30) as download:
            download.raise_for_status();chunks=[];size=0
            for chunk in download.iter_content(65536):
                size+=len(chunk)
                if size>20_000_000:raise ValueError('Image download exceeds byte limit')
                chunks.append(chunk)
        with Image.open(io.BytesIO(b''.join(chunks))) as image:
            if image.size!=(width,height):raise ValueError('Image service changed requested dimensions')
            image.load();image=image.convert('RGB');temporary=path.with_suffix('.partial.png');image.save(temporary);temporary.replace(path)
        record.write_text(json.dumps(dict(params,sha256=hashlib.sha256(path.read_bytes()).hexdigest(),quality_certified=False),ensure_ascii=False,indent=2))
        return path
    except requests.RequestException:unavailable('Image service transport interruption')
    except (KeyError,TypeError,json.JSONDecodeError):unavailable('Image service protocol changed')
    finally:session.close()
