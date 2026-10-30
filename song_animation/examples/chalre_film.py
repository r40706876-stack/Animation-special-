"""Authored film for the supplied recording; not a universal automation proof.
Coherent illustrated character, independent cloth and moving town/admiration layers.
"""
import argparse,json,math,subprocess
from pathlib import Path
from functools import lru_cache
import numpy as np
from PIL import Image,ImageDraw,ImageFilter,ImageFont
from song_animation.examples.lyric_meaning_demo import paper,put,ease,mix
from song_animation.art import curve
from song_animation.lyrics import overlay,export_srt,font
W,H=540,960
ROOT=Path(__file__).parents[1]/'assets'/'chalre_demo'
CUES=[(0,3.28,'Jha-jha te, har jha te'),(3.48,6.81,'Paye dende lok misaal'),(7.14,9.7,'Chalre-chalre waal'),(9.86,11.12,'Mondhe rakhdae…')]
PLAN={'fps':30,'lyrics':[{'start_frame':round(a*30),'end_frame':round(b*30),'text':s} for a,b,s in CUES]}
@lru_cache(None)
def a(name):
 im=Image.open(ROOT/(name+'.webp')).convert('RGBA');return im.crop(im.getchannel('A').getbbox())
@lru_cache(None)
def town():
 im=paper().copy();d=ImageDraw.Draw(im)
 # Quiet sunlit layered town, leaving the principal face clear.
 for x,y,w,h in [(-40,230,160,470),(400,170,180,550),(70,315,140,420),(330,320,120,430)]:
  d.rounded_rectangle((x,y,x+w,y+h),radius=6,fill='#e8d8b8',outline='#c8ae8b',width=1)
  for yy in range(y+45,y+h-20,105):
   for xx in range(x+22,x+w-20,47):
    d.rounded_rectangle((xx,yy,xx+27,yy+57),radius=13,fill='#c9b08c',outline='#eaddc3',width=2)
    d.line((xx+13,yy+5,xx+13,yy+52),fill='#b59772',width=1)
  d.line((x,y+18,x+w,y+18),fill='#f8edda',width=4)
 for y in range(690,960,24):
  d.line((0,y,540,y),fill='#dfcaa4',width=1)
  for x in range(-40+(y%48),540,74):d.line((x,y,x-10,y+24),fill='#dfcaa4',width=1)
 return im

@lru_cache(None)
def hero_base():
 im=a('hero');return im.resize((480,round(im.height*480/im.width)),Image.Resampling.LANCZOS)
def moving_hero(t):
 im=hero_base();arr=np.asarray(im);h,w=arr.shape[:2];yy,xx=np.mgrid[:h,:w]
 weight=np.clip(1-yy/(h*.28),0,1)**2
 source_x=xx-np.rint(np.sin(yy*.11+t*2.2)*weight*2.3).astype(int)
 valid=(source_x>=0)&(source_x<w);out=np.zeros_like(arr);out[valid]=arr[yy[valid],source_x[valid]]
 return Image.fromarray(out)

def portrait(t,width=1,center=(270,475)):
 layer=Image.new('RGBA',(W,H));s=width;cx,cy=center
 breath=math.sin(t*1.4)*1.8
 # One coherent anatomy asset; loose cloth/curls/observers move independently.
 put(layer,moving_hero(t),cx,cy,480*s,angle=math.sin(t*.8)*.65,shadow=False)
 return layer

def admirer(im,x,y,side,t,scale=1):
 """Small secondary engraved figures, gazing and gesturing at the hero."""
 d=ImageDraw.Draw(im);s=scale;bob=math.sin(t*1.7+x)*1.8
 def p(xx,yy):return (x+xx*s,y+(yy+bob)*s)
 color='#816d58';skin='#bc9071';cloth='#c9b598'
 d.polygon([p(-17,20),p(13,20),p(23,90),p(-24,90)],fill=cloth,outline=color)
 d.ellipse((*p(-13,-13),*p(13,17)),fill=skin,outline=color,width=1)
 d.arc((*p(-14,-17),*p(13,11)),180,355,fill='#55483e',width=5)
 d.line([p(-11,88),p(-15,136)],fill=color,width=6);d.line([p(10,88),p(14,136)],fill=color,width=6)
 q=math.sin(t*1.8+x)*7
 d.line([p(side*12,30),p(side*33,43),p(side*45,13+q)],fill=color,width=5)
 d.ellipse((*p(side*45-3,9+q),*p(side*45+3,15+q)),fill=skin)
 d.line([p(-side*12,29),p(-side*19,74)],fill=color,width=4)
 # Profile eye faces the hero rather than the camera.
 ex=x+side*6*s;ey=y+(1+bob)*s;d.ellipse((ex,ey,ex+2,ey+2),fill='#4c4035')

def curls(im,t,cx=255,cy=190,scale=1):
 d=ImageDraw.Draw(im)
 for j in range(5):
  x=cx+(j-2)*22*scale;y=cy+abs(j-2)*7*scale
  wind=math.sin(t*2+j*.7)*4*scale
  pts=curve([(x,y),(x+20*scale+wind,y-25*scale),(x-17*scale,y-29*scale),(x-6*scale+wind,y-5*scale)],35)
  d.line(pts,fill='#48372c',width=max(1,round(1.4*scale)))
  d.line([(xx,yy-1) for xx,yy in pts],fill='#6f5740',width=1)

def cloth(t,width=400):
 # Spatially varying deformation; the shoulder attachment stays fixed.
 im=a('shawl');h=round(im.height*width/im.width);im=im.resize((int(width),h),Image.Resampling.LANCZOS)
 arr=np.asarray(im);yy,xx=np.mgrid[:h,:int(width)];strength=(xx/max(1,width-1))**1.5
 shift=np.rint(np.sin(xx*.018-t*2.5)*strength*10).astype(int)
 sy=yy-shift;valid=(sy>=0)&(sy<h);out=np.zeros_like(arr);out[valid]=arr[sy[valid],xx[valid]]
 return Image.fromarray(out)

