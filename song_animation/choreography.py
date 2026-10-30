"""Retarget existing illustrated people onto a connected locomotion rig.
Artwork remains song-generated; this supplies body mechanics when review finds
missing footsteps, disconnected walking parts or unfulfilled pacing.
"""
import copy,hashlib,re
from xml.etree import ElementTree as ET
from .vector import raster,validate_vector,invisible_foreground_nodes

def key(t,x,y,rotation=0,scale=1,opacity=1):
    return dict(t=t,x=x,y=y,rotation=rotation,scale=scale,opacity=opacity)

def retarget(plan,index,notes):
    text=' '.join(notes).lower();scene=plan['scenes'][index]
    identity=str(plan.get('bible',{}).get('characters','')).lower()
    if not re.search(r'\b(human|poet|man|woman|person|singer|dancer|male|female)\b',identity):return plan,False
    walk=bool(re.search(r'footstep|pacing|walking|walk\b',text+' '+scene.get('action','').lower()))
    shadows='shadow' in (text+' '+scene.get('action','').lower()) and 'detach' in scene.get('action','').lower()
    if not (walk or shadows):return plan,False
    assets=copy.deepcopy(plan['assets'])
    def find(part):
        for aid,a in assets.items():
            if re.search(r'(?:^|_)'+part+r'$',aid):return aid,a
        return None,None
    torso_id,torso=find('torso');head_id,head=find('head');arm_id,arm=find('arm')
    if not torso or not head:return plan,False
    def tight(aid,a,w,h):
        out='rig_'+aid[:50]+'_'+str(w)+'_'+str(h)
        if out in assets:return out
        root=ET.fromstring(a['svg']);box=raster(a['svg'],int(a['width']),int(a['height'])).getchannel('A').getbbox()
        if not box:raise ValueError('Cannot rig empty person artwork')
        vb=[float(v) for v in re.split(r'[ ,]+',root.get('viewBox',f"0 0 {a['width']} {a['height']}").strip())]
        x,y,vw,vh=vb;l,t,r,b=box
        root.set('viewBox',f"{x+l*vw/a['width']} {y+t*vh/a['height']} {(r-l)*vw/a['width']} {(b-t)*vh/a['height']}")
        ET.register_namespace('','http://www.w3.org/2000/svg')
        assets[out]=dict(id=out,width=w,height=h,svg=ET.tostring(root,encoding='unicode'),description=a.get('description','')+' retargeted to connected body',reusable=True)
        return out
    body=tight(torso_id,torso,100,150);face=tight(head_id,head,65,85)
    def authored(aid,w,h,svg):
        assets[aid]=dict(id=aid,width=w,height=h,svg=f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}">{svg}</svg>',description='Connected locomotion rig part',reusable=True);return aid
    leg=authored('rig_neutral_trouser_leg',24,110,'<path d="M2 0H22L21 108H4Z" fill="#514538"/><path d="M7 5L9 101" stroke="#77614b" stroke-width="2"/>')
    foot=authored('rig_leather_shoe',42,17,'<path d="M3 2H22Q24 8 36 9Q42 11 40 16H2Z" fill="#392c29"/><path d="M4 13H38" stroke="#a8845b" stroke-width="2"/>')
    sleeve=tight(arm_id,arm,25,105) if arm else authored('rig_sleeved_arm',25,105,'<path d="M2 0H23L20 65H5Z" fill="#a46035"/><path d="M5 65H20V94Q20 105 12 105Q4 105 5 94Z" fill="#d9a37c"/>')
    nodes=copy.deepcopy(scene['nodes']);remove=set()
    for n in nodes:
        label=(n['id']+' '+str(n.get('asset',''))).lower()
        if n.get('role')!='background' and re.search(r'poet|hero|person|character|torso|head|arm|foot|boot|leg|shadow',label):remove.add(n['id'])
    for _ in range(len(nodes)):
        remove.update(n['id'] for n in nodes if n.get('parent') in remove)
    nodes=[n for n in nodes if n['id'] not in remove]
    if walk:
        for n in nodes:
            if 'vine_layer' in n['id']:
                side=-1 if '1' in n['id'] else 1
                for k in n['keys']:k.update(x=-120 if side<0 else 660,y=825,rotation=side*12)
    prefix='connected_'+str(index)+'_'
    def node(name,asset,keys,parent=None,pivot=(.5,.5),wave=None):
        n=dict(id=prefix+name,asset=asset,keys=keys,role='foreground',parent=prefix+parent if parent else None,pivot=list(pivot))
        if wave:n['wave']=wave
        nodes.append(n)
    if shadows:
        shade=authored('rig_detaching_silhouette',100,330,'<ellipse cx="50" cy="35" rx="23" ry="30" fill="#a18b9c"/><path d="M25 70Q50 55 75 70L95 190L77 198L67 120L71 245L81 325H57L48 251L42 325H18L28 240L31 125L20 195L4 188Z" fill="#85738b" stroke="#bea7ba" stroke-width="3"/>')
        node('shadow_left',shade,[key(0,180,550,opacity=.85),key(.5,110,520,-8,opacity=.65),key(1,35,470,-16,opacity=0)])
        node('shadow_right',shade,[key(0,360,550,opacity=.85),key(.5,430,520,8,opacity=.65),key(1,505,470,16,opacity=0)])
    pacing='pac' in text+' '+scene.get('action','').lower()
    xs=[160,380,200] if pacing else ([100,270,440] if walk else [270,270,270])
    node('root',None,[key(0,xs[0],680),key(.5,xs[1],680),key(1,xs[2],680)])
    gait=3 if walk else 0
    for side,phase,x in [('left',0,-18),('right',.5,18)]:
        node(side+'_leg',leg,[key(0,x,-55),key(1,x,-55)],parent='root',pivot=(.5,0),wave=dict(rotation=19 if walk else 0,cycles=gait,phase=phase))
        node(side+'_foot',foot,[key(0,6,105),key(1,6,105)],parent=side+'_leg')
    node('body',body,[key(0,0,-130),key(1,0,-130)],parent='root')
    for side,phase,x in [('left',.5,-44),('right',0,44)]:
        node(side+'_arm',sleeve,[key(0,x,-182),key(1,x,-182)],parent='root',pivot=(.5,0),wave=dict(rotation=14 if walk else 3,cycles=gait or 1,phase=phase))
    node('face',face,[key(0,0,-240),key(.5,0,-240,-7 if pacing else 0),key(1,0,-240)],parent='root')
    if len(nodes)>24:return plan,False
    result=copy.deepcopy(plan);result['assets']=assets;result['scenes'][index]['nodes']=nodes
    result['scenes'][index]['body_mechanics']='Retargeted source artwork to a connected articulated body with grounded alternating feet'
    validate_vector(result)
    if invisible_foreground_nodes(result,index):raise ValueError('Connected rig has invisible parts')
    return result,True
