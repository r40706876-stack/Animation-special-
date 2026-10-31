"""Directed 30s sample using a real FLUX cutout. Not universal automation evidence."""
import argparse,json,math,subprocess
from functools import lru_cache
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
from . import poet_multiscene as v2
from . import poet_story_film as old
from .lyric_meaning_demo import ease,put
from song_animation.lyrics import overlay,export_srt
W,H=540,960
SHOTS=[(0,'encounter'),(3.4,'remembered_glance'),(6.6,'first_poem'),(9.8,'unspoken_distance'),(13.1,'poem_grows'),(16.4,'window_hesitation'),(19.9,'unspoken_line'),(23.3,'written_metaphor'),(26.6,'unmailed_letter')]
CUES=[(0,3.4,'आ...'),(3.4,6.6,'हमको किसी के हुस्न ने'),(6.6,9.8,'शायर बना दिया'),(9.8,13.1,'हमको किसी के हुस्न ने'),(13.1,16.4,'शायर बना दिया'),(16.4,19.9,'होंठों का नाम ले न सके'),(19.9,23.3,'होंठों का नाम ले न सके'),(23.3,26.6,'जाम लिख दिया'),(26.6,29.988118,'होंठों का नाम ले न सके')]
PLAN={'fps':30,'lyrics':[{'start_frame':round(s*30),'end_frame':round(e*30),'text':t} for s,e,t in CUES]}

@lru_cache(None)
def poet():return Image.open(Path(__file__).parents[1]/'assets/poet_story_v3/poet.webp').convert('RGBA')

def breathe(image,t):
    # Continuous local head lean tapers to zero at the neck; feet stay planted.
    a=np.asarray(image);h,w=a.shape[:2];yy,xx=np.mgrid[:h,:w]
    head=np.clip((h*.36-yy)/(h*.31),0,1)
    cloth=np.clip((yy/h-.42)/.58,0,1)*np.clip((xx/w-.45)*2,0,1)
    shift=np.rint(math.sin(t*1.05)*9*head+np.sin(yy*.026-t*1.8)*cloth*3).astype(int)
    sx=xx-shift;result=a[yy,np.clip(sx,0,w-1)].copy();result[(sx<0)|(sx>=w)]=0
    return Image.fromarray(result)

def actor(im,x,y,height,t):
    image=breathe(poet(),t);old.anchored(im,image,x,y,height*image.width/image.height,(.5,1),math.sin(t*.9)*.15,1,True)

def courtyard(t,alone=False):
    im=v2.setting('courtyard').copy();actor(im,166,794,346,t)
    alpha=1-ease((t-11.0)/2.0) if alone else ease(t/.55)
    v2.actor(im,'woman',369,779,385,t,alpha);v2.petals(im,t)
    d=ImageDraw.Draw(im)
    for j in range(4):
        r=(t*5+j*7)%28;d.arc((25-r,488-r*.12,65+r,490+r*.12),0,170,fill=(236,233,201,85),width=1)
    return im

def window(t):
    im=v2.setting('balcony').copy();actor(im,179,1050,770,t)
    foreground=v2.setting('balcony').crop((0,666,W,H));mask=Image.new('L',foreground.size)
    ImageDraw.Draw(mask).polygon([(0,240),(195,69),(W,2),(W,H-666),(0,H-666)],fill=255)
    foreground.putalpha(mask);im.alpha_composite(foreground,(0,666))
    curtain=Image.new('RGBA',(W,H));d=ImageDraw.Draw(curtain)
    for j in range(6):
        x=508+j*6+math.sin(t*1.2+j*.4)*3;d.line([(x,0),(x-12,280),(x+3,550),(x-25,745)],fill=(255,251,233,25),width=8)
    im.alpha_composite(curtain);return im

def scene(t,index):
    if index==0:return courtyard(t)
    if index==1:return v2.glance(3.5+(t-3.4)*4/3.2)
    if index==2:return old.inspired(7.6+(t-6.6)*2.05/3.2)
    if index==3:return courtyard(t,True)
    if index==4:return old.inspired(12.2+(t-13.1)*2.05/3.3)
    if index==5:return window(t)
    if index==6:return old.hesitant(19.5+(t-19.9)*4/3.4)
    if index==7:return old.metaphor(23.5+(t-23.3)*3/3.3)
    return v2.ending(26.5+(t-26.6)*3.4/3.388118)

def frame(t,captions=True):
    index=max(i for i,(s,_) in enumerate(SHOTS) if t>=s);im=scene(t,index)
    age=t-SHOTS[index][0]
    if index and age<.18:im=Image.blend(scene(SHOTS[index][0]-.001,index-1),im,ease(age/.18))
    return overlay(im.convert('RGB'),PLAN,round(t*30)) if captions else im.convert('RGB')

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--audio',required=True);ap.add_argument('--out',required=True);args=ap.parse_args()
    out=Path(args.out);out.mkdir(parents=True,exist_ok=True);duration=29.988118
    dest=out/'song_story_30s_v3.mp4'
    p=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s','540x960','-r','30','-i','-','-i',args.audio,'-vf','scale=1080:1920:flags=lanczos','-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-t',str(duration),'-movflags','+faststart',str(dest)],stdin=subprocess.PIPE)
    try:
        for f in range(round(duration*30)):
            p.stdin.write(frame(f/30).tobytes())
            if f%150==0:print('Render',f,'/',900,flush=True)
        p.stdin.close()
        if p.wait():raise RuntimeError('Encoding failed')
    except BaseException:p.kill();p.wait();raise
    sheet=Image.new('RGB',(810,480*len(SHOTS)))
    for row,(start,_) in enumerate(SHOTS):
        end=SHOTS[row+1][0] if row+1<len(SHOTS) else duration
        for col,q in enumerate((.15,.5,.85)):sheet.paste(frame(start+(end-start)*q).resize((270,480)),(270*col,row*480))
    sheet.save(out/'contact.jpg',quality=94);export_srt(PLAN,out/'lyrics.srt')
    (out/'about.json').write_text(json.dumps({'kind':'directed source-specific updated film','shots':SHOTS,'image_backend':'FLUX public Space plus existing original approved artwork','source_audio_only':True,'caption_timing':'approximate phrases','universal_automation_certified':False},ensure_ascii=False,indent=2))
    subprocess.run(['ffmpeg','-v','error','-xerror','-i',str(dest),'-f','null','-'],check=True)

if __name__=='__main__':main()
