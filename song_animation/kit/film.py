"""Render a kit film: python -m song_animation.kit.film --audio song.m4a --out kit_out

audio -> 30 s clip (existing selector) -> Hindi phrases with timing (existing
analyze_audio) -> shots (director) -> code-drawn frames + captions + audio.
Every stage leaves a JSON record in --out so a rerun resumes cheaply.
"""
import argparse,json,math,subprocess,hashlib
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
from .art import W,H,SS,CW,CH,Canvas,outdoor,indoor,draw_object,effect,ease
from .director import direct

FPS=30;XF=.45

def make_grain(seed):
    rng=np.random.default_rng(seed);n=rng.normal(0,1,(H//2,W//2)).astype(np.float32)
    return np.asarray(Image.fromarray((128+n*22).clip(0,255).astype(np.uint8),'L').resize((W,H),Image.BILINEAR),dtype=np.float32)
GRAIN=[make_grain(s) for s in range(4)]
_y,_x=np.ogrid[:H,:W];VIG=(np.clip(1-.42*np.sqrt(((_x-W/2)/(W*.75))**2+((_y-H/2)/(H*.72))**2)**2.2,0,1)*.85+.15)[...,None].astype(np.float32)

class Renderer:
    def __init__(self,plan,captions=True):
        self.shots=plan['shots'];self.captions=captions;self.bg={}
        self.cues=[(l['start'],l['end'],l['text']) for s in self.shots for l in s['lines']]
    def background(self,i):
        if i not in self.bg:
            s=self.shots[i];self.bg[i]=outdoor(s['sky'],s['ground'],seed=i+1) if s['setting']=='outdoor' else indoor(s['wall'],s['light'],seed=i+1)
            if len(self.bg)>3:self.bg.pop(next(iter(self.bg)))
        return self.bg[i]
    def shot_image(self,i,t):
        s=self.shots[i];c=Canvas(self.background(i).copy())
        for o in s['objects']:draw_object(c,o,t,s['night'])
        for e in s['effects']:effect(c,e,t,s['night'])
        img=c.img.reduce(SS);p=t/max(.1,s['end']-s['start']);z={'push_in':1+.07*ease(p),'pull_out':1.07-.07*ease(p)}.get(s['camera'],1.06)
        cw,ch=int(W/z),int(H/z);pan={'pan_left':1-ease(p),'pan_right':ease(p)}.get(s['camera'],.5)
        ox=int((W-cw)*pan);oy=(H-ch)//2;return img.crop((ox,oy,ox+cw,oy+ch)).resize((W,H),Image.BICUBIC)
    def caption(self,img,t):
        from ..lyrics import font
        layer=Image.new('RGBA',(W,H),(0,0,0,0));d=ImageDraw.Draw(layer)
        for a,b,text in self.cues:
            if not a-.15<=t<=b+.15:continue
            alpha=max(0,min(1,(t-(a-.15))/.3,((b+.15)-t)/.3));words=text.split();lines=[text]
            size=60
            while True:
                f=font(size,text);wd=lambda s:d.textbbox((0,0),s,font=f)[2]-d.textbbox((0,0),s,font=f)[0]
                if wd(text)>W-120 and len(words)>3:half=len(words)//2;lines=[' '.join(words[:half]),' '.join(words[half:])]
                if max(wd(l) for l in lines)<=W-120 or size<=40:break
                size-=2
            y=1610-(len(lines)-1)*44
            for ln in lines:
                x=(W-wd(ln))//2
                for dx,dy in((0,4),(2,3),(-2,3)):d.text((x+dx,y+dy),ln,font=f,fill=(30,15,8,int(170*alpha)))
                d.text((x,y),ln,font=f,fill=(255,243,220,int(255*alpha)));y+=88
            break
        return Image.alpha_composite(img.convert('RGBA'),layer).convert('RGB')
    def frame(self,n,total):
        t=n/FPS;i=next((k for k,s in enumerate(self.shots) if t<s['end']),len(self.shots)-1);s=self.shots[i]
        img=self.shot_image(i,t-s['start'])
        if i+1<len(self.shots) and t>s['end']-XF:
            nx=self.shots[i+1];img=Image.blend(img,self.shot_image(i+1,max(0,t-nx['start'])),ease((t-(s['end']-XF))/XF))
        dur=total/FPS
        if t<.5:img=Image.blend(Image.new('RGB',(W,H),(20,10,6)),img,ease(t/.5))
        if t>dur-.8:img=Image.blend(img,Image.new('RGB',(W,H),(20,10,6)),ease((t-(dur-.8))/.8))
        a=np.asarray(img,dtype=np.float32);g=(GRAIN[n//3%4]-128)/128
        img=Image.fromarray((a*(1+g[...,None]*.07)*VIG).clip(0,255).astype(np.uint8),'RGB')
        return self.caption(img,t) if self.captions else img

def render(plan,clip,out,duration,captions=True,stills=None):
    r=Renderer(plan,captions);out=Path(out);out.mkdir(parents=True,exist_ok=True);total=int(round(duration*FPS))
    if stills:
        for s in stills:r.frame(int(s*FPS),total).save(out/f'still_{s:05.2f}.jpg',quality=88)
        return
    video=out/'kit_film.mp4'
    p=subprocess.Popen(['ffmpeg','-y','-v','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-i',str(clip),
        '-map','0:v','-map','1:a','-c:v','libx264','-preset','medium','-crf','19','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k',
        '-af',f'afade=t=out:st={max(0,duration-.8):.2f}:d=0.8','-t',f'{duration:.3f}','-movflags','+faststart',str(video)],stdin=subprocess.PIPE)
    for n in range(total):
        p.stdin.write(r.frame(n,total).tobytes())
        if n%150==0:print('frame',n,'/',total,flush=True)
    p.stdin.close()
    if p.wait():raise RuntimeError('ffmpeg encode failed')
    for s in (1.5,duration*.35,duration*.65,duration-2):r.frame(int(s*FPS),total).save(out/f'still_{s:05.2f}.jpg',quality=85)
    return video

def lyrics_for(clip,out,waits=(60,180,420,600)):
    """Strict checked lyrics when possible; otherwise the model's first hearing without captions.

    A busy model (HTTP 5xx) is waited out with growing pauses (~21 min in all);
    a daily-quota block (429 everywhere) stops at once and the daily retry picks it up.
    """
    import time
    from ..audio_lyrics import analyze_audio
    from ..provider import ProviderUnavailable
    for attempt in range(len(waits)+1):
        try:return analyze_audio(clip,out),True
        except ProviderUnavailable as error:
            codes={a.get('http_status') for a in getattr(error,'attempts',[]) if isinstance(a,dict)}
            if attempt==len(waits) or (codes and codes<= {429,404}):last=error;break
            print(f'Model busy {sorted(c for c in codes if c)}; waiting {waits[attempt]} s before retry {attempt+1}',flush=True);time.sleep(waits[attempt])
        except Exception as error:last=error;break
    error=last
    print('Checked lyrics unavailable:',str(error)[:300],flush=True)
    try:
        cand=json.loads((Path(out)/'audio_candidate.json').read_text()).get('data',{})
        words=[{'start':float(s['start']),'end':float(s['end']),'text':str(s.get('text','')).strip()} for s in cand.get('segments',[]) if str(s.get('text','')).strip()]
        if words:return {'words':words,'mood':cand.get('mood',''),'summary':cand.get('summary',''),'language':cand.get('language','')},False
    except (OSError,ValueError,KeyError,TypeError):pass
    raise error

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--audio',required=True);ap.add_argument('--out',default='kit_out')
    ap.add_argument('--lyrics',help='use this lyrics.json (timed to the clip) instead of the model');ap.add_argument('--no-model',action='store_true')
    ap.add_argument('--stills',default='');ap.add_argument('--start',type=float)
    a=ap.parse_args();out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
    from ..clip import prepare
    clip,sel=prepare(a.audio,out,limit=30,start=a.start);dur=float(sel['duration'])
    key=hashlib.sha256(Path(clip).read_bytes()).hexdigest()[:16];cache=out/'kit_lyrics.json'
    if a.lyrics:lyr=json.loads(Path(a.lyrics).read_text());checked=True
    elif cache.exists() and json.loads(cache.read_text()).get('key')==key and json.loads(cache.read_text()).get('checked'):saved=json.loads(cache.read_text());lyr,checked=saved['lyrics'],saved['checked']
    else:
        lyr,checked=lyrics_for(clip,out);cache.write_text(json.dumps({'key':key,'lyrics':lyr,'checked':checked},ensure_ascii=False))
    words=[{'start':float(w['start']),'end':float(w['end']),'text':w['text']} for w in lyr.get('words',[])]
    plan=direct(words,dur,lyr,out=out,use_model=not a.no_model)
    if not checked:
        for s in plan['shots']:s['lines_hidden']=s['lines'];s['lines']=[]  # unverified words never become captions
    plan.update(audio=str(a.audio),clip_start=sel.get('start'),duration=dur,captions_checked=checked)
    (out/'kit_plan.json').write_text(json.dumps(plan,ensure_ascii=False,indent=1))
    print('Director:',plan['source'],'| shots:',len(plan['shots']),'| captions:',checked,flush=True)
    for s in plan['shots']:print(f"  {s['start']:5.1f}-{s['end']:5.1f} {s['setting']:7s} {s['sky'] if s['setting']=='outdoor' else s['wall']:7s} {[o['name'] for o in s['objects']]} {s['effects']} | {s['text'][:60]}",flush=True)
    stills=[float(x) for x in a.stills.split(',') if x]
    video=render(plan,clip,out,dur,captions=True,stills=stills or None)
    if video:print('wrote',video,flush=True)

if __name__=='__main__':main()
