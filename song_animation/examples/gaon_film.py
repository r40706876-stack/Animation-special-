"""Authored film for song_20261104_gaon.m4a (village memories); not a universal automation proof.

Original flat paper-grain illustrations drawn in code, one scene per lyric line:
chulha -> kolhu field -> sunset -> dibiya in the aala -> latched door ->
city glare web -> the rusty door opens -> termite-eaten charkha waiting.
"""
import argparse,math,subprocess,json
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFilter,ImageChops

W,H=1080,1920;SS=2;FPS=30
CLIP_START=15.0;CLIP_LEN=30.0
# (start,end,text) on the 30 s clip; Hindi heard twice independently by Gemini (2026-11-05/06).
CUES=[(0.05,1.8,'एक चूल्हे आगे पोती माँ'),(1.8,3.6,'स्वाद हाथ की रोटी का'),
 (3.75,5.5,'एक कोल्हू आला खेत मेरा'),(5.5,7.4,'मिल गए दस, खो गया एक मेरा'),
 (7.5,10.1,'एक सूरज छुपता खेत'),(10.4,14.3,'एक डिबिया की लौ दीखे आले में'),
 (18.4,21.6,'फिर फँस गया बचपन\nचकाचौंध के जाले में'),(22.1,26.0,'बेशक कब्ज़े में जंग लगी\nएक खुला आज भी किवाड़ पड़ा'),
 (26.0,29.8,'एक चरखा खा लिया दीमक ने\nपर देखे मेरी बाट खड़ा')]
SCENES=[(0.0,3.65,'chulha'),(3.65,7.35,'kolhu'),(7.35,10.25,'sunset'),(10.25,14.45,'dibiya'),
 (14.45,18.35,'door'),(18.35,22.05,'city'),(22.05,26.0,'opendoor'),(26.0,30.0,'charkha')]
XF=0.45  # crossfade seconds

def S(v):return int(round(v*SS))
def ease(x):x=min(1,max(0,x));return x*x*(3-2*x)
def hexc(h,a=255):h=h.lstrip('#');return (int(h[0:2],16),int(h[2:4],16),int(h[4:6],16),a)
def mix(c1,c2,t):return tuple(int(round(a+(b-a)*t)) for a,b in zip(c1,c2))

def vgrad(w,h,stops):
    ys=np.linspace(0,1,h)[:,None];out=np.zeros((h,1,3))
    for (p0,c0),(p1,c1) in zip(stops,stops[1:]):
        m=(ys>=p0)&(ys<=p1);t=np.clip((ys-p0)/max(1e-6,p1-p0),0,1)
        for k in range(3):out[...,k]=np.where(m,np.array(hexc(c0)[k])+(hexc(c1)[k]-hexc(c0)[k])*t,out[...,k])
    return Image.fromarray(np.repeat(out,w,axis=1).astype(np.uint8),'RGB')

def glow(size,center,radius,color,strength=1.0):
    """Soft additive radial light as an RGB image to be added with ImageChops.add."""
    w,h=size;y,x=np.ogrid[:h,:w];d=np.sqrt((x-center[0])**2+(y-center[1])**2)/radius
    a=np.clip(1-d,0,1)**2*strength
    return Image.fromarray((a[...,None]*np.array(color[:3])[None,None,:]).clip(0,255).astype(np.uint8),'RGB')

