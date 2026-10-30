"""Second directed version: a connected encounter, memory, room and written metaphor.
This authored sample demonstrates coverage; it is not universal backend evidence.
"""
import argparse,json,math,subprocess
from functools import lru_cache
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFilter,ImageChops
from . import poet_story_film as old
from .lyric_meaning_demo import ease,mix,put
from song_animation.lyrics import overlay,export_srt
W,H=540,960
ROOT=Path(__file__).parents[1]/'assets'/'poet_story_v2'
SHOTS=[(0,'encounter'),(3.5,'remembered_glance'),(7.5,'first_poem'),(10.5,'unspoken_distance'),(15,'poem_grows'),(17.5,'window_hesitation'),(23.5,'written_metaphor'),(26.5,'unmailed_letter')]

@lru_cache(None)
def asset(name):
    im=Image.open(ROOT/(name+'.webp')).convert('RGBA')
    if name in ('poet','woman'):im=im.crop(im.getchannel('A').point(lambda a:255 if a>10 else 0).getbbox())
    return im

@lru_cache(None)
def setting(name):return asset(name).resize((W,H),Image.Resampling.LANCZOS)

def cloth(obj,t,strength=2):
    # Local cloth deformation, while heads and feet retain their attachment.
    a=np.asarray(obj);h,w=a.shape[:2];yy,xx=np.mgrid[:h,:w]
    weight=np.clip((yy/h-.35)/.65,0,1)*np.clip((xx/w-.5)*2,0,1)
    sx=xx-np.rint(np.sin(yy*.026-t*2.2)*weight*strength).astype(int)
    out=a[yy,np.clip(sx,0,w-1)].copy();out[(sx<0)|(sx>=w)]=0
    return Image.fromarray(out)

def actor(im,name,x,y,height,t,alpha=1):
    obj=asset(name);width=height*obj.width/obj.height
    obj=cloth(obj,t,4 if name=='woman' else 1)
    # Foot pivot remains planted; breathing is confined to a tiny lean.
    old.anchored(im,obj,x,y,width,(.5,1),math.sin(t*1.2)*.22,alpha,True)

def petals(im,t,amount=9):
    d=ImageDraw.Draw(im)
    for j in range(amount):
        age=(t*.11+j*.137)%1;x=45+(j*79)%470+math.sin(t+j)*12;y=100+age*660
        if y>770:continue
        d.ellipse((x,y,x+3,y+1.8),fill=(178,63,98,130))

def courtyard(t,alone=False):
    im=setting('courtyard').copy()
    actor(im,'poet',174,793,410,t)
    # The remembered woman recedes through light; no unrelated person replaces her.
    alpha=1-ease((t-12.5)/2.4) if alone else ease(t/.5)
    actor(im,'woman',369,779,385,t,alpha)
    # Fountain ripples and falling petals are environment detail; not actor motion proof.
    d=ImageDraw.Draw(im)
    for j in range(4):
        r=((t*5+j*7)%28);d.arc((25-r,488-r*.12,65+r,490+r*.12),0,170,fill=(236,233,201,85),width=1)
    petals(im,t)
    return im

def glance(t):
    bg=setting('courtyard').filter(ImageFilter.GaussianBlur(4));q=ease((t-3.5)/4)
    # A separately staged close reaction, rather than a crop of the desk.
    actor(bg,'woman',310,1395,1120,t)
    petals(bg,t,5)
    return bg

def window(t):
    im=setting('balcony').copy();q=ease((t-17.5)/6)
    # The poet remains behind the foreground desk; his held blank sheet is occluded.
    actor(im,'poet',176,1040,750,t)
    # The actual desk foreground occludes the lower torso, preserving scene depth.
    foreground=setting('balcony').crop((0,666,W,H));mask=Image.new('L',foreground.size)
    ImageDraw.Draw(mask).polygon([(0,240),(195,69),(W,2),(W,H-666),(0,H-666)],fill=255)
    foreground.putalpha(mask);im.alpha_composite(foreground,(0,666))
    # Light curtain edge drifts independently of the letter.
    curtain=Image.new('RGBA',(W,H));cd=ImageDraw.Draw(curtain)
    for j in range(6):
        x=508+j*6+math.sin(t*1.2+j*.4)*3
        cd.line([(x,0),(x-12,280),(x+3,550),(x-25,745)],fill=(255,251,233,25),width=8)
    im.alpha_composite(curtain);return im

def ending(t):
    im=setting('balcony').copy()
    letter=old.page().copy();text=old.jam();letter.alpha_composite(text,(110,373))
    for j,words in enumerate(['तुम्हारी याद','अधूरी बात','खामोश मोहब्बत']):letter.alpha_composite(old.word_mask(words,23),(57,219+j*36))
    # A completed poem sits beside the window; the earlier blank letter has changed.
    put(im,letter,321,743,243,angle=-10+ease((t-26.5)/3.5)*1.2,shadow=True)
    petals(im,t,4);return im

def scene(t,index):
    if index==0:return courtyard(t)
    if index==1:return glance(t)
    if index==2:return old.inspired(t)
    if index==3:return courtyard(t,True)
    if index==4:return old.inspired(t)
    if index==5:return window(t)
    if index==6:return old.metaphor(t)
    return ending(t)

def frame(t,captions=True):
    index=max(i for i,(start,_) in enumerate(SHOTS) if t>=start)
    im=scene(t,index)
    age=t-SHOTS[index][0]
    if index and age<.18:im=Image.blend(scene(SHOTS[index][0]-.001,index-1),im,ease(age/.18))
    return overlay(im.convert('RGB'),old.PLAN,round(t*30)) if captions else im.convert('RGB')

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--audio',required=True);ap.add_argument('--out',required=True);args=ap.parse_args()
    out=Path(args.out);out.mkdir(parents=True,exist_ok=True)
    dur=min(29.988118,float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',args.audio])));n=round(dur*30)
    dest=out/'song_story_multiscene_30s.mp4'
    cmd=['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s','540x960','-r','30','-i','-','-i',args.audio,'-vf','scale=1080:1920:flags=lanczos','-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-t',str(dur),'-movflags','+faststart',str(dest)]
    p=subprocess.Popen(cmd,stdin=subprocess.PIPE)
    try:
        for f in range(n):
            p.stdin.write(frame(f/30).tobytes())
            if f%150==0:print('Render',f,'/',n,flush=True)
        p.stdin.close()
        if p.wait():raise RuntimeError('Video encoding failed')
    except BaseException:p.kill();p.wait();raise
    sheet=Image.new('RGB',(810,480*len(SHOTS)))
    for row,(start,label) in enumerate(SHOTS):
        end=SHOTS[row+1][0] if row+1<len(SHOTS) else dur
        for col,q in enumerate([.15,.5,.85]):sheet.paste(frame(start+(end-start)*q).resize((270,480)),(270*col,480*row))
    sheet.save(out/'contact.jpg',quality=92);export_srt(old.PLAN,out/'lyrics.srt')
    subprocess.run(['ffmpeg','-v','error','-xerror','-i',str(dest),'-f','null','-'],check=True)
    (out/'about.json').write_text(json.dumps({'kind':'authored multiscene update','shots':SHOTS,'original_visuals_used':False,'original_audio_preserved':True,'caption_timing':'approximate phrases','universal_automation_certified':False},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
