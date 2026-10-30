"""Authored 30s meaning-led showcase for this reference song.
Not evidence of unrestricted automatic artwork generation for other songs.
"""
import math,json,subprocess,argparse
from pathlib import Path
from functools import lru_cache
from PIL import Image,ImageDraw
from song_animation.examples.lyric_meaning_demo import paper,put,asset,petal,thorns,flowers,ease,mix,curve
from song_animation.art import person
from song_animation.lyrics import overlay
W,H=540,960
WORDS=[(0,4.54,'जितने भी जख्म हैं मेरे दिल पर'),(4.54,9.42,'दोस्तों के लगाए हुए हैं'),(9.42,12.38,'लोग कांटों से बच के चलते हैं'),(12.38,16.22,'हमने फूलों से जख्म खाए हैं'),(16.22,18.96,'तुम तो गैरों की बात करती हो'),(18.96,22.3,'हमने अपने भी आजमाए हैं'),(22.3,26.36,'जितने भी जख्म हैं मेरे दिल पर'),(26.36,29.84,'दोस्तों के लगाए हुए हैं')]
PLAN={'fps':30,'lyrics':[dict(start_frame=round(a*30),end_frame=round(b*30),text=s) for a,b,s in WORDS]}
@lru_cache(None)
def heart_base():
 a=asset('heart');return a.resize((320,round(320*a.height/a.width)),Image.Resampling.LANCZOS)

def scarred_heart(t,count=4,base=0):
 a=heart_base().copy();d=ImageDraw.Draw(a);w,h=a.size
 sites=[(.25,.53,.61,.63),(.46,.71,.74,.58),(.28,.79,.65,.88),(.52,.43,.78,.49),(.26,.64,.51,.74),(.42,.86,.73,.79),(.43,.55,.68,.69)]
 for j,(x,y,x2,y2) in enumerate(sites):
  q=max(0,min(1,count-j))
  if not q:continue
  pts=curve([(w*x,h*y),(w*(x+.1),h*(y-.03)),(w*(x2-.06),h*(y2+.03)),(w*x2,h*y2)],50);n=max(2,int(q*50));d.line(pts[:n],fill='#612d36',width=7);d.line([(xx,yy-1) for xx,yy in pts[:n]],fill='#fae0c4',width=3)
  for k in range(6,n,8):
   xx,yy=pts[k];d.line((xx-3,yy+5,xx+4,yy-5),fill='#683743',width=2)
 return a

def heart_scene(t,reprise=False):
 im=paper().copy();phase=min(1,t/3.8);count=(3 if reprise else 0)+4*ease(phase)
 put(im,scarred_heart(t,count),270,432,330*(1+.026*math.sin(t*math.tau*1.1)),angle=math.sin(t*.4)*1.3)
 d=ImageDraw.Draw(im);pts=[]
 for x in range(95,446):
  z=((x-95)/350*2.4-t*.64)%1;dy=-23*math.exp(-((z-.43)/.025)**2)+13*math.exp(-((z-.49)/.035)**2);pts.append((x,704+dy))
 d.line(pts,fill='#94505b',width=1)
 for j in range(4):
  a=t*.45+j*2.3;x=270+math.cos(a)*(180+j*5);y=380+math.sin(a)*190;put(im,petal(),x,y,13+j*2,angle=a*30,alpha=.42,shadow=False)
 return im

def gift(t,duration=4.88,ending=False):
 p=t/duration;im=paper().copy();layer=Image.new('RGBA',(W,H))
 put(layer,asset('palm'),270,535,340,angle=9)
 q=ease(p/.56);x=mix(625,232,q);y=mix(225,425,q)
 retreat=ease((p-.59)/.32)
 put(im,asset('palm'),x+115+retreat*360,y-150-retreat*150,265,angle=163)
 put(layer,asset('rose'),x,y,230,angle=mix(-45,-5,q))
 if p>.65:
  d=ImageDraw.Draw(layer)
  for j in range(3):
   z=ease((p-.68-j*.055)/.18)
   if z:d.line(curve([(264,548+j*16),(277,541+j*16),(296,560+j*16),(309,557+j*16)])[:max(2,int(z*60))],fill='#9c4152',width=2)
 im.alpha_composite(layer)
 if p>.61:
  for j in range(3):
   v=max(0,(p-.61-j*.045)/.25);xx=245+v*75;yy=400+v*105
   if v<2.3:put(im,petal(),xx,yy,30,angle=30+v*70+j*25,alpha=max(0,1-(v-1.2)*.8))
 return im