def add_glow(img,center,radius,color,strength=1.0):
    # compute on a 1/4 grid then upscale: cheap and smooth
    q=4;g=glow((img.width//q,img.height//q),(center[0]/q,center[1]/q),radius/q,color,strength).resize(img.size,Image.BILINEAR)
    return ImageChops.add(img,g)

def texture_wall(img,box,base,seed,spots=260,dark=0.08):
    rng=np.random.default_rng(seed);d=ImageDraw.Draw(img,'RGBA');x0,y0,x1,y1=box
    for _ in range(spots):
        x=rng.uniform(x0,x1);y=rng.uniform(y0,y1);r=rng.uniform(S(6),S(40))
        c=mix(hexc(base)[:3],(0,0,0) if rng.random()<.6 else (255,240,210),rng.uniform(.02,dark))
        d.ellipse((x-r,y-r*.6,x+r,y+r*.6),fill=c+(int(rng.uniform(25,60)),))

def cracks(d,start,seed,n=3,color=(90,50,30,120)):
    rng=np.random.default_rng(seed)
    for _ in range(n):
        x,y=start[0]+rng.uniform(-S(40),S(40)),start[1]+rng.uniform(-S(40),S(40));pts=[(x,y)]
        for _ in range(7):x+=rng.uniform(-S(28),S(28));y+=rng.uniform(S(10),S(36));pts.append((x,y))
        d.line(pts,fill=color,width=S(2),joint='curve')

def bricks(d,box,seed):
    rng=np.random.default_rng(seed);x0,y0,x1,y1=box;bh=S(26);bw=S(62)
    for r,y in enumerate(range(int(y0),int(y1),bh)):
        off=(bw//2)*(r%2)
        for x in range(int(x0)-off,int(x1),bw):
            if rng.random()<.25:continue
            xa,xb=max(x0,x+S(3)),min(x1,x+bw-S(3))
            if xb-xa<S(8):continue
            c=mix(hexc('#a4543a')[:3],hexc('#7d3b27')[:3],rng.random())
            d.rounded_rectangle((xa,y+S(3),xb,y+bh-S(3)),radius=S(3),fill=c+(235,))

# ---------- static layers (built once at SS scale) ----------
CACHE={}
def static(name):
    if name in CACHE:return CACHE[name]
    w,h=S(W),S(H)
    if name=='chulha':
        img=vgrad(w,h,[(0,'#3a1f17'),(.55,'#6e3a24'),(.62,'#5a2f1d'),(1,'#2f1912')])
        texture_wall(img,(0,0,w,int(h*.62)),'#6e3a24',1,320,.12);d=ImageDraw.Draw(img,'RGBA')
        d.rectangle((0,S(1190),w,h),fill=hexc('#4a2718'));texture_wall(img,(0,S(1190),w,h),'#4a2718',2,160)
        d.line((0,S(1190),w,S(1190)),fill=hexc('#2a150d',200),width=S(4))
        # shelf with brass pots
        d.rectangle((S(60),S(430),S(420),S(452)),fill=hexc('#3b2014'));
        for i,(x,c) in enumerate([(110,'#c99a3c'),(205,'#b07d2a'),(300,'#d2a645')]):
            d.ellipse((S(x),S(350),S(x+70),S(432)),fill=hexc(c));d.rectangle((S(x+18),S(330),S(x+52),S(356)),fill=hexc(c));d.ellipse((S(x+10),S(322),S(x+60),S(340)),fill=hexc('#e2bd62'))
            d.arc((S(x+8),S(360),S(x+40),S(420)),200,300,fill=hexc('#f3d98a',160),width=S(4))
        # firewood stack right
        for i in range(5):
            y=S(1150-i*30);x=S(820+((i%2)*25))
            d.rounded_rectangle((x,y,x+S(200),y+S(30)),radius=S(14),fill=hexc('#6b4226'));d.ellipse((x+S(186),y,x+S(214),y+S(30)),fill=hexc('#c99766'));d.ellipse((x+S(193),y+S(8),x+S(207),y+S(22)),outline=hexc('#8a5a35'),width=S(2))
        # clay chulha body
        cx=S(540)
        d.rounded_rectangle((cx-S(260),S(860),cx+S(260),S(1230)),radius=S(70),fill=hexc('#b06a3f'))
        d.rounded_rectangle((cx-S(260),S(860),cx+S(260),S(910)),radius=S(30),fill=hexc('#c47c4c'))
        texture_wall(img,(cx-S(250),S(870),cx+S(250),S(1220)),'#b06a3f',3,90,.1);d=ImageDraw.Draw(img,'RGBA')
        d.chord((cx-S(140),S(990),cx+S(140),S(1290)),180,360,fill=hexc('#1b0c07'))  # fire mouth
        d.rectangle((cx-S(140),S(1139),cx+S(140),S(1232)),fill=hexc('#1b0c07'))
        # chakla belan at left floor
        d.ellipse((S(70),S(1330),S(380),S(1420)),fill=hexc('#8a5631'));d.ellipse((S(80),S(1322),S(370),S(1405)),fill=hexc('#a8703f'))
        d.rounded_rectangle((S(120),S(1300),S(400),S(1326)),radius=S(13),fill=hexc('#d4a26a'))
        d.ellipse((S(150),S(1340),S(300),S(1385)),fill=hexc('#f0dcb0'))  # raw dough disc
        CACHE[name]=img
    elif name=='kolhu':
        img=vgrad(w,h,[(0,'#f7e7b4'),(.33,'#f3d08a'),(.5,'#e9c27e'),(.52,'#9fae5a'),(1,'#5f7a33')])
        d=ImageDraw.Draw(img,'RGBA')
        d.polygon([(0,S(930)),(S(250),S(860)),(S(520),S(905)),(S(800),S(840)),(W*SS,S(900)),(W*SS,S(1000)),(0,S(1000))],fill=hexc('#b8a06a',200))
        d.ellipse((S(700),S(300),S(880),S(480)),fill=hexc('#fff3c4',230))
        # thatched shed
        d.polygon([(S(470),S(800)),(S(700),S(690)),(S(940),S(800))],fill=hexc('#c99b52'));
        for i in range(24):x=S(480+i*19);d.line((x,S(800)-((i*19)%120)*0+0,x+S(10),S(800)),fill=hexc('#a07a3c',160),width=S(2))
        d.polygon([(S(470),S(800)),(S(700),S(690)),(S(940),S(800))],outline=hexc('#8a6630'),width=S(3))
        for x in (510,900):d.rectangle((S(x),S(800),S(x+14),S(1040)),fill=hexc('#6b4a2a'))
        # jaggery pan
        d.ellipse((S(560),S(1030),S(860),S(1100)),fill=hexc('#3a3632'));d.ellipse((S(580),S(1032),S(840),S(1080)),fill=hexc('#b5762a'))
        d.rectangle((S(590),S(1080),S(830),S(1130)),fill=hexc('#6b4a2a'))
        # kolhu stone base
        d.ellipse((S(200),S(1100),S(470),S(1190)),fill=hexc('#7f7a72'));d.rectangle((S(250),S(990),S(420),S(1145)),fill=hexc('#8f8a80'));d.ellipse((S(250),S(960),S(420),S(1020)),fill=hexc('#a9a399'))
        # field rows
        for i in range(14):
            y=S(1010+i*68);d.line((0,y,W*SS,y+S(30)),fill=hexc('#4f6a2a',90),width=S(6))
        CACHE[name]=img
    elif name=='sunset':
        img=vgrad(w,h,[(0,'#3d3a78'),(.25,'#8a5a9a'),(.45,'#f08a6a'),(.56,'#ffc97a'),(.58,'#c48a4a'),(1,'#7a5a1a')])
        d=ImageDraw.Draw(img,'RGBA')
        d.polygon([(0,S(1080)),(S(160),S(1020)),(S(380),S(1060)),(S(600),S(1000)),(S(820),S(1050)),(W*SS,S(1010)),(W*SS,S(1120)),(0,S(1120))],fill=hexc('#6b4a6e'))
        # tree silhouettes on horizon
        for x,s in [(120,1.0),(330,.7),(860,1.2)]:
            d.rectangle((S(x),S(1040-120*s),S(x+10*s),S(1080)),fill=hexc('#3b2a40'))
            for dx,dy,r in [(0,-150,60),(-40,-120,45),(40,-115,48),(-10,-190,42)]:d.ellipse((S(x+dx*s-r*s),S(1040+dy*s-r*s),S(x+dx*s+r*s),S(1040+dy*s+r*s)),fill=hexc('#3b2a40'))
        # electric poles
        for x,top in [(170,640),(560,700),(940,610)]:
            d.rectangle((S(x),S(top),S(x+12),S(1110)),fill=hexc('#2a2030'));d.rectangle((S(x-50),S(top+20),S(x+62),S(top+30)),fill=hexc('#2a2030'))
        d.line((S(120),S(668),S(566),S(724),S(1080),S(630)),fill=hexc('#2a2030',200),width=S(3),joint='curve')
        d.rectangle((0,S(1110),W*SS,h),fill=hexc('#a08e2a'))
        CACHE[name]=img
    elif name in('dibiya',):
        img=vgrad(w,h,[(0,'#4a2a1c'),(1,'#2a160f')]);texture_wall(img,(0,0,w,h),'#4a2a1c',5,420,.14);d=ImageDraw.Draw(img,'RGBA')
        cracks(d,(S(180),S(260)),6,3);cracks(d,(S(860),S(1250)),7,2)
        bricks(d,(S(700),S(220),S(980),S(420)),8)
        # aala (arched niche)
        x0,x1,y0,y1=S(330),S(750),S(700),S(1180)
        d.rounded_rectangle((x0-S(26),y0-S(26),x1+S(26),y1+S(30)),radius=S(210),fill=hexc('#6a3c26'))
        d.rounded_rectangle((x0,y0,x1,y1),radius=S(190),fill=hexc('#1c0e09'))
        d.rectangle((x0-S(40),y1,x1+S(40),y1+S(40)),fill=hexc('#7a4a30'))
        CACHE[name]=img
    elif name in('door','opendoor','charkha'):
        img=vgrad(w,h,[(0,'#9a6440'),(.72,'#7c4c30'),(.73,'#5e3822'),(1,'#3e2416')])
        texture_wall(img,(0,0,w,int(h*.72)),'#8a5a3a',9,380,.12);d=ImageDraw.Draw(img,'RGBA')
        bricks(d,(S(60),S(160),S(330),S(330)),10);bricks(d,(S(790),S(1180),S(1050),S(1320)),11);cracks(d,(S(900),S(240)),12,2)
        # door frame
        d.rectangle((S(250),S(520),S(830),S(1395)),fill=hexc('#3e2618'))
        CACHE[name]=img
    elif name=='city':
        img=vgrad(w,h,[(0,'#0b0d2a'),(.6,'#1d1a4a'),(1,'#120f2a')]);d=ImageDraw.Draw(img,'RGBA')
        rng=np.random.default_rng(13)
        for i in range(140):x,y=rng.uniform(0,w),rng.uniform(0,S(700));d.ellipse((x,y,x+S(3),y+S(3)),fill=(255,255,255,int(rng.uniform(60,180))))
        CACHE[name]=img
    return CACHE[name]

# ---------- city building data (fixed) ----------
RNG=np.random.default_rng(21)
BUILDINGS=[]
x=-20
while x<W+20:
    bw=RNG.uniform(90,190);bh=RNG.uniform(420,980);BUILDINGS.append((x,bw,bh,[(RNG.random(),RNG.choice(['#ffd27a','#7af0ff','#ff7ad1','#fff2c0'])) for _ in range(60)]));x+=bw+RNG.uniform(-10,10)

def flame(d,cx,base,hgt,wid,t,seed,cols=('#ffdf7a','#ff9a3a','#e8522a')):
    for k,c in enumerate(reversed(cols)):
        s=1-k*.28;ph=t*9+seed+k
        hh=hgt*s*(0.85+.15*math.sin(ph*1.7));ww=wid*s
        sway=math.sin(ph)*wid*.18
        pts=[(cx-ww,base),(cx-ww*.6,base-hh*.45),(cx+sway,base-hh),(cx+ww*.6,base-hh*.45),(cx+ww,base)]
        d.polygon(pts,fill=hexc(c,235))

def village(img,x0,x1,y0,y1):
    """Warm dusk village path seen through the doorway (shared by two shots)."""
    sky=vgrad(x1-x0,y1-y0,[(0,'#f6c98a'),(.55,'#f9e2b0'),(.56,'#c9a35a'),(1,'#a88040')]);img.paste(sky,(x0,y0));d=ImageDraw.Draw(img,'RGBA')
    d.polygon([(x0+S(200),y1),(x0+S(320),y1),(x0+S(272),y0+S(470)),(x0+S(258),y0+S(470))],fill=hexc('#e2c48a'))
    d.ellipse((x0+S(330),y0+S(300),x0+S(470),y0+S(440)),fill=hexc('#4f6b2a'));d.rectangle((x0+S(395),y0+S(420),x0+S(405),y0+S(480)),fill=hexc('#4a3420'))
    d.rectangle((x0+S(60),y0+S(420),x0+S(150),y0+S(480)),fill=hexc('#c98a5a'));d.polygon([(x0+S(50),y0+S(422)),(x0+S(105),y0+S(380)),(x0+S(160),y0+S(422))],fill=hexc('#a0482a'))

def scene_frame(name,t,dur):
    p=t/dur;img=static(name).copy();d=ImageDraw.Draw(img,'RGBA')
    if name=='chulha':
        cx=S(540)
        for i,o in enumerate((-80,0,80)):flame(d,cx+S(o),S(1225),S(150+30*(i==1)),S(55),t,i*2.1)
        d.ellipse((cx-S(300),S(800),cx+S(300),S(880)),fill=hexc('#1f1f22'))  # tawa
        d.ellipse((cx-S(285),S(796),cx+S(285),S(864)),fill=hexc('#2e2e33'))
        puff=0.5+0.5*math.sin(min(1,p*1.4)*math.pi)  # roti puffs once
        ry=S(30+22*puff)
        d.ellipse((cx-S(200),S(830)-ry,cx+S(200),S(836)+S(10)),fill=hexc('#f4dca6'))
        rng=np.random.default_rng(3)
        for _ in range(16):
            x=cx+rng.uniform(-S(160),S(160));y=S(826)-rng.uniform(0,1)*ry*.9;r=rng.uniform(S(6),S(14))
            d.ellipse((x-r,y-r*.6,x+r,y+r*.6),fill=hexc('#b9772f',int(140+80*puff)))
        for k in range(4):  # steam
            ph=(t*.55+k*.25)%1;x0=cx+S(-120+k*80);pts=[(x0+math.sin(ph*6+j*.6+k)*S(18),S(790)-ph*S(380)-j*S(22)) for j in range(9)]
            d.line(pts,fill=(255,245,230,int(120*(1-ph))),width=S(8),joint='curve')
        rng=np.random.default_rng(int(t*FPS)//4)
        for _ in range(10):  # embers
            x=cx+rng.uniform(-S(120),S(120));y=S(1180)-rng.uniform(0,S(260));d.ellipse((x,y,x+S(5),y+S(5)),fill=hexc('#ffb347',200))
        img=add_glow(img,(cx,S(1150)),S(620),(255,140,60),.55+.08*math.sin(t*11))
    elif name=='kolhu':
        rng=np.random.default_rng(7)
        ang=t*1.3;cx,cy=S(335),S(985);L=S(300)
        ex,ey=cx+math.cos(ang)*L,cy+math.sin(ang)*L*.28
        d.line((cx,cy,ex,ey),fill=hexc('#5a3a1e'),width=S(16));d.ellipse((cx-S(30),cy-S(14),cx+S(30),cy+S(14)),fill=hexc('#6b4a2a'))
        for k in range(3):  # steam from pan
            ph=(t*.5+k*.33)%1;x0=S(650+k*70);pts=[(x0+math.sin(ph*5+j*.7)*S(14),S(1040)-ph*S(320)-j*S(20)) for j in range(8)]
            d.line(pts,fill=(255,250,240,int(130*(1-ph))),width=S(7),joint='curve')
        # sugarcane stalks foreground both sides
        for side in (0,1):
            for i in range(9):
                bx=(S(30+i*38) if side==0 else S(1050-i*38));sway=math.sin(t*1.6+i*.7)*S(22)
                top=S(560+((i*53)%180));base=S(1920)
                d.line((bx,base,bx+sway,top),fill=hexc('#8a7a3a' if i%2 else '#9aa04a'),width=S(15))
                for j in range(6):
                    yy=base-(base-top)*(j+1)/7;xx=bx+sway*(j+1)/7;d.line((xx-S(9),yy,xx+S(9),yy),fill=hexc('#55662a'),width=S(4))
                for j in range(5):
                    yy=top+S(55*j);xx=bx+sway*(1-j*.08);dirn=-1 if (i+j)%2 else 1;L=S(150+40*(j%3));droop=S(120)+sway*.4
                    d.line([(xx,yy),(xx+dirn*L*.45,yy-S(70)),(xx+dirn*L*.85,yy-S(20)+droop*.3),(xx+dirn*L,yy+droop*.7)],fill=hexc('#5f8a2e' if j%2 else '#7aa83a',235),width=S(10),joint='curve')
    elif name=='sunset':
        sy=S(820)+p*S(170);sx=S(560)
        img=add_glow(img,(sx,sy),S(700),(255,170,90),.6)
        d=ImageDraw.Draw(img,'RGBA');d.ellipse((sx-S(120),sy-S(120),sx+S(120),sy+S(120)),fill=hexc('#ffe7a8'))
        # re-cover horizon so sun sinks behind hills
        st=static('sunset');img.paste(st.crop((0,S(1010),S(W),S(H))),(0,S(1010)));d=ImageDraw.Draw(img,'RGBA')
        for x,top in [(170,640),(560,700),(940,610)]:pass
        rng=np.random.default_rng(5)
        rng=np.random.default_rng(5)
        for row in range(14):  # mustard field: scattered clumps, farther = smaller and paler
            depth=row/13;y0=S(1125+depth**1.4*760);n=int(110-depth*40)
            for i in range(n):
                x=rng.uniform(-S(20),S(W+20))+math.sin(t*2+i*.9+row)*S(3+8*depth);y=y0+rng.uniform(-S(30),S(30));r=S(5+16*depth)*rng.uniform(.7,1.2)
                d.line((x,y+r*3,x+math.sin(t*2+i)*r*.4,y),fill=hexc('#5d7a22',190),width=max(1,int(S(1+2*depth))))
                for a in range(int(4+3*depth)):
                    ang=rng.uniform(0,6.28);rr=r*rng.uniform(.2,1.0);fx=x+math.cos(ang)*rr;fy=y+math.sin(ang)*rr*.7;pr=r*rng.uniform(.25,.45)
                    d.ellipse((fx-pr,fy-pr,fx+pr,fy+pr),fill=mix(hexc('#e8b81a')[:3],hexc('#ffe066')[:3],rng.random())+(int(200+55*depth),))
        for k in range(5):  # birds
            bx=S(-80)+((t*.12+k*.19)%1.2)*S(1250);by=S(420+k*55)+math.sin(t*2+k)*S(12);fl=math.sin(t*12+k)*S(10)
            d.line([(bx-S(22),by-fl),(bx,by),(bx+S(22),by-fl)],fill=hexc('#2a2030'),width=S(4),joint='curve')
    elif name=='dibiya':
        cx,base=S(540),S(1150)
        fl=.85+.15*math.sin(t*13)+.06*math.sin(t*31)
        img=add_glow(img,(cx,S(1060)),S(760)*fl,(255,170,80),.75);d=ImageDraw.Draw(img,'RGBA')
        d.rounded_rectangle((cx-S(55),base-S(70),cx+S(55),base),radius=S(14),fill=hexc('#5c5c5c'));d.rectangle((cx-S(60),base-S(78),cx+S(60),base-S(64)),fill=hexc('#7a7a7a'))
        d.rectangle((cx-S(6),base-S(110),cx+S(6),base-S(76)),fill=hexc('#2a2a2a'))
        flame(d,cx,base-S(104),S(90)*fl,S(22),t,1.0)
        rng=np.random.default_rng(9)
        for i in range(30):
            ph=(rng.random()+t*.05*(1+rng.random()))%1;x=rng.uniform(S(200),S(880))+math.sin(t+i)*S(15);y=S(1400)-ph*S(900)
            d.ellipse((x,y,x+S(4),y+S(4)),fill=(255,220,170,int(110*math.sin(ph*math.pi))))
    elif name in('door','opendoor'):
        x0,x1,y0,y1=S(280),S(800),S(550),S(1395);mid=(x0+x1)//2
        if name=='opendoor':
            op=ease((t-.4)/2.6)
            village(img,x0,x1,y0,y1);d=ImageDraw.Draw(img,'RGBA')
            img=add_glow(img,(mid,S(1000)),S(900),(255,200,120),.45*op);d=ImageDraw.Draw(img,'RGBA')
            # light spilling on the floor
            spread=S(40)+op*S(330);d.polygon([(mid-S(10)-op*S(250),y1),(mid+S(10)+op*S(250),y1),(mid+spread+S(250),S(1920)),(mid-spread-S(250),S(1920))],fill=(255,230,170,int(90*op)))
        else:op=0
        def panel(xa,xb,mirror):
            if xb-xa<S(6):return
            d.rectangle((xa,y0,xb,y1),fill=hexc('#6b3f22'))
            n=4
            for i in range(1,n):xx=xa+(xb-xa)*i/n;d.line((xx,y0,xx,y1),fill=hexc('#4e2c16'),width=S(3))
            for yy in (y0+S(80),y0+(y1-y0)//2,y1-S(80)):
                d.rectangle((xa,yy-S(14),xb,yy+S(14)),fill=hexc('#4a2a16'))
                for i in range(5):sx=xa+(xb-xa)*(i+.5)/5;d.ellipse((sx-S(7),yy-S(7),sx+S(7),yy+S(7)),fill=hexc('#2b2b2b'))
            # rust on hinges
            hx=xa if not mirror else xb
            for yy in (y0+S(80),y1-S(80)):d.ellipse((hx-S(16),yy-S(22),hx+S(16),yy+S(22)),fill=hexc('#8a3f1a',220))
        panel(x0,mid,False)
        w2=(x1-mid)*(1-.86*op);panel(mid,mid+int(w2),True)
        if name=='door':
            sw=math.sin(t*1.4)*S(10)  # hanging kadi chain + lock
            ky=y0+(y1-y0)//2;pts=[(mid+S(30),ky-S(40))]
            for i in range(1,7):pts.append((mid+S(30)+sw*i/6,ky-S(40)+i*S(18)))
            for (a,b) in zip(pts,pts[1:]):d.ellipse((a[0]-S(8),a[1]-S(6),a[0]+S(8),a[1]+S(10)),outline=hexc('#3a3a3a'),width=S(4))
            lx,ly=pts[-1];d.rounded_rectangle((lx-S(30),ly+S(14),lx+S(30),ly+S(74)),radius=S(10),fill=hexc('#b78a2e'));d.arc((lx-S(20),ly-S(10),lx+S(20),ly+S(30)),180,360,fill=hexc('#5a5a5a'),width=S(7))
            d.ellipse((lx-S(5),ly+S(38),lx+S(5),ly+S(50)),fill=hexc('#3a2a10'))
            lfx=S(900)-p*S(420)+math.sin(t*3)*S(40);lfy=S(500)+p*S(900)
            d.ellipse((lfx-S(22),lfy-S(10),lfx+S(22),lfy+S(10)),fill=hexc('#a0702a',230))
        rng=np.random.default_rng(14)
        for i in range(26):
            ph=(rng.random()+t*.04*(1+rng.random()))%1;x=rng.uniform(S(150),S(950));y=S(1500)-ph*S(1000)
            d.ellipse((x,y,x+S(4),y+S(4)),fill=(255,236,200,int(90*math.sin(ph*math.pi))))
    elif name=='city':
        base=S(1500)
        for i,(bx,bw,bh,wins) in enumerate(BUILDINGS):
            x0=S(bx);x1=S(bx+bw);y0=base-S(bh)
            d.rectangle((x0,y0,x1,base),fill=hexc('#07061a' if i%2 else '#0c0a24'));d.line((x0,y0,x1,y0),fill=hexc('#6a5acd',160),width=S(3))
            cols=max(2,int(bw//34));rows=int(bh//52)
            for r in range(rows):
                for c in range(cols):
                    seed,col=wins[(r*cols+c)%len(wins)]
                    on=math.sin(t*3+seed*40)>-.2
                    if seed<.35 or not on:continue
                    wx=x0+S(14)+c*S(34);wy=y0+S(20)+r*S(52)
                    if wx+S(18)>x1-S(8):continue
                    d.rectangle((wx,wy,wx+S(18),wy+S(28)),fill=hexc(col,220))
        d.rectangle((0,base,S(W),S(H)),fill=hexc('#0d0b22'))
        gx,gy=S(540),S(760);pulse=.7+.3*math.sin(t*5)
        img=add_glow(img,(gx,gy),S(900),(255,230,200),.5*pulse);img=add_glow(img,(S(220),S(980)),S(500),(255,90,200),.35);img=add_glow(img,(S(880),S(1050)),S(500),(80,220,255),.35)
        d=ImageDraw.Draw(img,'RGBA')
        # web of glare: radial spokes + rings
        rot=t*.08;spokes=16
        for k in range(spokes):
            a=rot+k*2*math.pi/spokes;d.line((gx,gy,gx+math.cos(a)*S(1300),gy+math.sin(a)*S(1300)),fill=(255,240,210,70),width=S(3))
        for ring in range(1,9):
            r=S(70)*ring*(1+.05*math.sin(t*2+ring));pts=[(gx+math.cos(rot+k*2*math.pi/spokes)*r,gy+math.sin(rot+k*2*math.pi/spokes)*r) for k in range(spokes+1)]
            d.line(pts,fill=(255,240,210,80),width=S(3))
        # small paper kite caught in the web, fluttering
        kx,ky=gx+S(250),gy+S(170);fl=math.sin(t*9)*S(10)
        d.polygon([(kx,ky-S(70)),(kx+S(55)+fl,ky),(kx,ky+S(80)),(kx-S(55)+fl,ky)],fill=hexc('#ff6b3a'));d.line((kx,ky-S(70),kx,ky+S(80)),fill=hexc('#ffe0b0'),width=S(3));d.line((kx-S(55)+fl,ky,kx+S(55)+fl,ky),fill=hexc('#ffe0b0'),width=S(3))
        d.line([(kx,ky+S(80)),(kx+S(20)+fl,ky+S(140)),(kx-S(10),ky+S(200)),(kx+S(15)+fl,ky+S(260))],fill=hexc('#ffe0b0',200),width=S(3),joint='curve')
        for j in range(3):tx,ty=kx+S(10*j)+fl,ky+S(150+50*j);d.polygon([(tx,ty),(tx+S(16),ty+S(10)),(tx,ty+S(20))],fill=hexc('#ffd23a'))
    elif name=='charkha':
        # through the open door: dusty path to the village under soft sky
        x0,x1,y0,y1=S(280),S(800),S(550),S(1395)
        village(img,x0,x1,y0,y1);d=ImageDraw.Draw(img,'RGBA')
        d.rectangle((x0,y0,x0+S(22),y1),fill=hexc('#6b3f22'));d.rectangle((x1-S(70),y0,x1,y1),fill=hexc('#6b3f22'))
        img=add_glow(img,((x0+x1)//2,S(1000)),S(800),(255,200,130),.35);d=ImageDraw.Draw(img,'RGBA')
        # charkha in foreground
        cx,cy,R=S(560),S(1500),S(250);ang=t*.55
        d.rounded_rectangle((S(180),S(1735),S(980),S(1790)),radius=S(16),fill=hexc('#5a3a1e'))
        d.polygon([(cx-S(30),S(1740)),(cx+S(30),S(1740)),(cx+S(14),cy),(cx-S(14),cy)],fill=hexc('#6b4426'))
        d.ellipse((cx-R,cy-R,cx+R,cy+R),outline=hexc('#7a4c26'),width=S(14))
        for k in range(8):a=ang+k*math.pi/8*2;d.line((cx,cy,cx+math.cos(a)*R,cy+math.sin(a)*R),fill=hexc('#7a4c26'),width=S(8))
        for k in range(16):a=ang+k*math.pi/8;d.line((cx+math.cos(a)*R*.97,cy+math.sin(a)*R*.97,cx+math.cos(a+math.pi/8)*R*.97,cy+math.sin(a+math.pi/8)*R*.97),fill=hexc('#c9a070'),width=S(3))
        d.ellipse((cx-S(22),cy-S(22),cx+S(22),cy+S(22)),fill=hexc('#4a2e16'))
        d.line((cx+math.cos(ang)*S(60),cy+math.sin(ang)*S(60),cx+math.cos(ang)*S(60)+S(30),cy+math.sin(ang)*S(60)+S(60)),fill=hexc('#4a2e16'),width=S(10))
        d.rounded_rectangle((S(800),S(1660),S(900),S(1740)),radius=S(8),fill=hexc('#6b4426'));d.line((cx,cy-R,S(850),S(1665)),fill=(240,230,210,170),width=S(2))
        rng=np.random.default_rng(31)  # termite holes on base and spindle stand
        for _ in range(60):
            x=rng.uniform(S(190),S(970));y=rng.uniform(S(1742),S(1785));r=rng.uniform(S(2),S(6));d.ellipse((x-r,y-r,x+r,y+r),fill=hexc('#2a1a0c',220))
        for _ in range(18):
            a=rng.uniform(0,2*math.pi);x=cx+math.cos(a)*R;y=cy+math.sin(a)*R;r=rng.uniform(S(3),S(6));d.ellipse((x-r,y-r,x+r,y+r),fill=hexc('#2a1a0c',200))
        rng=np.random.default_rng(15)
        for i in range(24):
            ph=(rng.random()+t*.04*(1+rng.random()))%1;x=rng.uniform(S(250),S(830));y=S(1450)-ph*S(900)
            d.ellipse((x,y,x+S(4),y+S(4)),fill=(255,240,200,int(100*math.sin(ph*math.pi))))
    return img

# ---------- finishing ----------
def make_grain(seed):
    rng=np.random.default_rng(seed);n=rng.normal(0,1,(H//2,W//2)).astype(np.float32)
    return Image.fromarray((128+n*22).clip(0,255).astype(np.uint8),'L').resize((W,H),Image.BILINEAR)
GRAIN=[make_grain(s) for s in range(4)]
def vignette():
    y,x=np.ogrid[:H,:W];d=np.sqrt(((x-W/2)/(W*.75))**2+((y-H/2)/(H*.72))**2);v=np.clip(1-.42*d**2.2,0,1)
    return Image.fromarray((v*255).astype(np.uint8),'L')
VIG=vignette()
PAPER=None
def finish(img,frame):
    global PAPER
    rgb=np.asarray(img,dtype=np.float32)
    g=(np.asarray(GRAIN[frame//3%4],dtype=np.float32)-128)/128
    rgb=rgb*(1+g[...,None]*.07)
    rgb=rgb*(np.asarray(VIG,dtype=np.float32)[...,None]/255*.85+.15)
    return Image.fromarray(rgb.clip(0,255).astype(np.uint8),'RGB')

def camera(img,name,p):
    # gentle push-in (or pull-out for the opening door) on every shot
    z=1.0+.06*(1-ease(p)) if name=='opendoor' else 1.0+.06*ease(p)
    cw,ch=int(W/z),int(H/z);ox=(W-cw)//2;oy=int((H-ch)*.5)
    return img.crop((ox,oy,ox+cw,oy+ch)).resize((W,H),Image.BICUBIC)

def render_scene(name,t,dur):
    big=scene_frame(name,t,dur);img=big.reduce(SS);return camera(img,name,t/dur)

def caption_layer(t):
    from song_animation.lyrics import font
    layer=Image.new('RGBA',(W,H),(0,0,0,0));d=ImageDraw.Draw(layer)
    for a,b,text in CUES:
        if not a-.2<=t<=b+.2:continue
        alpha=min(1,(t-(a-.2))/.35,((b+.2)-t)/.35)
        lines=text.split('\n');size=58
        while True:  # never let a line touch the frame edge
            f=font(size,text);widest=max(d.textbbox((0,0),ln,font=f)[2]-d.textbbox((0,0),ln,font=f)[0] for ln in lines)
            if widest<=W-120 or size<=40:break
            size-=2
        y=1585-(len(lines)-1)*44
        for ln in lines:
            box=d.textbbox((0,0),ln,font=f);tw=box[2]-box[0];x=(W-tw)//2
            for dx,dy in((0,4),(2,3),(-2,3)):d.text((x+dx,y+dy),ln,font=f,fill=(30,15,8,int(170*alpha)))
            d.text((x,y),ln,font=f,fill=(255,243,220,int(255*alpha)));y+=88
    return layer

def frame_at(i,captions):
    t=i/FPS;idx=next(k for k,(a,b,_) in enumerate(SCENES) if t<b or k==len(SCENES)-1)
    a,b,name=SCENES[idx];img=render_scene(name,t-a,b-a)
    if idx+1<len(SCENES) and t>b-XF:  # crossfade into next
        a2,b2,n2=SCENES[idx+1];nxt=render_scene(n2,max(0,t-a2),b2-a2);img=Image.blend(img,nxt,ease((t-(b-XF))/XF))
    if t>CLIP_LEN-.8:img=Image.blend(img,Image.new('RGB',(W,H),(20,10,6)),ease((t-(CLIP_LEN-.8))/.8))
    img=finish(img,i)
    if captions:img=Image.alpha_composite(img.convert('RGBA'),caption_layer(t)).convert('RGB')
    return img

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--audio',required=True);ap.add_argument('--out',default='gaon_film')
    ap.add_argument('--no-captions',action='store_true');ap.add_argument('--stills',default='');ap.add_argument('--seconds',type=float,default=CLIP_LEN)
    args=ap.parse_args();out=Path(args.out);out.mkdir(parents=True,exist_ok=True);captions=not args.no_captions
    if args.stills:
        for s in args.stills.split(','):frame_at(int(float(s)*FPS),captions).save(out/f'still_{float(s):05.2f}.jpg',quality=90)
        return
    n=int(round(args.seconds*FPS));video=out/'gaon_film.mp4'
    p=subprocess.Popen(['ffmpeg','-y','-v','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-',
        '-ss',str(CLIP_START),'-t',str(args.seconds),'-i',args.audio,'-map','0:v','-map','1:a','-c:v','libx264','-preset','medium','-crf','19',
        '-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-af','afade=t=out:st=%.2f:d=0.8'%(args.seconds-.8),'-shortest','-movflags','+faststart',str(video)],stdin=subprocess.PIPE)
    for i in range(n):
        p.stdin.write(frame_at(i,captions).tobytes())
        if i%90==0:print('frame',i,'/',n,flush=True)
    p.stdin.close()
    if p.wait():raise RuntimeError('ffmpeg encode failed')
    (out/'gaon_film.json').write_text(json.dumps({'audio':args.audio,'clip_start':CLIP_START,'seconds':args.seconds,'scenes':SCENES,'captions':captions},ensure_ascii=False,indent=1))
    print('wrote',video)

if __name__=='__main__':main()
