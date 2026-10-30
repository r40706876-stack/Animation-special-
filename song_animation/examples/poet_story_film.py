"""Authored connected film for supplied song 1000076620, original audio only.
The main event is writing a metaphor, not drinking. Not a universal automation proof.
"""
import argparse,copy,json,math,subprocess
from pathlib import Path
from functools import lru_cache
import numpy as np
from PIL import Image,ImageDraw,ImageFilter
from song_animation.examples.lyric_meaning_demo import paper,ease,mix,put
from song_animation.art import curve
from song_animation.lyrics import overlay,font,export_srt
W,H=540,960
ROOT=Path(__file__).parents[1]/'assets'/'poet_story'
CUES=[(3.5,5.5,'हमको किसी के'),(5.5,7.5,'हुस्न ने'),(7.5,10.5,'शायर बना दिया'),(10.5,13,'हमको किसी के'),(13,15,'हुस्न ने'),(15,17.5,'शायर बना दिया'),(17.5,20.5,'होंठों का नाम ले न सके'),(20.5,23.5,'होंठों का नाम ले न सके'),(23.5,26.5,'जाम लिख दिया'),(26.5,29.988,'होंठों का नाम ले न सके')]
PLAN={'fps':30,'lyrics':[{'start_frame':round(s*30),'end_frame':round(e*30),'text':text} for s,e,text in CUES]}
@lru_cache(None)
def asset(name):return Image.open(ROOT/(name+'.webp')).convert('RGBA')

def anchored(im,obj,x,y,width,pivot,angle=0,alpha=1,shadow=True):
 width=max(1,round(width));s=obj.resize((width,max(1,round(obj.height*width/obj.width))),Image.Resampling.LANCZOS)
 oldw,oldh=s.size;px,py=pivot[0]*oldw,pivot[1]*oldh;r=math.radians(angle)
 s=s.rotate(angle,resample=Image.Resampling.BICUBIC,expand=True)
 dx=math.cos(r)*(px-oldw/2)+math.sin(r)*(py-oldh/2)
 dy=-math.sin(r)*(px-oldw/2)+math.cos(r)*(py-oldh/2)
 left=round(x-(s.width/2+dx));top=round(y-(s.height/2+dy))
 if alpha<1:s.putalpha(s.getchannel('A').point(lambda a:round(a*max(0,alpha))))
 if shadow:
  sh=Image.new('RGBA',s.size,(72,49,33,0));sh.putalpha(s.getchannel('A').filter(ImageFilter.GaussianBlur(3)).point(lambda a:round(a*.13)));im.alpha_composite(sh,(left+3,top+5))
 im.alpha_composite(s,(left,top))

@lru_cache(None)
def desk():
 im=paper().copy();d=ImageDraw.Draw(im)
 for j in range(15):
  yy=80+j*59;d.line(curve([(-20,yy),(120,yy-7),(330,yy+8),(560,yy-4)],60),fill='#e7d4ae',width=1)
 # A soft diagonal window light is part of the setting, not a scene-changing pan.
 wash=Image.new('RGBA',(W,H));dd=ImageDraw.Draw(wash)
 dd.polygon([(0,0),(540,0),(540,255),(0,720)],fill=(255,253,235,45));im.alpha_composite(wash)
 return im

@lru_cache(None)
def page():
 im=Image.new('RGBA',(420,570));d=ImageDraw.Draw(im)
 d.polygon([(14,10),(408,3),(414,551),(4,563)],fill='#fff8e9',outline='#d2bb96')
 d.line((25,27,389,21),fill='#eadcbd',width=1)
 d.line((18,535,390,529),fill='#eadcbd',width=1)
 for j in range(260):
  x=22+j*173%373;y=30+j*277%490;d.line((x,y,x+2,y),fill='#f0e5cd')
 return im

@lru_cache(None)
def well():
 im=Image.new('RGBA',(150,120));d=ImageDraw.Draw(im)
 d.ellipse((17,69,138,113),fill=(89,59,38,35))
 d.rounded_rectangle((24,32,127,94),radius=25,fill='#28414d',outline='#a78852',width=2)
 d.ellipse((24,24,127,64),fill='#bea471',outline='#6e5d46',width=2)
 d.ellipse((32,30,119,57),fill='#122c3c',outline='#ebe0c5',width=1)
 d.arc((40,34,110,53),180,330,fill='#708a8c',width=2)
 for x in range(39,120,10):d.line((x,68,x+2,85),fill='#829082',width=1)
 return im

def portrait(t,width=250):
 obj=asset('muse');h=round(obj.height*width/obj.width);obj=obj.resize((round(width),h),Image.Resampling.LANCZOS)
 a=np.asarray(obj);yy,xx=np.mgrid[:h,:round(width)];weight=np.clip((yy-h*.65)/(h*.35),0,1)*np.clip((xx-width*.5)/(width*.5),0,1)
 sy=yy-np.rint(np.sin(xx*.045+t*1.8)*weight*3).astype(int);valid=(sy>=0)&(sy<h);out=np.zeros_like(a);out[valid]=a[sy[valid],xx[valid]]
 return Image.fromarray(out)

