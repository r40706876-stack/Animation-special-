"""Original vector-like artwork drawn deterministically with Pillow.
No stock/video downloads, global camera jitter or random per-frame image generation.
"""
import math
from PIL import Image, ImageDraw
from .contract import PALETTES
W,H=540,960

def lerp(a,b,t): return a+(b-a)*t
def ease(t):
    t=max(0,min(1,t));return t*t*(3-2*t)
def curve(points,n=60):
    out=[]
    for i in range(n+1):
        t=i/n; a,b,c,d=points
        out.append(tuple((1-t)**3*a[j]+3*(1-t)**2*t*b[j]+3*(1-t)*t*t*c[j]+t**3*d[j] for j in (0,1)))
    return out

def line(d,points,fill,width=2): d.line(points,fill=fill,width=width,joint='curve')
def ellipse(d,xy,fill,outline=None,width=1): d.ellipse(xy,fill=fill,outline=outline,width=width)

def rose(d,x,y,r,p,open_=1):
    # Each petal keeps its identity as the flower opens.
    for layer,count in [(3,9),(2,8),(1,6)]:
        rr=r*(.23+.18*layer)*(.65+.35*open_)
        for i in range(count):
            ang=i*math.tau/count+layer*.49
            px=x+math.cos(ang)*rr*.54;py=y+math.sin(ang)*rr*.54
            col=['#9c354f','#b73d58',p['accent'],'#df7180'][layer]
            ellipse(d,(px-rr*.64,py-rr*.68,px+rr*.64,py+rr*.68),col,p['ink'])
    ellipse(d,(x-r*.17,y-r*.17,x+r*.17,y+r*.17),'#86364a')
    pts=[]
    for i in range(80):
        t=i/79; a=t*math.tau*2.2;rr=r*.05+r*.26*t
        pts.append((x+math.cos(a)*rr,y+math.sin(a)*rr))
    line(d,pts,'#f0a0a5',1)

def flower(d,x,y,s,p,angle=0):
    # Stem, two leaves and a coherent head: a single asset across all shots.
    def tr(a,b): return (x+s*(a*math.cos(angle)-b*math.sin(angle)),y+s*(a*math.sin(angle)+b*math.cos(angle)))
    line(d,[tr(0,0),tr(-2,95)],p['green'],max(2,int(s*5)))
    d.polygon([tr(0,51),tr(31,31),tr(20,61)],fill=p['green'])
    d.polygon([tr(-1,70),tr(-28,52),tr(-18,78)],fill=p['green'])
    rose(d,x,y,26*s,p)

def paper(p):
    im=Image.new('RGB',(W,H),p['paper']);d=ImageDraw.Draw(im)
    # Repeatable sparse paper grain (no frame flicker).
    for i in range(460):
        x=(i*197+13)%W;y=(i*337+29)%H
        d.line((x,y,x+2,y),fill='#dfd8c9')
    return im

def palm(d,x,y,p,side='receive',grip=0):
    skin='#d7a27b';edge='#815e50'
    # The palm and each digit are separate shapes, with bend controlled by grip.
    if side=='receive':
        d.polygon([(x-39,y+28),(x+36,y+28),(x+32,H+30),(x-34,H+30)],fill='#faf5e8',outline=p['ink'])
        d.rounded_rectangle((x-39,y-64,x+39,y+40),radius=28,fill=skin,outline=edge,width=2)
        for j,h in enumerate((49,68,75,61)):
            xx=x-34+j*18;top=y-59-h+grip*30
            d.rounded_rectangle((xx,top,xx+15,y-30),radius=7,fill=skin,outline=edge,width=2)
        d.rounded_rectangle((x+25,y-33,x+60,y+14),radius=17,fill=skin,outline=edge,width=2)
        line(d,curve([(x-22,y-27),(x,y-5),(x+8,y-10),(x+17,y+10)]),edge,1)
    else:
        d.polygon([(x+25,y-32),(W+30,y-110),(W+30,y-30),(x+31,y+20)],fill=p['blue'],outline=p['ink'])
        d.rounded_rectangle((x-27,y-32,x+49,y+26),radius=18,fill=skin,outline=edge,width=2)
        # Fingers visibly curl/release around the stem.
        for j in range(3):
            xx=x-27+j*14
            d.rounded_rectangle((xx,y-2,xx+12,y+26+24*grip),radius=6,fill=skin,outline=edge,width=1)

def gift(im,u,p,phase):
    d=ImageDraw.Draw(im)
    # quiet concentric framing, then action; no text card.
    for r in (182,203): d.arc((270-r,450-r,270+r,450+r),210,330,fill='#d9bca8',width=1)
    palm(d,254,592,p,grip=.25*ease((phase-.8)/.2))
    approach=ease(phase/.64)
    x=lerp(626,254,approach);y=lerp(332,498,approach)
    # Flower remains in receiving palm after release; giver continues away.
    flower(d,x,y,1.5,p,angle=lerp(-.7,0,approach))
    retreat=ease((phase-.72)/.28)
    palm(d,x+10+retreat*420,y+85-retreat*120,p,'give',grip=1-ease((phase-.62)/.15))
    if phase>.72:
        for k in range(5):
            a=k*math.tau/5-1.5;rr=65+ease((phase-.72)/.28)*22
            xx=254+math.cos(a)*rr;yy=498+math.sin(a)*rr
            line(d,[(xx,yy),(xx+math.cos(a)*9,yy+math.sin(a)*9)],p['accent'],2)

