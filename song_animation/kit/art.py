"""Flat, warm, paper-grain illustration kit drawn with Pillow.

Everything is drawn at SS x resolution and reduced, so edges stay smooth.
A shot = background (outdoor sky+ground, or indoor wall+light) + objects + effects.
Objects are anchored bottom-centre at (x, y) given as fractions of the frame.
"""
import math
import numpy as np
from PIL import Image,ImageDraw,ImageChops

W,H=1080,1920;SS=2;CW,CH=W*SS,H*SS
def S(v):return int(round(v*SS))
def hexc(h,a=255):h=h.lstrip('#');return (int(h[0:2],16),int(h[2:4],16),int(h[4:6],16),a)
def mix(c1,c2,t):return tuple(int(round(a+(b-a)*t)) for a,b in zip(c1,c2))
def ease(x):x=min(1,max(0,x));return x*x*(3-2*x)

class SafeDraw:
    """ImageDraw wrapper: width/radius may be floats (scaled sizes); Pillow needs ints."""
    def __init__(self,d):self._d=d
    def __getattr__(self,name):
        fn=getattr(self._d,name)
        def call(*a,**k):
            for key in('width','radius'):
                if key in k:k[key]=max(1,int(round(k[key])))
            return fn(*a,**k)
        return call

def Draw(img):return SafeDraw(ImageDraw.Draw(img,'RGBA'))

class Canvas:
    """Image + draw handle; glows replace the image, so always draw via c.d."""
    def __init__(self,img):self.img=img;self.d=Draw(img)
    def glow(self,center,radius,color,strength=1.0):
        q=8;w,h=self.img.width//q,self.img.height//q;y,x=np.ogrid[:h,:w]
        dd=np.sqrt((x-center[0]/q)**2+(y-center[1]/q)**2)/(radius/q);a=np.clip(1-dd,0,1)**2*strength
        g=Image.fromarray((a[...,None]*np.array(color[:3])[None,None,:]).clip(0,255).astype(np.uint8),'RGB').resize(self.img.size,Image.BILINEAR)
        self.img=ImageChops.add(self.img,g);self.d=Draw(self.img)

def vgrad(w,h,stops):
    ys=np.linspace(0,1,h)[:,None];out=np.zeros((h,1,3))
    for (p0,c0),(p1,c1) in zip(stops,stops[1:]):
        m=(ys>=p0)&(ys<=p1);t=np.clip((ys-p0)/max(1e-6,p1-p0),0,1)
        for k in range(3):out[...,k]=np.where(m,hexc(c0)[k]+(hexc(c1)[k]-hexc(c0)[k])*t,out[...,k])
    return Image.fromarray(np.repeat(out,w,axis=1).astype(np.uint8),'RGB')

def mottle(c,box,base,seed,spots=260,dark=.1):
    rng=np.random.default_rng(seed);x0,y0,x1,y1=box
    for _ in range(spots):
        x=rng.uniform(x0,x1);y=rng.uniform(y0,y1);r=rng.uniform(S(6),S(40))
        col=mix(hexc(base)[:3],(0,0,0) if rng.random()<.6 else (255,240,210),rng.uniform(.02,dark))
        c.d.ellipse((x-r,y-r*.6,x+r,y+r*.6),fill=col+(int(rng.uniform(25,60)),))