def ink_paths():
 result=[]
 for row in range(3):
  y=487+row*31
  result.append(curve([(97,y),(128,y-15),(158,y+13),(198,y-3)],70)+curve([(198,y-3),(224,y-12),(245,y+8),(278,y-1)],60))
 return result
PATHS=ink_paths()
def writing_progress(t):
 return [ease((t-(7.6+j*2.3))/2.05) for j in range(3)]

@lru_cache(None)
def word_mask(text,size):
 f=font(size,text);d=ImageDraw.Draw(Image.new('RGB',(1,1)));box=d.textbbox((0,0),text,font=f)
 im=Image.new('RGBA',(round(d.textlength(text,font=f))+15,size+32));ImageDraw.Draw(im).text((5,2),text,font=f,fill='#28404e')
 return im
@lru_cache(None)
def jam():return word_mask('जाम',53)

def base(t):
 im=desk().copy();put(im,page(),255,454,420,angle=-1.2,shadow=True)
 # The same letter, cup and inkwell remain in their established places throughout.
 put(im,asset('goblet'),449,631,112,angle=-2,shadow=True)
 put(im,well(),77,650,87,shadow=True)
 return im

def reveal_muse(im,t,alpha=1):
 q=ease((t-3.5)/2.5)
 if q<=0:return
 obj=portrait(t,260);obj.putalpha(obj.getchannel('A').point(lambda a:round(a*q*alpha)))
 anchored(im,obj,227,331,260,(.5,.5),angle=-1,shadow=False)
 # Fine ink lines expand outward from the first remembered glance.
 d=ImageDraw.Draw(im)
 for j in range(3):
  pts=curve([(102,424+j*6),(45,385),(65,245),(129,222-j*7)],70)
  n=round(q*len(pts))
  if n>1:d.line(pts[:n],fill='#a8b7a6',width=1)

def draw_written(im,t):
 from PIL import ImageChops
 for j,(text,q) in enumerate(zip(['तुम्हारी याद','अधूरी बात','खामोश मोहब्बत'],writing_progress(t))):
  obj=word_mask(text,24).copy();cut=Image.new('L',obj.size);ImageDraw.Draw(cut).rectangle((0,0,round(q*obj.width),obj.height),fill=255)
  obj.putalpha(ImageChops.multiply(obj.getchannel('A'),cut));im.alpha_composite(obj,(94,458+j*34))
 if t>16.4:
  q=ease((t-16.4)/1.0);ImageDraw.Draw(im).line((95,603,95+180*q,603),fill='#c9b492',width=1)


def pen(im,x,y,width=335,angle=0,alpha=1):anchored(im,asset('writing_hand'),x,y,width,(.147,.883),angle,alpha,True)

def intro(t):
 im=base(t);wx,wy=77,650
 nibx,niby=77,584+math.sin(t*2)*3
 if t>2:
  q=ease((t-2)/1.5);niby=mix(584,497,q);nibx=mix(77,132,q)
 pen(im,nibx,niby,365,angle=-3)
 d=ImageDraw.Draw(im)
 if t<.9:
  q=ease(t/.9);y=mix(595,638,q);d.ellipse((74,y-5,80,y+5),fill='#213f50')
 for j in range(3):
  age=t-.82-j*.35
  if 0<age<1.2:
   r=age*22;opacity=1-age/1.2;color=tuple(round(mix(225,c,opacity)) for c in (56,87,103))
   d.ellipse((wx-r,640-r*.23,wx+r,640+r*.23),outline=color,width=1)
 return im

def inspired(t):
 im=base(t);reveal_muse(im,t);draw_written(im,t)
 if t<7.6:
  q=ease((t-3.5)/3.9);x=mix(132,97,q);y=mix(497,487,q)
 else:
  active=min(2,max(0,int((t-7.6)/2.3)));q=writing_progress(t)[active]
  text=['तुम्हारी याद','अधूरी बात','खामोश मोहब्बत'][active];obj=word_mask(text,24);x=99+q*(obj.width-12);y=482+active*34+math.sin(q*math.tau*4)*6
 pen(im,x,y,335,angle=math.sin(t*1.7)*1.4)
 return im