def bloom(im,u,p,phase):
    d=ImageDraw.Draw(im)
    # Individual petal paths, not movement of an entire static picture.
    for j in range(17):
        a=j*2.399;dist=45+((j*37)%130)+phase*150
        x=270+math.cos(a+phase*.4)*dist;y=468+math.sin(a+phase*.4)*dist*1.25
        d.ellipse((x-5,y-8,x+5,y+8),fill=p['accent'],outline=p['ink'])
    rose(d,270,468,lerp(75,150,ease(phase)),p,open_=phase)
    rr=3+ease((phase-.72)/.28)*72
    ellipse(d,(270-rr,468-rr,270+rr,468+rr),p['ink'])

def person(d,x,y,p,col=None,step=0,scale=1,rose_=False):
    col=col or p['muted'];s=scale
    # Top-down shoulders, alternating feet, head and hair.
    for side in (-1,1):
        yy=y+12*s+side*math.sin(step)*8*s
        d.rounded_rectangle((x+side*9*s-4*s,yy,x+side*9*s+4*s,yy+14*s),radius=3,fill=p['ink'])
    ellipse(d,(x-19*s,y-10*s,x+19*s,y+15*s),col,p['ink'])
    ellipse(d,(x-10*s,y-19*s,x+10*s,y+2*s),'#d3a584',p['ink'])
    d.arc((x-10*s,y-19*s,x+10*s,y+2*s),180,355,fill=p['ink'],width=max(2,int(5*s)))
    if rose_: flower(d,x+22*s,y+9*s,.43*s,p,angle=.35)

def crowd(im,u,p,phase):
    d=ImageDraw.Draw(im)
    # Perspective-free paving and awnings keep the silhouette reading clear.
    for y in range(0,H,72):
        line(d,[(0,y),(W,y)],'#d6ccba',1)
        for x in range(-60 if y%144 else 0,W,108):line(d,[(x,y),(x,y+72)],'#d6ccba',1)
    for edge in (0,1):
        for j in range(4):
            x=0 if not edge else 499;y=110+j*195
            d.rectangle((x,y,x+41,y+90),fill='#fff7e6',outline=p['ink'])
            for k in range(5):d.rectangle((x,y+k*18,x+41,y+k*18+8),fill=p['blue'] if j%2 else p['green'])
    # Reproducible lanes; foreground walkers avoid the central owner.
    for j in range(18):
        lane=j%6;xx=80+lane*75
        direction=1 if lane%2 else -1
        yy=((j*139+u*direction*72)%1150)-95
        if abs(xx-270)<70 and abs(yy-485)<100:xx+=95 if xx>=270 else -95
        person(d,xx,yy,p,step=u*6+j,scale=.79)
    ellipse(d,(226,441,314,533),p['paper'])
    person(d,270,485,p,p['accent'],0,1.2,True)

def paths(im,u,p,phase):
    d=ImageDraw.Draw(im)
    left=curve([(270,760),(255,590),(160,510),(95,190)])
    right=curve([(270,760),(285,590),(380,510),(445,190)])
    for pts in (left,right):
        line(d,pts,'#d9c9b2',43);line(d,pts,p['paper'],37)
    ix=int(ease(phase)*60)
    for j,pts in enumerate((left,right)):
        for k in range(0,max(0,ix-5),5):
            x,y=pts[k];d.ellipse((x-2,y-5,x+2,y+5),fill=p['muted'])
        x,y=pts[ix];person(d,x,y,p,p['accent'] if j==0 else p['blue'],u*6,1,rose_=j==0)
    for j in range(8):
        x=40+(j*151)%460;y=90+(j*173)%680
        if abs(x-270)>90:line(d,[(x,y),(x+4,y-12),(x+9,y-4)],p['green'],2)

def heart(im,u,p,phase):
    d=ImageDraw.Draw(im)
    pulse=1+.012*math.sin(u*math.tau*1.1)
    pts=[]
    for i in range(161):
        t=i/160*math.tau
        x=16*math.sin(t)**3;y=13*math.cos(t)-5*math.cos(2*t)-2*math.cos(3*t)-math.cos(4*t)
        pts.append((270+x*10*pulse,468-y*10*pulse))
    d.polygon(pts,fill='#f0d7d1');line(d,pts,p['ink'],3)
    for j in range(5):
        progress=max(0,min(1,phase*1.5-j*.12))
        cr=curve([(180,480+j*10),(200+j*16,310),(330-j*8,650),(365,420+j*10)])
        count=max(2,int(progress*60))
        line(d,cr[:count], [p['accent'],p['blue'],p['green']][j%3],2)
        if progress: x,y=cr[count-1];ellipse(d,(x-4,y-4,x+4,y+4),p['accent'])
    rose(d,270,480,20,p)
    scars(d,p.get('_scar_base',0),p)
    base=730
    wave=[]
    for x in range(72,469,3):
        z=((x-72)/396*3-u*.7)%1
        dy= -30*math.exp(-((z-.45)/.025)**2)+16*math.exp(-((z-.5)/.035)**2)
        wave.append((x,base+dy))
    line(d,wave,p['accent'],2)

