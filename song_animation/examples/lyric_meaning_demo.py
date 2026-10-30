"""Authored two-line art-direction demonstration, not an all-song automation proof.
Original raster artwork + independent footprints, branches, petals, contact marks.
"""
import math,subprocess,argparse,json
from pathlib import Path
from functools import lru_cache
import numpy as np
from PIL import Image,ImageDraw,ImageFilter
from song_animation.art import curve
from song_animation.lyrics import overlay
W,H=540,960
ROOT=Path(__file__).parents[1]/'assets'/'meaning_demo'
def ease(t):
 t=max(0,min(1,t));return t*t*(3-2*t)
def mix(a,b,t):return a+(b-a)*t
@lru_cache(None)
def asset(name):
 im=Image.open(ROOT/(name+'.webp')).convert('RGBA');return im.crop(im.getchannel('A').getbbox())
@lru_cache(None)
def paper():
 y,x=np.mgrid[:H,:W];grain=np.random.default_rng(144).normal(0,1.3,(H,W));shade=((x-W*.45)**2/(W*W)+(y-H*.4)**2/(H*H))*12
 a=np.stack([np.clip(c+grain-shade,0,255) for c in (248,241,220)],axis=2).astype('uint8')
 im=Image.fromarray(a).convert('RGBA');d=ImageDraw.Draw(im)
 for i in range(700):
  xx=(i*197+21)%W;yy=(i*337+63)%H;d.line((xx,yy,xx+2,yy+1),fill=(231,221,202,255))
 return im

def put(im,obj,x,y,width,angle=0,alpha=1,shadow=True):
 s=obj.resize((int(width),max(1,round(obj.height*width/obj.width))),Image.Resampling.LANCZOS).rotate(angle,resample=Image.Resampling.BICUBIC,expand=True)
 if alpha<1:s.putalpha(s.getchannel('A').point(lambda a:int(a*alpha)))
 left=int(x-s.width/2);top=int(y-s.height/2)
 if shadow:
  sh=Image.new('RGBA',s.size,(58,34,26,0));sh.putalpha(s.getchannel('A').filter(ImageFilter.GaussianBlur(3)).point(lambda a:int(a*.16)));im.alpha_composite(sh,(left+3,top+6))
 im.alpha_composite(s,(left,top))
@lru_cache(None)
def sole():
 im=Image.new('RGBA',(32,65));d=ImageDraw.Draw(im)
 d.rounded_rectangle((7,5,25,42),radius=8,fill=(110,80,55,85),outline=(105,79,59,210),width=1)
 d.ellipse((9,47,24,60),fill=(110,80,55,45),outline=(105,79,59,210))
 for y in range(14,38,6):d.line((11,y,21,y),fill=(105,79,59,60))
 return im
@lru_cache(None)
def petal():
 im=Image.new('RGBA',(75,100));d=ImageDraw.Draw(im)
 pts=curve([(35,5),(4,0),(-4,35),(18,74)])[:-1]+curve([(18,74),(44,113),(74,65),(68,25)])[:-1]+curve([(68,25),(65,3),(46,-3),(35,5)])
 d.polygon(pts,fill='#b8183e');d.line(pts,fill='#6b203a',width=1)
 d.line(curve([(35,10),(17,37),(35,66),(29,85)]),fill='#e4788c',width=2)
 d.line(curve([(35,9),(58,12),(65,40),(53,65)]),fill='#ef9c9d',width=1)
 return im
@lru_cache(None)
def route():
 segments=[[(270,760),(480,745),(450,690),(410,650)],[(410,650),(350,600),(130,575),(120,480)],[(120,480),(100,390),(410,380),(410,310)],[(410,310),(420,240),(300,200),(270,190)]]
 pts=sum([curve(s,100)[:-1] for s in segments],[])+[(270,190)]
 distances=[0.]
 for a,b in zip(pts,pts[1:]):distances.append(distances[-1]+math.dist(a,b))
 result=[]
 for dist in np.arange(0,distances[-1],25):
  j=min(len(pts)-2,max(0,int(np.searchsorted(distances,dist))-1));q=(dist-distances[j])/(distances[j+1]-distances[j]);a,b=pts[j:j+2]
  x,y=mix(a[0],b[0],q),mix(a[1],b[1],q);angle=math.atan2(b[1]-a[1],b[0]-a[0]);side=-1 if len(result)%2 else 1
  result.append((x+side*10*math.sin(angle),y-side*10*math.cos(angle),-math.degrees(angle)-90))
 return result