P={'ink':'#4b4140','green':'#7f8a6b','paper':'#f5ecd8','muted':'#ae9f90','accent':'#a84956','blue':'#728c96'}
def strangers(t):
 im=paper().copy();d=ImageDraw.Draw(im)
 for y in range(95,810,75):
  d.line((0,y,W,y),fill='#ded3bc',width=1)
  for x in range(-40 if y%150 else 0,W,108):d.line((x,y,x,y+75),fill='#ded3bc',width=1)
 for j in range(20):
  lane=j%5;x=65+lane*102;direction=1 if lane%2 else -1;y=95+(j*117+t*direction*48)%650
  if abs(x-270)<65 and abs(y-460)<80:x+=85
  person(d,x,y,P,P['muted'] if j%3 else P['blue'],t*6+j,1.1)
 d.ellipse((224,407,316,507),fill=P['paper'],outline='#c49a8b',width=1);person(d,270,462,P,P['accent'],0,1.7)
 return im

def familiar(t):
 im=paper().copy();phase=t/3.34;d=ImageDraw.Draw(im)
 anchors=[(95,215),(450,270),(95,685)];target=[(212,420),(340,450),(230,570)]
 for j,((x,y),(tx,ty)) in enumerate(zip(anchors,target)):
  loss=ease((phase-.24-j*.16)/.34);dist=loss*100;xx=x+(-dist if x<270 else dist);yy=y+(-dist if y<400 else dist)
  pts=curve([(xx,yy),(230,yy),(tx-50,ty+20),(tx,ty)])
  if loss<.9:
   cut=int(len(pts)*(1-loss*.8));d.line(pts[:max(2,cut)],fill=['#a3515c','#8b9b83','#b29564'][j],width=2)
  put(im,asset('palm'),xx,yy,135,angle=-35 if x<270 else 145,alpha=1-loss*.8)
 put(im,scarred_heart(t,2+3*ease(phase)),280,470,270*(1+.02*math.sin(t*7)),angle=-5)
 return im

def art(t):
 if t<4.54:return heart_scene(t)
 if t<9.42:return gift(t-4.54)
 if t<12.38:return thorns(t-9.42)
 if t<16.22:return flowers(t-12.38)
 if t<18.96:return strangers(t-16.22)
 if t<22.3:return familiar(t-18.96)
 if t<26.36:return heart_scene(t-22.3,True)
 return gift(t-26.36,3.64,True)

def frame(t):
 im=art(t)
 # Short transitions preserve action; the lyrics plane stays fixed.
 for a,_,_ in WORDS[1:]:
  if a-.12<=t<a:im=Image.blend(im,art(a),ease((t-a+.12)/.12))
 return overlay(im.convert('RGB'),PLAN,min(899,round(t*30)))

def main():
 p=argparse.ArgumentParser();p.add_argument('--audio',required=True);p.add_argument('--out',required=True);a=p.parse_args();out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
 cmd=['ffmpeg','-y','-v','error','-f','rawvideo','-pix_fmt','rgb24','-s','540x960','-r','30','-i','-','-i',a.audio,'-map','0:v','-map','1:a','-t','30','-vf','scale=1080:1920:flags=lanczos','-c:v','libx264','-crf','18','-preset','fast','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k','-movflags','+faststart',str(out/'preview.mp4')]
 with (out/'ffmpeg.log').open('w') as log:
  proc=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=log)
  try:
   for f in range(900):
    proc.stdin.write(frame(f/30).tobytes())
    if f%150==0:print('Render',f,'/900',flush=True)
   proc.stdin.close()
   if proc.wait():raise RuntimeError('Render failed')
  except BaseException:proc.kill();proc.wait();raise
 sheet=Image.new('RGB',(540,320*8))
 for i,(start,end,words) in enumerate(WORDS):
  for j,q in enumerate((.1,.5,.9)):sheet.paste(frame(start+(end-start)*q).resize((180,320)),(j*180,i*320))
 sheet.save(out/'contact.jpg',quality=95)
 subprocess.run(['ffmpeg','-v','error','-xerror','-i',str(out/'preview.mp4'),'-f','null','-'],check=True)
 probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-of','json',str(out/'preview.mp4')]))
 video=next(s for s in probe['streams'] if s['codec_type']=='video');assert int(video['nb_frames'])==900 and abs(float(video['duration'])-30)<.04
 (out/'about.json').write_text(json.dumps({'type':'authored lyric-meaning art-direction showcase for this source song; not all-song automation certification','duration':30,'dimensions':[1080,1920],'frames':900,'original_artwork':'built-in imagegen','technical_checks':'passed','lyrics_timing':'approximate phrase boundaries','meaning_map':[dict(start=a,end=b,words=s) for a,b,s in WORDS]},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