def hesitant(t):
 im=base(t);reveal_muse(im,t,alpha=mix(1,.52,ease((t-17.5)/6)));draw_written(im,t)
 q=ease((t-17.5)/4.5)
 x=mix(99,139,q)+math.sin(t*3.5)*1.2;y=610-18*math.sin(math.pi*q)
 pen(im,x,y,345,angle=-3*q)
 # A lingering blank line after the finished poetry is the unspoken confession.
 d=ImageDraw.Draw(im)
 for j in range(3):d.ellipse((103+j*9,615,105+j*9,617),fill='#a99c86')
 # The remembered face softly recedes behind a moving translucent veil.
 veil=Image.new('RGBA',(W,H));v=ImageDraw.Draw(veil)
 for j in range(7):
  x=305+j*19+math.sin(t*1.2+j*.5)*5
  v.line(curve([(x,140),(x-9,315),(x+12,500),(x-3,720)],80),fill=(251,245,228,round(9+q*12)),width=16)
 im.alpha_composite(veil)
 return im

def metaphor(t):
 im=base(t);reveal_muse(im,t,.52);draw_written(im,t)
 q=ease((t-23.5)/2.3);obj=jam().copy();mask=obj.getchannel('A');cut=Image.new('L',obj.size);ImageDraw.Draw(cut).rectangle((0,0,round(q*obj.width),obj.height),fill=255)
 from PIL import ImageChops
 obj.putalpha(ImageChops.multiply(mask,cut));im.alpha_composite(obj,(104,582))
 x=109+q*(obj.width-12);y=622+math.sin(q*math.tau*2)*7
 if t<26.4:pen(im,x,y,345,angle=-4+q*6)
 else:
  age=ease((t-26.4)/2.5);pen(im,mix(x,610,age),mix(y,675,age),345,angle=mix(2,-3,age),alpha=1)
 # An ink line links the written metaphor to the cup already present on the desk.
 d=ImageDraw.Draw(im);p=curve([(215,625),(295,698),(376,672),(434,641)],90)
 n=round(ease((t-25.3)/2)*len(p))
 if n>1:d.line(p[:n],fill='#9a7881',width=1)
 if t>27.3:
  q=ease((t-27.3)/2.5)
  # The unsent paper corner folds gently; written states are retained underneath.
  x=460-34*q;y=735-26*q
  d.polygon([(460,699),(460,735),(424,735),(x,y)],fill='#ebdec2',outline='#c7b28e')
 return im

SHOTS=[(0,intro),(3.5,inspired),(10.5,inspired),(17.5,hesitant),(23.5,metaphor),(26.5,metaphor)]
def frame(t,captions=True):
 idx=max(i for i,(start,_) in enumerate(SHOTS) if t>=start)
 im=SHOTS[idx][1](t)
 if idx and t-SHOTS[idx][0]<.2 and SHOTS[idx][1]!=SHOTS[idx-1][1]:im=Image.blend(SHOTS[idx-1][1](t),im,ease((t-SHOTS[idx][0])/.2))
 if 10.5<=t<17.5:
  # A small crop changes emphasis; ongoing hand/ink action provides the motion.
  layer=im.crop((34,190,484,890)).resize((540,840),Image.Resampling.LANCZOS);im=desk().copy();im.alpha_composite(layer,(0,40))
 return overlay(im.convert('RGB'),PLAN,round(t*30)) if captions else im.convert('RGB')

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--audio',required=True);ap.add_argument('--out',required=True);args=ap.parse_args();out=Path(args.out);out.mkdir(parents=True,exist_ok=True)
 dur=min(29.988118,float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',args.audio])));n=round(dur*30)
 proc=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s','540x960','-r','30','-i','-','-i',args.audio,'-vf','scale=1080:1920:flags=lanczos','-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-t',str(dur),'-movflags','+faststart',str(out/'new_song_story_30s.mp4')],stdin=subprocess.PIPE)
 for f in range(n):proc.stdin.write(frame(f/30).tobytes())
 proc.stdin.close()
 if proc.wait():raise RuntimeError('Encoding failed')
 sheet=Image.new('RGB',(810,480*len(SHOTS)),'#fff8e9')
 for row,(start,_) in enumerate(SHOTS):
  end=SHOTS[row+1][0] if row+1<len(SHOTS) else dur
  for col,q in enumerate([.15,.5,.85]):sheet.paste(frame(start+(end-start)*q).resize((270,480)),(270*col,480*row))
 sheet.save(out/'contact.jpg',quality=91);export_srt(PLAN,out/'lyrics.srt')
 (out/'about.json').write_text(json.dumps({'kind':'authored connected-story film for supplied recording','duration':dur,'original_visuals_used':False,'original_audio_preserved':True,'story':['Blank paper awaits expression','Remembered beauty appears and the pen begins to move','The letter grows from that inspiration','A final line remains unspoken','The poet writes a metaphor instead: jaam','The letter remains unsent; the remembered face and same cup persist'],'caption_timing':'approximate phrases, not verified word alignment','last_line_evidence':'Independent large-v3 Hindi ASR strongly identifies likh diya, correcting the direct model utha liya mistake','universal_automation_certified':False},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