def base(t):
 im=town().copy();d=ImageDraw.Draw(im)
 sunx=250+math.sin(t*.2)*20
 d.ellipse((sunx-112,95,sunx+112,319),fill='#f1d49b')
 for j in range(10):
  x=(j*67+t*(10+j%3))%620-40;y=200+j*48+math.sin(t+j)*12
  d.ellipse((x,y,x+2,y+2),fill='#d3af70')
 return im

def shot0(t):
 im=base(t)
 admirer(im,55,490,1,t,.84);admirer(im,481,535,-1,t,.88)
 im.alpha_composite(portrait(t,1,(270,473)))
 return im

def shot1(t):
 im=base(t)
 for x,y,side,s in [(41,408,1,.85),(487,395,-1,.8),(64,625,1,1.15),(475,641,-1,1.12)]:admirer(im,x,y,side,t,s)
 im.alpha_composite(portrait(t,.88,(270,460)))
 # Thin admiration trails connect the observers' gaze to the admired person.
 d=ImageDraw.Draw(im)
 for j,(x,y) in enumerate([(70,460),(473,450)]):
  pts=curve([(x,y),(160 if j==0 else 380,y-20),(180 if j==0 else 350,320),(224 if j==0 else 322,300)],50)
  count=round(ease((t-3.48)/.8)*len(pts))
  if count>1:d.line(pts[:count],fill='#c19a57',width=1)
 return im

def shot2(t):
 im=paper().copy();d=ImageDraw.Draw(im)
 d.ellipse((-125,50,650,825),fill='#efdbb4',outline='#d1b884',width=1)
 layer=portrait(t,1.95,(275,720));im.alpha_composite(layer)
 # Fine wind lines move past the independently animated curls.
 for j in range(3):
  x=40+((t*35+j*83)%150);y=110+j*75
  d.line(curve([(x,y),(x+26,y-12),(x+45,y+9),(x+72,y-2)]),fill='#d2b985',width=1)
 return im

def shot3(t):
 im=base(t);im.alpha_composite(portrait(t,1.08,(243,484)))
 q=ease((t-9.8)/.9)
 tail=cloth(t,260)
 # A single loose end extends from the viewer-right shoulder; fringes flutter.
 tail.putalpha(tail.getchannel('A').point(lambda a:int(a*q)))
 im.alpha_composite(tail,(326,418))
 # Foreground olive leaves cross slowly for depth without obscuring eyes.
 d=ImageDraw.Draw(im)
 for j in range(5):
  x=20+j*10+math.sin(t+j)*3;y=690+j*24
  d.line((0,820,x+20,y),fill='#88784d',width=2)
  d.ellipse((x-7,y-15,x+6,y+15),fill='#a7a17b',outline='#7f7d5a')
 return im
SHOTS=[(0,shot0),(3.4,shot1),(6.98,shot2),(9.78,shot3)]
def frame(t,captions=True):
 index=max(i for i,(start,_) in enumerate(SHOTS) if t>=start)
 im=SHOTS[index][1](t)
 # Short soft edits, never whole-scene perpetual pans.
 if index and t-SHOTS[index][0]<.16:
  im=Image.blend(SHOTS[index-1][1](t),im,ease((t-SHOTS[index][0])/.16))
 im=im.convert('RGB')
 if captions:
  im=overlay(im,PLAN,round(t*30))
  cue=next((c for c in PLAN['lyrics'] if c['start_frame']<=round(t*30)<c['end_frame']),None)
  if cue:
   meaning='जहाँ जाओ, लोग तुम्हारी मिसाल देते हैं' if t<7 else ('घुँघराले-घुँघराले बाल' if t<9.8 else 'कंधे पर रखे हो…')
   d=ImageDraw.Draw(im);f=font(18,meaning);w=d.textlength(meaning,font=f);d.text(((540-w)/2,858),meaning,font=f,fill='#6f5743')
 return im

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--audio',required=True);ap.add_argument('--out',required=True);args=ap.parse_args();out=Path(args.out);out.mkdir(parents=True,exist_ok=True)
 dur=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',args.audio]));n=round(dur*30)
 cmd=['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s','540x960','-r','30','-i','-','-i',args.audio,'-vf','scale=1080:1920:flags=lanczos','-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-t',str(dur),'-movflags','+faststart',str(out/'chalre_corrected.mp4')]
 proc=subprocess.Popen(cmd,stdin=subprocess.PIPE)
 for f in range(n):proc.stdin.write(frame(f/30).tobytes())
 proc.stdin.close()
 if proc.wait():raise RuntimeError('Video encoder failed')
 sheet=Image.new('RGB',(810,480*4),'#fff8e8')
 for row,(start,_) in enumerate(SHOTS):
  end=SHOTS[row+1][0] if row+1<len(SHOTS) else dur
  for col,q in enumerate([.15,.5,.85]):sheet.paste(frame(start+(end-start)*q).resize((270,480)),(col*270,row*480))
 sheet.save(out/'contact.jpg',quality=90);export_srt(PLAN,out/'lyrics.srt')
 (out/'about.json').write_text(json.dumps({'kind':'authored supplied-song correction','duration':dur,'song_match':'Chalre Chalre Waal','language':'Saraiki (Roman transliteration captions)','timing_verified':False,'caption_note':'Phrase timing is approximate; last audible line is incomplete and not extended with words from the full song.','independent_layers':['coherent character','cloth with spatial deformation','subtle hair deformation','admiring figures','town','foreground leaves'],'universal_automation_certified':False},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