def bricks(c,box,seed):
    rng=np.random.default_rng(seed);x0,y0,x1,y1=box;bh=S(26);bw=S(62)
    for r,y in enumerate(range(int(y0),int(y1),bh)):
        off=(bw//2)*(r%2)
        for x in range(int(x0)-off,int(x1),bw):
            if rng.random()<.25:continue
            xa,xb=max(x0,x+S(3)),min(x1,x+bw-S(3))
            if xb-xa<S(8):continue
            c.d.rounded_rectangle((xa,y+S(3),xb,y+bh-S(3)),radius=S(3),fill=mix(hexc('#a4543a')[:3],hexc('#7d3b27')[:3],rng.random())+(235,))

def cracks(c,start,seed,n=3):
    rng=np.random.default_rng(seed)
    for _ in range(n):
        x,y=start[0]+rng.uniform(-S(40),S(40)),start[1]+rng.uniform(-S(40),S(40));pts=[(x,y)]
        for _ in range(7):x+=rng.uniform(-S(28),S(28));y+=rng.uniform(S(10),S(36));pts.append((x,y))
        c.d.line(pts,fill=(70,40,25,110),width=S(2),joint='curve')

# ---------------- backgrounds ----------------
SKIES={
 'dawn':[(0,'#4a5a9a'),(.35,'#c9a0c0'),(.55,'#ffd0a0')],
 'day':[(0,'#8ec5e8'),(.4,'#cfe6ef'),(.55,'#f7ecd0')],
 'golden':[(0,'#f7e7b4'),(.35,'#f3d08a'),(.55,'#e9c27e')],
 'dusk':[(0,'#3d3a78'),(.25,'#8a5a9a'),(.45,'#f08a6a'),(.55,'#ffc97a')],
 'night':[(0,'#0b0d2a'),(.4,'#1d1a4a'),(.55,'#2a2a5a')],
 'rain':[(0,'#4a5560'),(.4,'#6f7c86'),(.55,'#8e9aa0')],
}
GROUNDS={  # (top colour, bottom colour, horizon style)
 'field':('#9fae5a','#5f7a33','hills'),'mustard':('#b39a2a','#8a7a1e','hills'),'river':('#7aa04a','#4f6a2a','river'),
 'road':('#b49a6a','#8a6a40','road'),'village':('#c9a06a','#9a7040','lane'),'hills':('#7a9a5a','#4a6a3a','bighills'),
 'desert':('#e0b878','#c08a50','dunes'),'city':('#2a2840','#14122a','skyline'),'courtyard':('#b07a4a','#7a4a2a','wall'),
}
NIGHTISH=('night','rain')

def outdoor(sky,ground,seed=1):
    st=SKIES.get(sky,SKIES['day']);gt,gb,style=GROUNDS.get(ground,GROUNDS['field'])
    hz=.58;img=vgrad(CW,CH,[(p*hz/.55,c) for p,c in st]+[(hz,st[-1][1]),(hz+.002,gt),(1,gb)])
    c=Canvas(img);dk=sky in NIGHTISH;y0=int(CH*hz)
    shade=lambda h,a=255:mix(hexc(h)[:3],(20,20,50),.55 if dk else 0)+(a,)
    if style in('hills','river','bighills'):
        amp=S(90 if style=='bighills' else 45)
        pts=[(0,y0)]+[(x,y0-amp*(.6+.4*math.sin(x/S(170)+seed))) for x in range(0,CW+S(40),S(40))]+[(CW,y0+S(4)),(0,y0+S(4))]
        c.d.polygon(pts,fill=shade('#8a8ab0' if style=='bighills' else '#a89a7a',200))
    if style=='river':
        c.d.polygon([(S(380),y0),(S(700),y0),(CW,S(1600)),(CW,CH),(0,CH),(0,S(1650))],fill=shade('#5a8ab0'))
        for i in range(18):yy=y0+S(30)+i*S(70);c.d.line((S(300)-i*S(14),yy,S(780)+i*S(16),yy+S(10)),fill=shade('#a9cbe0',90),width=S(4))
    if style=='road':
        c.d.polygon([(S(500),y0),(S(580),y0),(S(900),CH),(S(180),CH)],fill=shade('#6a6060'))
        for i in range(8):yy=y0+S(40)+S(i*i*14);c.d.rectangle((S(536),yy,S(544),yy+S(12+i*6)),fill=shade('#e8d8a0'))
    if style=='lane':
        c.d.polygon([(S(460),y0),(S(620),y0),(S(1000),CH),(S(80),CH)],fill=shade('#d8b880'))
    if style=='dunes':
        for k in range(3):c.d.ellipse((S(-300+k*420),y0-S(60),S(500+k*420),y0+S(200)),fill=shade('#d8a868'))
    if style=='skyline':
        rng=np.random.default_rng(seed);x=-S(20)
        while x<CW:
            bw=rng.uniform(S(90),S(190));bh=rng.uniform(S(250),S(800));c.d.rectangle((x,y0-bh,x+bw,y0+S(4)),fill=hexc('#0c0a24' if rng.random()<.5 else '#14123a'))
            for r in range(int(bh//S(52))):
                for k in range(int(bw//S(34))):
                    if rng.random()<.45:c.d.rectangle((x+S(12)+k*S(34),y0-bh+S(18)+r*S(52),x+S(28)+k*S(34),y0-bh+S(44)+r*S(52)),fill=hexc(['#ffd27a','#7af0ff','#ff7ad1','#fff2c0'][int(rng.integers(4))],200))
            x+=bw
    if style=='skyline':
        c.d.rectangle((0,y0+S(4),CW,CH),fill=hexc('#15132e'))
        rng2=np.random.default_rng(seed+5)
        for i in range(40):
            x=rng2.uniform(0,CW);col=['#ffd27a','#7af0ff','#ff7ad1'][i%3];c.d.line((x,y0+S(20),x+rng2.uniform(-S(20),S(20)),y0+rng2.uniform(S(200),S(700))),fill=hexc(col,50),width=S(6))
        c.d.polygon([(S(470),y0+S(4)),(S(610),y0+S(4)),(S(950),CH),(S(130),CH)],fill=hexc('#22203f'))
        for i in range(7):yy=y0+S(40)+S(i*i*16);c.d.rectangle((S(536),yy,S(544),yy+S(14+i*6)),fill=hexc('#e8d8a0',160))
    if style=='wall':
        c.d.rectangle((0,y0-S(260),CW,y0),fill=shade('#b88a5a'));mottle(c,(0,y0-S(260),CW,y0),'#b88a5a',seed+3,90)
    if style in('hills','river','road','lane','bighills','dunes'):
        for i in range(12):
            yy=y0+S(40)+S(i*i*11)
            if yy<CH:c.d.line((0,yy,CW,yy+S(20)),fill=shade(gb,45),width=S(5))
    if sky=='night':
        rng=np.random.default_rng(seed+9)
        for _ in range(120):x,y=rng.uniform(0,CW),rng.uniform(0,y0*.85);c.d.ellipse((x,y,x+S(3),y+S(3)),fill=(255,255,255,int(rng.uniform(60,200))))
    return c.img

WALLS={'mud':('#8a5a3a','#6e3a24'),'brick':('#9a5a3a','#7a3a24'),'plaster':('#d8c8a8','#b8a080'),'blue':('#5a7a9a','#3a5a7a')}
def indoor(wall='mud',light='day',seed=1):
    a,b=WALLS.get(wall,WALLS['mud']);fl=.74
    if light=='night':a,b=mix(hexc(a)[:3],(30,20,30),.5),mix(hexc(b)[:3],(30,20,30),.5);a='#%02x%02x%02x'%a;b='#%02x%02x%02x'%b
    img=vgrad(CW,CH,[(0,a),(fl,b),(fl+.002,'#5e3822'),(1,'#3e2416')]);c=Canvas(img)
    mottle(c,(0,0,CW,int(CH*fl)),a,seed,360,.12);mottle(c,(0,int(CH*fl),CW,CH),'#5e3822',seed+1,120)
    if wall=='brick':bricks(c,(0,0,CW,int(CH*fl)),seed)
    else:bricks(c,(S(60),S(160),S(330),S(330)),seed+2);cracks(c,(S(900),S(260)),seed+3,2)
    c.d.line((0,int(CH*fl),CW,int(CH*fl)),fill=hexc('#2a150d',180),width=S(4))
    return c.img

# ---------------- people (flat silhouettes, no faces/hands) ----------------
def person(c,x,y,s,t,tone='#3a2a2a',kind='man',pose='stand',facing=1):
    col=hexc(tone);bob=math.sin(t*2.2)*S(3)*s;h=S(330)*s
    if kind=='child':h*=.62
    hy=y-h+bob;r=h*.085
    if pose=='sit':  # seated figure in profile: folded legs, upright back, head covered by pallu for women
        c.d.rounded_rectangle((x-h*.26,y-h*.16,x+h*.2,y),radius=int(h*.07),fill=col)
        c.d.polygon([(x-h*.16,y-h*.12),(x+h*.08,y-h*.12),(x+h*.05,y-h*.58+bob),(x-h*.12,y-h*.58+bob)],fill=col)
        c.d.ellipse((x-r*1.05,y-h*.58-2.1*r+bob,x+r*1.05,y-h*.58+bob*.5),fill=col)
        if kind in('mother','woman','girl'):
            drape='#8a2a2a' if kind=='mother' else '#c0405a'
            c.d.polygon([(x-r*1.25,y-h*.58-1.6*r+bob),(x+r*.4,y-h*.58-2.3*r+bob),(x+r*1.2,y-h*.58-1.2*r+bob),(x-h*.08,y-h*.3),(x-h*.2,y-h*.14),(x-h*.17,y-h*.5)],fill=hexc(drape,235))
        c.d.ellipse((x-h*.3,y-S(8)*s,x+h*.26,y+S(8)*s),fill=(0,0,0,50))
        return
    if kind in('mother','woman','girl'):
        c.d.polygon([(x-h*.2,y),(x+h*.2,y),(x+h*.1,hy+h*.25),(x-h*.1,hy+h*.25)],fill=col)  # saree/skirt
        c.d.rounded_rectangle((x-h*.1,hy+h*.18,x+h*.1,hy+h*.42),radius=int(h*.05),fill=col)
        c.d.ellipse((x-r,hy+h*.02,x+r,hy+h*.02+2*r),fill=col)
        drape='#8a2a2a' if kind=='mother' else '#c0405a'
        c.d.polygon([(x-r*1.2,hy+h*.04),(x+r*1.3,hy+h*.06),(x+h*.16,hy+h*.5),(x-h*.05*facing,hy+h*.3)],fill=hexc(drape,230))
    else:
        c.d.rounded_rectangle((x-h*.11,hy+h*.18,x+h*.11,hy+h*.55),radius=int(h*.05),fill=col)
        ph=math.sin(t*4)*h*.03 if pose=='walk' else 0
        c.d.line((x-h*.05,hy+h*.54,x-h*.06-ph,y),fill=col,width=int(h*.07));c.d.line((x+h*.05,hy+h*.54,x+h*.06+ph,y),fill=col,width=int(h*.07))
        c.d.ellipse((x-r,hy+h*.03,x+r,hy+h*.03+2*r),fill=col)
        if kind=='oldman':c.d.line((x+h*.18*facing,hy+h*.35,x+h*.22*facing,y),fill=hexc('#6a4a2a'),width=int(h*.025))
        if kind in('father','oldman'):c.d.chord((x-r*1.3,hy,x+r*1.3,hy+h*.12),180,360,fill=hexc('#e8a030'))  # pagdi
    c.d.ellipse((x-h*.22,y-S(8)*s,x+h*.22,y+S(8)*s),fill=(0,0,0,50))

# ---------------- objects ----------------
def flame(c,cx,base,hgt,wid,t,seed):
    for k,col in enumerate(('#e8522a','#ff9a3a','#ffdf7a')):
        sc=1-k*.28;ph=t*9+seed+k;hh=hgt*sc*(.85+.15*math.sin(ph*1.7));ww=wid*sc;sw=math.sin(ph)*wid*.18
        c.d.polygon([(cx-ww,base),(cx-ww*.6,base-hh*.45),(cx+sw,base-hh),(cx+ww*.6,base-hh*.45),(cx+ww,base)],fill=hexc(col,235))

def steam(c,x,y,t,n=3,spread=70,height=320):
    for k in range(n):
        ph=(t*.5+k/n)%1;x0=x+S(-spread+k*spread*2/max(1,n-1));pts=[(x0+math.sin(ph*6+j*.6+k)*S(14),y-ph*S(height)-j*S(20)) for j in range(8)]
        c.d.line(pts,fill=(255,248,236,int(120*(1-ph))),width=S(7),joint='curve')

def o_tree(c,x,y,s,t,p):
    tone='#3b5a2a' if not p.get('night') else '#1e2a26';sw=math.sin(t*1.3)*S(8)*s
    c.d.polygon([(x-S(28)*s,y),(x+S(28)*s,y),(x+S(14)*s,y-S(330)*s),(x-S(14)*s,y-S(330)*s)],fill=hexc('#5a3a22'))
    for dx,dy,r,k in [(0,-430,170,0),(-130,-360,130,1),(130,-360,135,2),(-70,-520,120,3),(80,-520,125,4),(0,-600,100,5)]:
        cx=x+S(dx)*s+sw*(1+k*.1);cy=y+S(dy)*s;rr=S(r)*s
        c.d.ellipse((cx-rr,cy-rr*.85,cx+rr,cy+rr*.85),fill=mix(hexc(tone)[:3],(120,160,70),.12*(k%3))+(255,))
def o_palm(c,x,y,s,t,p):
    sw=math.sin(t*1.2)*S(14)*s;tx,ty=x+S(40)*s+sw,y-S(520)*s
    c.d.line([(x,y),(x+S(25)*s,y-S(260)*s),(tx,ty)],fill=hexc('#6a4a2a'),width=S(26)*s,joint='curve')
    for a in range(7):
        ang=-math.pi*.95+a*math.pi*.32;L=S(230)*s;ex,ey=tx+math.cos(ang)*L,ty+math.sin(ang)*L*.6+S(60)*s
        c.d.line([(tx,ty),((tx+ex)/2,min(ty,ey)-S(30)*s),(ex,ey)],fill=hexc('#3f6a2a'),width=S(18)*s,joint='curve')
def o_bush(c,x,y,s,t,p):
    for dx,r in [(-60,70),(0,95),(70,75)]:c.d.ellipse((x+S(dx)*s-S(r)*s,y-S(r)*1.6*s,x+S(dx)*s+S(r)*s,y),fill=hexc('#4a6a2a'))
def o_flowers(c,x,y,s,t,p):
    rng=np.random.default_rng(int(x)%997);col=p.get('color','#e84a6a')
    for i in range(14):
        fx=x+rng.uniform(-S(160),S(160))*s;fy=y-rng.uniform(S(20),S(120))*s+math.sin(t*2+i)*S(4);r=S(14)*s
        c.d.line((fx,y,fx,fy),fill=hexc('#4a6a2a'),width=S(3))
        for a in range(5):aa=a*1.256;c.d.ellipse((fx+math.cos(aa)*r*.8-r*.55,fy+math.sin(aa)*r*.8-r*.55,fx+math.cos(aa)*r*.8+r*.55,fy+math.sin(aa)*r*.8+r*.55),fill=hexc(col))
        c.d.ellipse((fx-r*.35,fy-r*.35,fx+r*.35,fy+r*.35),fill=hexc('#ffd84a'))
def o_sugarcane(c,x,y,s,t,p):
    for i in range(7):
        bx=x+S(-150+i*50)*s;sw=math.sin(t*1.6+i*.7)*S(20)*s;top=y-S(900+((i*53)%180))*s
        c.d.line((bx,y,bx+sw,top),fill=hexc('#8a7a3a' if i%2 else '#9aa04a'),width=S(14)*s)
        for j in range(5):
            yy=top+S(55*j)*s;xx=bx+sw;dr=-1 if (i+j)%2 else 1;L=S(170)*s
            c.d.line([(xx,yy),(xx+dr*L*.45,yy-S(70)*s),(xx+dr*L,yy+S(90)*s)],fill=hexc('#5f8a2e' if j%2 else '#7aa83a',235),width=S(9)*s,joint='curve')
def o_sun(c,x,y,s,t,p):
    r=S(130)*s;c.glow((x,y),S(700)*s,(255,180,100),.55);c.d.ellipse((x-r,y-r,x+r,y+r),fill=hexc('#ffe7a8'))
def o_moon(c,x,y,s,t,p):
    r=S(95)*s;c.glow((x,y),S(500)*s,(200,210,255),.35);c.d.ellipse((x-r,y-r,x+r,y+r),fill=hexc('#f4f0d8'))
    for dx,dy,rr in[(-30,-20,16),(25,25,12),(10,-40,9)]:c.d.ellipse((x+S(dx)*s-S(rr)*s,y+S(dy)*s-S(rr)*s,x+S(dx)*s+S(rr)*s,y+S(dy)*s+S(rr)*s),fill=hexc('#ddd8bc'))
def o_clouds(c,x,y,s,t,p):
    col=hexc('#ffffff',200) if not p.get('night') else hexc('#6a6a8a',160);dx=(t*S(14))%S(200)
    for k,(ox,oy) in enumerate([(-300,0),(150,-120),(420,60)]):
        cx=x+S(ox)*s+dx;cy=y+S(oy)*s
        for ex,r in[(-70,60),(0,85),(80,65)]:c.d.ellipse((cx+S(ex)*s-S(r)*s,cy-S(r)*s,cx+S(ex)*s+S(r)*s,cy+S(r)*.6*s),fill=col)
def o_house(c,x,y,s,t,p):
    w,h=S(300)*s,S(200)*s;c.d.rectangle((x-w/2,y-h,x+w/2,y),fill=hexc('#c98a5a'));mottle(c,(x-w/2,y-h,x+w/2,y),'#c98a5a',int(x)%97,30)
    c.d.polygon([(x-w*.62,y-h),(x,y-h*1.85),(x+w*.62,y-h)],fill=hexc('#a0482a'))
    c.d.rectangle((x-S(35)*s,y-S(120)*s,x+S(35)*s,y),fill=hexc('#5a3420'))
    lit=p.get('night');c.d.rectangle((x+S(70)*s,y-S(150)*s,x+S(120)*s,y-S(100)*s),fill=hexc('#ffd27a' if lit else '#3a2a20'))
    if lit:c.glow((x+S(95)*s,y-S(125)*s),S(200)*s,(255,190,90),.4)
def o_hut(c,x,y,s,t,p):
    w,h=S(280)*s,S(170)*s;c.d.rectangle((x-w/2,y-h,x+w/2,y),fill=hexc('#b07a4a'))
    c.d.polygon([(x-w*.65,y-h+S(10)*s),(x,y-h*2.1),(x+w*.65,y-h+S(10)*s)],fill=hexc('#c99b52'))
    for i in range(12):xx=x-w*.6+i*w*1.2/11;c.d.line((xx,y-h+S(8)*s,x+(xx-x)*.2,y-h*1.9),fill=hexc('#a07a3c',150),width=S(2))
    c.d.rounded_rectangle((x-S(32)*s,y-S(110)*s,x+S(32)*s,y),radius=S(28)*s,fill=hexc('#3a2418'))
def o_well(c,x,y,s,t,p):
    c.d.ellipse((x-S(150)*s,y-S(60)*s,x+S(150)*s,y+S(10)*s),fill=hexc('#8a8278'));c.d.rectangle((x-S(150)*s,y-S(170)*s,x+S(150)*s,y-S(25)*s),fill=hexc('#9a9288'))
    c.d.ellipse((x-S(150)*s,y-S(205)*s,x+S(150)*s,y-S(135)*s),fill=hexc('#b0a89c'));c.d.ellipse((x-S(120)*s,y-S(195)*s,x+S(120)*s,y-S(145)*s),fill=hexc('#1a2a30'))
    for dx in(-130,120):c.d.rectangle((x+S(dx)*s,y-S(380)*s,x+S(dx+12)*s,y-S(170)*s),fill=hexc('#5a3a22'))
    c.d.rectangle((x-S(140)*s,y-S(390)*s,x+S(140)*s,y-S(372)*s),fill=hexc('#5a3a22'));sw=math.sin(t*1.5)*S(8)
    c.d.line((x,y-S(372)*s,x+sw,y-S(240)*s),fill=hexc('#c9b08a'),width=S(3));c.d.rounded_rectangle((x+sw-S(30)*s,y-S(250)*s,x+sw+S(30)*s,y-S(200)*s),radius=S(8),fill=hexc('#b78a2e'))
def o_cow(c,x,y,s,t,p):
    col=hexc(p.get('color','#f0e6d8'));b=S(1)*s;tail=math.sin(t*3)*S(20)*s
    c.d.ellipse((x-220*b,y-260*b,x+180*b,y-110*b),fill=col)
    for lx in(-170,-110,90,140):c.d.rectangle((x+lx*b,y-140*b,x+(lx+26)*b,y),fill=col)
    c.d.polygon([(x+150*b,y-240*b),(x+280*b,y-280*b),(x+300*b,y-200*b),(x+180*b,y-170*b)],fill=col)
    c.d.ellipse((x+250*b,y-240*b,x+320*b,y-190*b),fill=hexc('#d8b8a8'));c.d.line((x+220*b,y-280*b,x+200*b,y-330*b),fill=hexc('#9a8a6a'),width=int(10*b))
    c.d.line((x-215*b,y-230*b,x-250*b+tail,y-110*b),fill=col,width=int(9*b));c.d.ellipse((x-80*b,y-230*b,x+10*b,y-170*b),fill=hexc('#8a6a4a',200))
def o_cart(c,x,y,s,t,p):
    b=S(1)*s;ang=t*.6
    c.d.polygon([(x-230*b,y-170*b),(x+160*b,y-170*b),(x+180*b,y-110*b),(x-210*b,y-110*b)],fill=hexc('#8a5a32'));c.d.line((x+170*b,y-130*b,x+420*b,y-90*b),fill=hexc('#6a4426'),width=int(14*b))
    for cx in(x-120*b,x+60*b):
        R=95*b;cy=y-R;c.d.ellipse((cx-R,cy-R,cx+R,cy+R),outline=hexc('#5a3a1e'),width=int(12*b))
        for k in range(6):a=ang+k*math.pi/3;c.d.line((cx,cy,cx+math.cos(a)*R,cy+math.sin(a)*R),fill=hexc('#5a3a1e'),width=int(7*b))
def o_charpai(c,x,y,s,t,p):
    b=S(1)*s;c.d.polygon([(x-260*b,y-110*b),(x+260*b,y-110*b),(x+300*b,y-60*b),(x-300*b,y-60*b)],fill=hexc('#c9a06a'))
    for i in range(14):xx=x-280*b+i*40*b;c.d.line((xx,y-108*b,xx+20*b,y-62*b),fill=hexc('#8a6a3a',160),width=int(3*b))
    for lx in(-290,270):c.d.rectangle((x+lx*b,y-80*b,x+(lx+22)*b,y),fill=hexc('#6a4426'))
def o_haystack(c,x,y,s,t,p):
    c.d.chord((x-S(180)*s,y-S(330)*s,x+S(180)*s,y+S(30)*s),180,360,fill=hexc('#d8b04a'));c.d.rectangle((x-S(180)*s,y-S(150)*s,x+S(180)*s,y),fill=hexc('#d8b04a'))
    for i in range(16):xx=x-S(170)*s+i*S(22)*s;c.d.line((xx,y,xx+S(10)*s,y-S(140)*s),fill=hexc('#b08a2a',150),width=S(3))
def o_swing(c,x,y,s,t,p):
    o_tree(c,x-S(80)*s,y,s,t,p);a=math.sin(t*1.8)*.35;px,py=x+S(90)*s,y-S(420)*s;L=S(300)*s
    ex,ey=px+math.sin(a)*L,py+math.cos(a)*L;c.d.line((px-S(40)*s,py,ex-S(40)*s,ey),fill=hexc('#c9b08a'),width=S(4));c.d.line((px+S(40)*s,py,ex+S(40)*s,ey),fill=hexc('#c9b08a'),width=S(4))
    c.d.rounded_rectangle((ex-S(60)*s,ey-S(8)*s,ex+S(60)*s,ey+S(12)*s),radius=S(5),fill=hexc('#7a4a26'))
def o_temple(c,x,y,s,t,p):
    b=S(1)*s;c.d.rectangle((x-170*b,y-260*b,x+170*b,y),fill=hexc('#f0e0c0'));c.d.polygon([(x-150*b,y-260*b),(x,y-560*b),(x+150*b,y-260*b)],fill=hexc('#e8a050'))
    for k in range(5):c.d.line((x-150*b+k*15*b,y-260*b-k*55*b,x+150*b-k*15*b,y-260*b-k*55*b),fill=hexc('#c07a30'),width=int(5*b))
    c.d.line((x,y-560*b,x,y-660*b),fill=hexc('#5a3a1e'),width=int(5*b));fl=math.sin(t*4)*20*b
    c.d.polygon([(x,y-660*b),(x+90*b+fl,y-630*b),(x,y-600*b)],fill=hexc('#ff7a1a'))
    c.d.rounded_rectangle((x-55*b,y-180*b,x+55*b,y),radius=int(50*b),fill=hexc('#3a2418'));flame(c,x,y-20*b,60*b,15*b,t,2);c.glow((x,y-60*b),400*b,(255,180,90),.35)
def o_diyas(c,x,y,s,t,p):
    for i in range(5):
        dx=x+S(-240+i*120)*s;c.d.chord((dx-S(40)*s,y-S(40)*s,dx+S(40)*s,y+S(10)*s),0,180,fill=hexc('#b0582a'));flame(c,dx,y-S(12)*s,S(55)*s,S(13)*s,t,i)
    c.glow((x,y-S(40)*s),S(520)*s,(255,170,80),.5)
def o_lantern(c,x,y,s,t,p):
    b=S(1)*s;c.d.rectangle((x-55*b,y-40*b,x+55*b,y),fill=hexc('#7a3a1a'));c.d.rounded_rectangle((x-45*b,y-170*b,x+45*b,y-40*b),radius=int(30*b),fill=hexc('#ffe6a0',200))
    c.d.arc((x-40*b,y-240*b,x+40*b,y-160*b),180,360,fill=hexc('#5a5a5a'),width=int(6*b));flame(c,x,y-50*b,70*b,14*b,t,1);c.glow((x,y-100*b),550*b,(255,180,90),.55)
def o_chulha(c,x,y,s,t,p):
    b=S(1)*s;c.d.rounded_rectangle((x-260*b,y-370*b,x+260*b,y),radius=int(70*b),fill=hexc('#b06a3f'));mottle(c,(x-250*b,y-360*b,x+250*b,y-10*b),'#b06a3f',4,60)
    c.d.chord((x-140*b,y-240*b,x+140*b,y+60*b),180,360,fill=hexc('#1b0c07'));c.d.rectangle((x-140*b,y-91*b,x+140*b,y-2*b),fill=hexc('#1b0c07'))
    for i,o in enumerate((-80,0,80)):flame(c,x+o*b,y-5*b,(150+30*(i==1))*b,55*b,t,i*2.1)
    c.d.ellipse((x-300*b,y-430*b,x+300*b,y-350*b),fill=hexc('#1f1f22'));puff=.5+.5*math.sin(min(1,t*.4)*math.pi);ry=(30+22*puff)*b
    c.d.ellipse((x-200*b,y-400*b-ry,x+200*b,y-384*b),fill=hexc('#f4dca6'));steam(c,x,y-430*b,t)
    c.glow((x,y-80*b),620*b,(255,140,60),.55+.08*math.sin(t*11))
def o_matka(c,x,y,s,t,p):
    for i,dx in enumerate((-90,40,150)):
        b=S(1)*s*(1-.2*i);cx=x+S(dx)*s;c.d.ellipse((cx-80*b,y-170*b,cx+80*b,y),fill=hexc('#b0582a'));c.d.rectangle((cx-38*b,y-200*b,cx+38*b,y-150*b),fill=hexc('#a04a22'));c.d.ellipse((cx-48*b,y-215*b,cx+48*b,y-190*b),fill=hexc('#c06a3a'))
        c.d.arc((cx-60*b,y-130*b,cx+60*b,y-30*b),200,340,fill=hexc('#f0d0a0',140),width=int(5*b))
def o_cycle(c,x,y,s,t,p):
    b=S(1)*s;R=95*b;col=hexc('#2a2a2a');ang=t*(1.5 if p.get('moving') else 0)
    for cx in(x-150*b,x+150*b):
        c.d.ellipse((cx-R,y-2*R,cx+R,y),outline=col,width=int(8*b))
        for k in range(8):a=ang+k*math.pi/4;c.d.line((cx,y-R,cx+math.cos(a)*R,y-R+math.sin(a)*R),fill=hexc('#6a6a6a'),width=int(2*b))
    c.d.line([(x-150*b,y-R),(x-20*b,y-R),(x+60*b,y-230*b),(x-60*b,y-230*b),(x-150*b,y-R)],fill=hexc('#2a5a9a'),width=int(9*b))
    c.d.line([(x-20*b,y-R),(x+150*b,y-R)],fill=hexc('#2a5a9a'),width=int(9*b));c.d.line([(x+60*b,y-230*b),(x+150*b,y-R)],fill=hexc('#2a5a9a'),width=int(9*b))
    c.d.line([(x+60*b,y-230*b),(x+70*b,y-270*b),(x+120*b,y-275*b)],fill=col,width=int(8*b));c.d.ellipse((x-95*b,y-255*b,x-25*b,y-232*b),fill=col)
def o_tractor(c,x,y,s,t,p):
    b=S(1)*s;ang=t*(1.2 if p.get('moving') else 0)
    c.d.rounded_rectangle((x-120*b,y-260*b,x+250*b,y-120*b),radius=int(18*b),fill=hexc('#c0322a'));c.d.rectangle((x-120*b,y-400*b,x+40*b,y-250*b),fill=hexc('#a02a22'))
    c.d.rectangle((x-100*b,y-380*b,x+20*b,y-280*b),fill=hexc('#bfe0f0'));c.d.rectangle((x+180*b,y-330*b,x+200*b,y-260*b),fill=hexc('#3a3a3a'))
    for cx,R in((x-90*b,150*b),(x+210*b,85*b)):
        c.d.ellipse((cx-R,y-2*R,cx+R,y),fill=hexc('#2a2a2a'));c.d.ellipse((cx-R*.5,y-R*1.5,cx+R*.5,y-R*.5),fill=hexc('#e8c040'))
        for k in range(8):a=ang+k*math.pi/4;c.d.line((cx+math.cos(a)*R*.7,y-R+math.sin(a)*R*.7,cx+math.cos(a)*R*.95,y-R+math.sin(a)*R*.95),fill=hexc('#4a4a4a'),width=int(14*b))
def o_pole(c,x,y,s,t,p):
    c.d.rectangle((x,y-S(560)*s,x+S(12)*s,y),fill=hexc('#2a2030'));c.d.rectangle((x-S(50)*s,y-S(540)*s,x+S(62)*s,y-S(530)*s),fill=hexc('#2a2030'))
    c.d.line((0,y-S(500)*s,x,y-S(540)*s,CW,y-S(470)*s),fill=hexc('#2a2030',200),width=S(3),joint='curve')
def o_kite(c,x,y,s,t,p):
    fl=math.sin(t*9)*S(10)*s;b=S(1)*s;kx,ky=x+math.sin(t*.7)*S(40),y
    c.d.polygon([(kx,ky-70*b),(kx+55*b+fl,ky),(kx,ky+80*b),(kx-55*b+fl,ky)],fill=hexc(p.get('color','#ff6b3a')));c.d.line((kx,ky-70*b,kx,ky+80*b),fill=hexc('#ffe0b0'),width=S(3))
    c.d.line([(kx,ky+80*b),(kx+20*b+fl,ky+140*b),(kx-10*b,ky+200*b),(kx+15*b+fl,ky+260*b)],fill=hexc('#ffe0b0',200),width=S(3),joint='curve')
def o_boat(c,x,y,s,t,p):
    b=S(1)*s;bob=math.sin(t*1.6)*8*b;y=y+bob
    c.d.polygon([(x-260*b,y-80*b),(x+260*b,y-80*b),(x+190*b,y),(x-190*b,y)],fill=hexc('#6a4426'));c.d.line((x-40*b,y-80*b,x-40*b,y-420*b),fill=hexc('#4a2e16'),width=int(9*b))
    c.d.polygon([(x-30*b,y-410*b),(x+190*b,y-120*b),(x-30*b,y-110*b)],fill=hexc('#f0e6d0'))
    for i in range(3):c.d.arc((x-300*b+i*200*b,y-10*b,x-180*b+i*200*b,y+30*b),180,360,fill=hexc('#cfe6f0',150),width=int(4*b))
def o_train(c,x,y,s,t,p):
    b=S(1)*s;off=(t*S(140)*s)%S(400) if p.get('moving') else 0;x=x-off
    c.d.line((0,y,CW,y),fill=hexc('#4a4a4a'),width=int(8*b))
    for k in range(4):
        cx=x+k*380*b;col='#2a5a8a' if k else '#8a2a2a';c.d.rounded_rectangle((cx-170*b,y-230*b,cx+170*b,y-30*b),radius=int(20*b),fill=hexc(col))
        for w in range(3):c.d.rectangle((cx-140*b+w*100*b,y-200*b,cx-80*b+w*100*b,y-140*b),fill=hexc('#ffd27a' if p.get('night') else '#cfe6f0'))
        for wx in(-110,110):c.d.ellipse((cx+(wx-30)*b,y-60*b,cx+(wx+30)*b,y),fill=hexc('#2a2a2a'))
def o_bus(c,x,y,s,t,p):
    b=S(1)*s;c.d.rounded_rectangle((x-330*b,y-300*b,x+330*b,y-50*b),radius=int(30*b),fill=hexc('#e8a030'))
    for w in range(5):c.d.rectangle((x-290*b+w*120*b,y-260*b,x-200*b+w*120*b,y-170*b),fill=hexc('#cfe6f0'))
    c.d.rectangle((x-330*b,y-150*b,x+330*b,y-130*b),fill=hexc('#c0322a'))
    for wx in(-200,200):c.d.ellipse((x+(wx-55)*b,y-110*b,x+(wx+55)*b,y),fill=hexc('#2a2a2a'))
def o_streetlamp(c,x,y,s,t,p):
    b=S(1)*s;c.d.rectangle((x-10*b,y-620*b,x+10*b,y),fill=hexc('#2a2a2a'));c.d.line((x,y-620*b,x+120*b,y-640*b),fill=hexc('#2a2a2a'),width=int(12*b))
    c.d.polygon([(x+90*b,y-640*b),(x+150*b,y-640*b),(x+140*b,y-600*b),(x+100*b,y-600*b)],fill=hexc('#ffe6a0'))
    if p.get('night'):c.glow((x+120*b,y-560*b),600*b,(255,200,120),.45);c.d.polygon([(x+100*b,y-600*b),(x+140*b,y-600*b),(x+330*b,y),(x-90*b,y)],fill=(255,230,170,40))
def o_city(c,x,y,s,t,p):
    gx,gy=S(540),S(760);pulse=.7+.3*math.sin(t*5);c.glow((gx,gy),S(900),(255,230,200),.45*pulse)
    if p.get('web',True):
        rot=t*.08
        for k in range(16):a=rot+k*math.pi/8;c.d.line((gx,gy,gx+math.cos(a)*S(1300),gy+math.sin(a)*S(1300)),fill=(255,240,210,60),width=S(3))
        for ring in range(1,9):
            r=S(70)*ring*(1+.05*math.sin(t*2+ring));c.d.line([(gx+math.cos(rot+k*math.pi/8)*r,gy+math.sin(rot+k*math.pi/8)*r) for k in range(17)],fill=(255,240,210,70),width=S(3))
def o_phone(c,x,y,s,t,p):
    b=S(1)*s;c.glow((x,y-260*b),520*b,(140,200,255),.45);c.d.rounded_rectangle((x-120*b,y-500*b,x+120*b,y),radius=int(30*b),fill=hexc('#1a1a22'))
    c.d.rounded_rectangle((x-105*b,y-470*b,x+105*b,y-30*b),radius=int(18*b),fill=hexc('#8ad0ff'))
    for i in range(3):yy=y-420*b+i*120*b+((t*40*b)%120*b if p.get('scroll') else 0);c.d.rounded_rectangle((x-85*b,yy,x+85*b,yy+90*b),radius=int(10*b),fill=hexc('#e8f6ff',200))
def o_letter(c,x,y,s,t,p):
    b=S(1)*s;rot=math.sin(t*1.2)*6*b
    c.d.polygon([(x-200*b,y-260*b+rot),(x+200*b,y-260*b-rot),(x+200*b,y+rot),(x-200*b,y-rot)],fill=hexc('#f3e2c2'))
    c.d.line([(x-200*b,y-260*b+rot),(x,y-120*b),(x+200*b,y-260*b-rot)],fill=hexc('#c9a070'),width=int(6*b));c.d.ellipse((x-30*b,y-150*b,x+30*b,y-90*b),fill=hexc('#a02a22'))
def o_radio(c,x,y,s,t,p):
    b=S(1)*s;c.d.rounded_rectangle((x-220*b,y-260*b,x+220*b,y),radius=int(30*b),fill=hexc('#8a5a32'));c.d.ellipse((x-180*b,y-210*b,x-20*b,y-50*b),fill=hexc('#3a2a1a'))
    for k in range(5):c.d.line((x-170*b,y-190*b+k*30*b,x-30*b,y-190*b+k*30*b),fill=hexc('#6a4a2a'),width=int(4*b))
    c.d.rectangle((x+20*b,y-200*b,x+190*b,y-140*b),fill=hexc('#f0d890'));c.d.line((x+40*b+((t*30)%150)*b,y-200*b,x+40*b+((t*30)%150)*b,y-140*b),fill=hexc('#c0322a'),width=int(4*b))
    for k in range(3):r=(60+((t*80+k*50)%150))*b;c.d.arc((x-100*b-r,y-130*b-r,x-100*b+r,y-130*b+r),200,250,fill=(255,240,210,int(160*(1-r/(210*b)))),width=int(4*b))
def o_clock(c,x,y,s,t,p):
    b=S(1)*s;cx,cy=x,y-180*b;R=170*b;c.d.ellipse((cx-R-14*b,cy-R-14*b,cx+R+14*b,cy+R+14*b),fill=hexc('#6a4426'));c.d.ellipse((cx-R,cy-R,cx+R,cy+R),fill=hexc('#f3e2c2'))
    for k in range(12):a=k*math.pi/6;c.d.line((cx+math.cos(a)*R*.82,cy+math.sin(a)*R*.82,cx+math.cos(a)*R*.94,cy+math.sin(a)*R*.94),fill=hexc('#3a2a1a'),width=int(6*b))
    for L,sp,wd in((.5,.3,10),(.78,2.0,6)):a=t*sp-math.pi/2;c.d.line((cx,cy,cx+math.cos(a)*R*L,cy+math.sin(a)*R*L),fill=hexc('#2a1a0a'),width=int(wd*b))
def o_photo(c,x,y,s,t,p):
    b=S(1)*s;c.d.rectangle((x-170*b,y-420*b,x+170*b,y),fill=hexc('#6a4426'));c.d.rectangle((x-140*b,y-390*b,x+140*b,y-30*b),fill=hexc('#d8c8a0'))
    person(c,x-50*b,y-50*b,s*.75,0,'#6a5a48','father');person(c,x+50*b,y-50*b,s*.7,0,'#6a5a48','mother')
def o_trunk(c,x,y,s,t,p):
    b=S(1)*s;c.d.rounded_rectangle((x-260*b,y-230*b,x+260*b,y),radius=int(16*b),fill=hexc('#3a5a7a'));c.d.rectangle((x-260*b,y-200*b,x+260*b,y-170*b),fill=hexc('#c9a040'))
    c.d.rectangle((x-30*b,y-190*b,x+30*b,y-120*b),fill=hexc('#c9a040'))
def o_charkha(c,x,y,s,t,p):
    b=S(1)*s;cx,cy,R=x,y-260*b,250*b;ang=t*.55
    c.d.rounded_rectangle((x-380*b,y-55*b,x+420*b,y),radius=int(16*b),fill=hexc('#5a3a1e'));c.d.polygon([(cx-30*b,y-50*b),(cx+30*b,y-50*b),(cx+14*b,cy),(cx-14*b,cy)],fill=hexc('#6b4426'))
    c.d.ellipse((cx-R,cy-R,cx+R,cy+R),outline=hexc('#7a4c26'),width=int(14*b))
    for k in range(8):a=ang+k*math.pi/4;c.d.line((cx,cy,cx+math.cos(a)*R,cy+math.sin(a)*R),fill=hexc('#7a4c26'),width=int(8*b))
    c.d.ellipse((cx-22*b,cy-22*b,cx+22*b,cy+22*b),fill=hexc('#4a2e16'))
    if p.get('old'):
        rng=np.random.default_rng(31)
        for _ in range(60):xx=rng.uniform(x-370*b,x+410*b);yy=rng.uniform(y-50*b,y-8*b);r=rng.uniform(2,6)*b;c.d.ellipse((xx-r,yy-r,xx+r,yy+r),fill=hexc('#2a1a0c',220))
def o_niche_lamp(c,x,y,s,t,p):
    b=S(1)*s;x0,x1,y0,y1=x-210*b,x+210*b,y-480*b,y;fl=.85+.15*math.sin(t*13)+.06*math.sin(t*31)
    c.d.rounded_rectangle((x0-26*b,y0-26*b,x1+26*b,y1+30*b),radius=int(210*b),fill=hexc('#6a3c26'));c.d.rounded_rectangle((x0,y0,x1,y1),radius=int(190*b),fill=hexc('#1c0e09'))
    c.d.rectangle((x0-40*b,y1,x1+40*b,y1+40*b),fill=hexc('#7a4a30'));c.glow((x,y-90*b),760*b*fl,(255,170,80),.75)
    c.d.rounded_rectangle((x-55*b,y-70*b,x+55*b,y),radius=int(14*b),fill=hexc('#5c5c5c'));flame(c,x,y-104*b,90*b*fl,22*b,t,1.0)
def o_candle(c,x,y,s,t,p):
    b=S(1)*s;c.d.rectangle((x-30*b,y-220*b,x+30*b,y),fill=hexc('#f3e6c8'));flame(c,x,y-222*b,80*b,16*b,t,3);c.glow((x,y-260*b),520*b,(255,180,90),.55)
def o_door(c,x,y,s,t,p):
    b=S(1)*s;x0,x1,y0,y1=x-260*b,x+260*b,y-845*b,y;mid=x;op=ease(t/2.6) if p.get('open') else 0
    c.d.rectangle((x0-30*b,y0-30*b,x1+30*b,y1),fill=hexc('#3e2618'))
    if op>0:village_view(c,x0,x1,y0,y1);c.glow((mid,y-400*b),900*b,(255,200,120),.4*op);c.d.polygon([(mid-250*op*b,y1),(mid+250*op*b,y1),(mid+600*op*b,CH),(mid-600*op*b,CH)],fill=(255,230,170,int(80*op)))
    def panel(xa,xb):
        if xb-xa<6:return
        c.d.rectangle((xa,y0,xb,y1),fill=hexc('#6b3f22'))
        for i in range(1,4):xx=xa+(xb-xa)*i/4;c.d.line((xx,y0,xx,y1),fill=hexc('#4e2c16'),width=int(3*b))
        for yy in(y0+80*b,(y0+y1)/2,y1-80*b):c.d.rectangle((xa,yy-14*b,xb,yy+14*b),fill=hexc('#4a2a16'))
    panel(x0,mid);panel(mid,mid+(x1-mid)*(1-.86*op))
    if p.get('locked') and not p.get('open'):
        sw=math.sin(t*1.4)*10*b;ky=(y0+y1)/2;lx,ly=mid+30*b+sw,ky+70*b
        for i in range(6):yy=ky-40*b+i*18*b;c.d.ellipse((mid+30*b+sw*i/6-8*b,yy-6*b,mid+30*b+sw*i/6+8*b,yy+10*b),outline=hexc('#3a3a3a'),width=int(4*b))
        c.d.rounded_rectangle((lx-30*b,ly+14*b,lx+30*b,ly+74*b),radius=int(10*b),fill=hexc('#b78a2e'));c.d.arc((lx-20*b,ly-10*b,lx+20*b,ly+30*b),180,360,fill=hexc('#5a5a5a'),width=int(7*b))
def village_view(c,x0,x1,y0,y1):
    x0,x1,y0,y1=int(x0),int(x1),int(y0),int(y1);c.img.paste(vgrad(x1-x0,y1-y0,[(0,'#f6c98a'),(.55,'#f9e2b0'),(.56,'#c9a35a'),(1,'#a88040')]),(x0,y0));c.d=Draw(c.img)
    w=x1-x0;h=y1-y0;c.d.polygon([(x0+w*.38,y1),(x0+w*.62,y1),(x0+w*.52,y0+h*.56),(x0+w*.5,y0+h*.56)],fill=hexc('#e2c48a'))
    c.d.ellipse((x0+w*.63,y0+h*.36,x0+w*.9,y0+h*.52),fill=hexc('#4f6b2a'));c.d.rectangle((x0+w*.12,y0+h*.5,x0+w*.29,y0+h*.57),fill=hexc('#c98a5a'))
    c.d.polygon([(x0+w*.1,y0+h*.5),(x0+w*.2,y0+h*.45),(x0+w*.31,y0+h*.5)],fill=hexc('#a0482a'))
def o_window(c,x,y,s,t,p):
    b=S(1)*s;x0,x1,y0,y1=x-200*b,x+200*b,y-420*b,y;c.d.rectangle((x0-24*b,y0-24*b,x1+24*b,y1+24*b),fill=hexc('#5a3420'))
    sky=p.get('sky','day');c.img.paste(vgrad(int(x1-x0),int(y1-y0),SKIES.get(sky,SKIES['day'])[:2]+[(1,SKIES.get(sky,SKIES['day'])[-1][1])]),(int(x0),int(y0)));c.d=Draw(c.img)
    if sky=='night':c.d.ellipse((x0+230*b,y0+60*b,x0+320*b,y0+150*b),fill=hexc('#f4f0d8'))
    if p.get('rain'):
        rng=np.random.default_rng(int(t*30))
        for _ in range(40):rx=rng.uniform(x0,x1);ry=rng.uniform(y0,y1);c.d.line((rx,ry,rx-6*b,ry+40*b),fill=(220,235,255,150),width=int(3*b))
    c.d.line((x,y0,x,y1),fill=hexc('#5a3420'),width=int(16*b));c.d.line((x0,(y0+y1)/2,x1,(y0+y1)/2),fill=hexc('#5a3420'),width=int(16*b))
def o_kolhu(c,x,y,s,t,p):
    b=S(1)*s;c.d.ellipse((x-140*b,y-60*b,x+140*b,y+20*b),fill=hexc('#7f7a72'));c.d.rectangle((x-90*b,y-210*b,x+90*b,y-30*b),fill=hexc('#8f8a80'));c.d.ellipse((x-90*b,y-240*b,x+90*b,y-180*b),fill=hexc('#a9a399'))
    a=t*1.3;ex,ey=x+math.cos(a)*300*b,y-200*b+math.sin(a)*80*b;c.d.line((x,y-210*b,ex,ey),fill=hexc('#5a3a1e'),width=int(16*b))
def o_web(c,x,y,s,t,p):
    p=dict(p,web=True);o_city(c,x,y,s,t,p)
OBJECTS={
 # name: (function, placement, short description for the director)
 'tree':(o_tree,'ground','big neem/peepal tree'),'palm':(o_palm,'ground','coconut palm'),'bush':(o_bush,'ground','small bush'),
 'flowers':(o_flowers,'ground','flower patch'),'sugarcane':(o_sugarcane,'ground','sugarcane stalks (frame edges)'),
 'sun':(o_sun,'sky','sun with glow'),'moon':(o_moon,'sky','full moon'),'clouds':(o_clouds,'sky','drifting clouds'),'kite':(o_kite,'sky','paper kite'),
 'house':(o_house,'ground','village brick house'),'hut':(o_hut,'ground','thatched hut'),'well':(o_well,'ground','village well with bucket'),
 'cow':(o_cow,'ground','cow side view'),'cart':(o_cart,'ground','bullock cart'),'charpai':(o_charpai,'ground','woven cot'),
 'haystack':(o_haystack,'ground','haystack'),'swing':(o_swing,'ground','swing hanging from a tree'),'temple':(o_temple,'ground','small temple with flag and lamp'),
 'diyas':(o_diyas,'ground','row of clay oil lamps'),'lantern':(o_lantern,'ground','hurricane lantern'),'chulha':(o_chulha,'ground','clay stove with fire, roti on tawa'),
 'matka':(o_matka,'ground','clay water pots'),'cycle':(o_cycle,'ground','bicycle'),'tractor':(o_tractor,'ground','red tractor'),
 'pole':(o_pole,'ground','electric pole with wire'),'boat':(o_boat,'ground','sail boat (use with river)'),'train':(o_train,'ground','train passing'),
 'bus':(o_bus,'ground','bus'),'streetlamp':(o_streetlamp,'ground','street lamp'),'citylights':(o_city,'sky','city glare web of lights (night city)'),
 'phone':(o_phone,'hero','glowing mobile phone'),'letter':(o_letter,'hero','old letter/envelope'),'radio':(o_radio,'hero','old radio playing'),
 'clock':(o_clock,'wall','wall clock, time passing'),'photo':(o_photo,'wall','old family photo frame'),'trunk':(o_trunk,'ground','old tin trunk'),
 'charkha':(o_charkha,'ground','spinning wheel'),'niche_lamp':(o_niche_lamp,'wall','oil lamp in wall niche'),'candle':(o_candle,'ground','candle'),
 'door':(o_door,'ground','old wooden door (params: locked/open)'),'window':(o_window,'wall','window (params: sky, rain)'),'kolhu':(o_kolhu,'ground','sugarcane crusher'),
}
PEOPLE=('mother','father','child','girl','boy','man','woman','oldman','couple')

EFFECTS=('rain','birds','fireflies','dust','embers','stars','leaves','petals','snow')
def effect(c,name,t,night=False):
    rng=np.random.default_rng(hash(name)%1000)
    if name=='rain':
        r2=np.random.default_rng(int(t*30))
        for _ in range(160):x=r2.uniform(0,CW);y=r2.uniform(0,CH);c.d.line((x,y,x-S(8),y+S(60)),fill=(210,225,245,120),width=S(2))
    elif name=='birds':
        for k in range(5):
            bx=S(-80)+((t*.12+k*.19)%1.2)*S(1250);by=S(380+k*55)+math.sin(t*2+k)*S(12);fl=math.sin(t*12+k)*S(10)
            c.d.line([(bx-S(22),by-fl),(bx,by),(bx+S(22),by-fl)],fill=hexc('#2a2030'),width=S(4),joint='curve')
    elif name in('fireflies','dust','embers','petals','leaves','snow'):
        col={'fireflies':(255,240,120),'dust':(255,236,200),'embers':(255,170,70),'petals':(240,120,150),'leaves':(170,120,50),'snow':(250,250,255)}[name]
        n={'fireflies':30,'dust':30,'embers':16,'petals':22,'leaves':12,'snow':80}[name];down=name in('petals','leaves','snow')
        for i in range(n):
            sp=.04*(1+rng.random());ph=(rng.random()+t*sp*(3 if down else 1))%1;x=rng.uniform(0,CW)+math.sin(t*(1+rng.random())+i)*S(30)
            y=(ph*CH) if down else (CH*.85-ph*CH*.7);r=S({'fireflies':5,'dust':3,'embers':4,'petals':9,'leaves':11,'snow':5}[name])
            a=int(220*math.sin(ph*math.pi)) if name!='fireflies' else int(255*(.5+.5*math.sin(t*5+i)))
            if name=='leaves':c.d.ellipse((x-r,y-r*.45,x+r,y+r*.45),fill=col+(a,))
            else:c.d.ellipse((x-r,y-r,x+r,y+r),fill=col+(a,))
            if name=='fireflies' and a>150:c.d.ellipse((x-3*r,y-3*r,x+3*r,y+3*r),fill=col+(40,))
    elif name=='stars':
        for i in range(60):x=rng.uniform(0,CW);y=rng.uniform(0,CH*.5);a=int(140+100*math.sin(t*3+i));c.d.ellipse((x,y,x+S(4),y+S(4)),fill=(255,255,255,a))

def draw_object(c,obj,t,night):
    name=obj['name'];x=obj['x']*CW;y=obj['y']*CH;s=obj.get('scale',1.0);p=dict(obj.get('params') or {});p.setdefault('night',night)
    if name in PEOPLE:
        if name=='couple':
            person(c,x-S(70)*s,y,s,t,'#3a2a2a','man',obj.get('pose','stand'));person(c,x+S(70)*s,y,s*.95,t+.5,'#3a2a2a','woman',obj.get('pose','stand'),-1);return
        if night:c.glow((x,y-S(160)*s),S(300)*s,(255,220,170),.25)
        tone='#5a4a66' if night else '#3a2a2a';person(c,x,y,s,t,tone,name,obj.get('pose','stand'));return
    OBJECTS[name][0](c,x,y,s,t,p)