def thorns(t):
 im=paper().copy();progress=ease(t/2.85);r=route();n=progress*(len(r)-1)
 for i,(x,y,a) in enumerate(r):
  visible=ease((n-i)*1.5)
  if visible:put(im,sole(),x,y,20+3*visible,a,alpha=.8*visible,shadow=False)
 for i,(x,y) in enumerate([(155,650),(390,480),(140,310)]):
  put(im,asset('thorns'),x,y,310,angle=(i-1)*4+math.sin(t*1.8+i)*1.2)
 return im

def flowers(t):
 im=paper().copy();hand=Image.new('RGBA',(W,H));put(hand,asset('palm'),310,493,405,angle=0)
 d=ImageDraw.Draw(hand)
 for j in range(3):
  contact=1.36+j*.32;v=ease((t-contact)/.42)
  if v:
   x=313+j*8;y=522+j*20;pts=curve([(x,y),(x+15,y-6),(x+28,y+14),(x+47,y+11)],40);end=max(2,int(v*40))
   d.line(pts[:end],fill='#a23745',width=2);d.line([(a,b+2) for a,b in pts[:end]],fill='#e3a5a1',width=1)
 recoil=sum(math.exp(-((t-(1.36+j*.32))/.13)**2) for j in range(3))*1.5
 hand=hand.rotate(-recoil,resample=Image.Resampling.BICUBIC,center=(310,750));im.alpha_composite(hand)
 settle=ease(t/.6);put(im,asset('rose'),mix(160,210,settle),mix(300,360,settle),mix(250,295,settle),angle=mix(-12,-3,settle)+math.sin(t*1.2)*1.2)
 for j in range(3):
  a=t-(.48+j*.32)
  if a<=0:continue
  q=min(1,a/.88);x=mix(250,336+j*8,ease(q));y=mix(350,526+j*20,ease(q))
  if a>.88:x+=(a-.88)*75;y+=(a-.88)*45
  put(im,petal(),x,y,45+j*3,angle=mix(28,-25,q)+j*18,alpha=max(.0,1-max(0,a-2)*.7))
 return im

def frame(t):
 if t<2.96:
  im=thorns(t)
  if t>2.79:im=Image.blend(im,flowers(0),ease((t-2.79)/.17))
 else:im=flowers(t-2.96)
 plan={'fps':30,'lyrics':[{'start_frame':0,'end_frame':89,'text':'लोग कांटों से बच के चलते हैं'},{'start_frame':89,'end_frame':204,'text':'हमने फूलों से जख्म खाए हैं'}]}
 return overlay(im.convert('RGB'),plan,min(203,round(t*30)))

def main():
 p=argparse.ArgumentParser();p.add_argument('--audio',required=True);p.add_argument('--out',required=True);a=p.parse_args();out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
 cmd=['ffmpeg','-y','-v','error','-f','rawvideo','-pix_fmt','rgb24','-s','540x960','-r','30','-i','-','-ss','9.42','-i',a.audio,'-map','0:v','-map','1:a','-t','6.8','-vf','scale=1080:1920:flags=lanczos','-c:v','libx264','-crf','18','-preset','fast','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k','-movflags','+faststart',str(out/'preview.mp4')]
 with (out/'ffmpeg.log').open('w') as log:
  proc=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=log)
  try:
   for f in range(204):proc.stdin.write(frame(f/30).tobytes())
   proc.stdin.close()
   if proc.wait():raise RuntimeError('Render failed')
  except BaseException:proc.kill();proc.wait();raise
 sheet=Image.new('RGB',(1080,1280))
 for i,t in enumerate([.5,1.4,2.6,3.6,4.9,6.4]):sheet.paste(frame(t).resize((360,640)),((i%3)*360,(i//3)*640))
 sheet.save(out/'contact.jpg',quality=95)
 subprocess.run(['ffmpeg','-v','error','-xerror','-i',str(out/'preview.mp4'),'-f','null','-'],check=True)
 (out/'about.json').write_text(json.dumps({'type':'authored art-direction proof, not automatic all-song quality certification','source_start':9.42,'duration':6.8,'lyrics_timing':'approximate phrase','original_artwork':'built-in imagegen','causal_animation':['footprints pass around branches','rose petals land and leave symbolic marks on palm']}))
if __name__=='__main__':main()