DRAWERS={'gift':gift,'bloom':bloom,'crowd':crowd,'paths':paths,'heart':heart}

def state(plan,index,frame):
    s=plan['scenes'][index];p=dict(PALETTES[plan['palette']])
    p['_scar_base']=min(8,4*sum(x['kind']=='wounded_heart' for x in plan['scenes'][:index]))
    im=paper(p);a,b=s['start_frame'],s['end_frame']
    u=(frame-a)/plan['fps'];cue=s['cue_frame']
    # The main action lands at the actual selected cue; easing before/after is continuous.
    if frame<=cue:phase=.64*(frame-a)/max(1,cue-a)
    else:phase=.64+.36*(frame-cue)/max(1,b-1-cue)
    DRAWERS[s['kind']](im,u,p,max(0,min(1,phase)))
    return im

def render_frame(plan,frame):
    index=next(i for i,s in enumerate(plan['scenes']) if s['start_frame']<=frame<s['end_frame'])
    s=plan['scenes'][index];im=state(plan,index,frame)
    if index+1<len(plan['scenes']) and s['kind']=='bloom':
        # Reveal the actual next scene through the flower centre, not a black filler.
        n=max(1,round(.45*plan['fps']));start=s['end_frame']-n
        if frame>=start:
            q=ease((frame-start)/max(1,n-1));rr=q*1100
            nxt=state(plan,index+1,s['end_frame'])
            mask=Image.new('L',(W,H));ImageDraw.Draw(mask).ellipse((270-rr,468-rr,270+rr,468+rr),fill=255)
            im=Image.composite(nxt,im,mask)
    return im

def thorn(im,u,p,phase):
    d=ImageDraw.Draw(im)
    palm(d,270,592,p,grip=ease((phase-.35)/.35))
    press=ease(phase/.64)
    flower(d,270,lerp(415,475,press),2.0,p)
    # An explicit thorn on the persistent stem reaches the palm.
    tipy=lerp(415,475,press)+102
    d.polygon([(270,tipy),(288,tipy-9),(273,tipy-18)],fill=p['green'],outline=p['ink'])
    injury=ease((phase-.64)/.25)
    if injury:
        x,y=289,tipy-8
        r=3+injury*4
        ellipse(d,(x-r,y-r,x+r,y+r),p['accent'])
        yy=y+injury*38
        d.polygon([(x,yy-9),(x-5,yy),(x+5,yy)],fill=p['accent'])
        ellipse(d,(x-5,yy-3,x+5,yy+7),p['accent'])
        for k in range(3):
            a=-.8+k*.6
            line(d,[(x+22*math.cos(a),y+22*math.sin(a)),(x+34*math.cos(a),y+34*math.sin(a))],p['accent'],2)

def scars(d,count,p):
    positions=[(205,425),(288,393),(320,490),(245,530),(185,460),(313,433),(273,570),(225,400)]
    for j,(xx,yy) in enumerate(positions):
        q=max(0,min(1,count-j))
        if q<=0:continue
        x2=xx+34*q;y2=yy+24*q
        line(d,[(xx,yy),(x2,y2)],p['accent'],3)
        for k in range(1,int(q*5)+1):
            a=xx+k*6;b=yy+k*4
            line(d,[(a-3,b+5),(a+3,b-5)],p['ink'],1)

def wounded_heart(im,u,p,phase):
    heart(im,u,p,phase)
    d=ImageDraw.Draw(im)
    scars(d,min(8,p.get('_scar_base',0)+4*ease(phase)),p)


def thorns(im,u,p,phase):
    d=ImageDraw.Draw(im)
    for j in range(6):
        yy=150+j*122;xx=60+(j%2)*175
        pts=[(xx,yy),(xx+45,yy-9),(xx+90,yy+6),(xx+137,yy-7)]
        line(d,pts,p['ink'],3)
        for k in range(5):
            x=xx+15+k*24;y=yy-3
            d.polygon([(x,y),(x+3,y-18),(x+8,y)],fill=p['green'],outline=p['ink'])
    # People follow a curved safe route between the thorns.
    pts=curve([(435,870),(455,650),(425,400),(440,70)],100)
    n=int(phase*100)
    for j in range(0,max(0,n-5),6):
        x,y=pts[j];ellipse(d,(x-3,y-6,x+3,y+6),p['muted'])
    x,y=pts[n];person(d,x,y,p,p['blue'],u*7,1.3)

DRAWERS.update(thorn=thorn,wounded_heart=wounded_heart,thorns=thorns)
