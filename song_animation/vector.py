"""Open-vocabulary vector assets + hierarchical keyframe animation.
The artwork is data (sanitized SVG), never executable generated Python/JS.
"""
import io,json,math,re,hashlib
from functools import lru_cache
from xml.etree import ElementTree as ET
import numpy as np
from PIL import Image
W,H=540,960
TAGS={'svg','g','path','rect','circle','ellipse','line','polyline','polygon','defs','linearGradient','radialGradient','stop','clipPath'}
ATTRS={'id','xmlns','viewBox','width','height','x','y','x1','y1','x2','y2','cx','cy','r','rx','ry','d','points','fill','fill-opacity','fill-rule','stroke','stroke-width','stroke-opacity','stroke-linecap','stroke-linejoin','stroke-dasharray','opacity','transform','offset','stop-color','stop-opacity','gradientUnits','gradientTransform','clip-path','clip-rule','preserveAspectRatio','fx','fy','spreadMethod','stroke-miterlimit','vector-effect','paint-order','color'}

def sanitize_svg(svg):
    if not isinstance(svg,str) or not 30<=len(svg)<=40000:raise ValueError('SVG size outside supported bounds')
    if re.search(r'<!|<\?|\b(?:https?|file|data|javascript):|@import',svg.replace('http://www.w3.org/2000/svg',''),re.I):raise ValueError('External or executable SVG content rejected')
    try:root=ET.fromstring(svg)
    except ET.ParseError as e:raise ValueError('Malformed SVG XML: '+str(e)) from None
    if root.tag.split('}')[-1]!='svg':raise ValueError('Asset must be SVG')
    if len(list(root.iter()))>600:raise ValueError('SVG too complex')
    shapes=0
    for el in root.iter():
        tag=el.tag.split('}')[-1]
        if tag not in TAGS:raise ValueError('Unsupported SVG element: '+tag)
        if tag in {'path','rect','circle','ellipse','line','polyline','polygon'}:shapes+=1
        for k,v in el.attrib.items():
            name=k.split('}')[-1]
            if name not in ATTRS or name.lower().startswith('on'):raise ValueError('Unsafe/unsupported SVG attribute: '+name)
            if 'url(' in v and not re.fullmatch(r'url\(#[A-Za-z0-9_-]+\)',v):raise ValueError('External SVG reference rejected')
    if shapes<1:raise ValueError('Empty SVG asset')
    return svg

def finite(x,lo,hi):return type(x) in (float,int) and math.isfinite(x) and lo<=x<=hi

def validate_vector(plan):
    fps=plan.get('fps');total=plan.get('total_frames')
    if type(fps) is not int or not 12<=fps<=30 or type(total) is not int or not fps<=total<=30*fps:raise ValueError('Vector films must be 1..30 seconds')
    assets=plan.get('assets',{});scenes=plan.get('scenes',[])
    if not 1<=len(assets)<=180 or not 1<=len(scenes)<=12:raise ValueError('Asset/scene budget exceeded')
    for key,a in assets.items():
        if not re.fullmatch(r'[A-Za-z0-9_-]{1,80}',key):raise ValueError('Invalid asset id')
        if not finite(a.get('width'),4,1080) or not finite(a.get('height'),4,1920):raise ValueError('Invalid asset raster dimensions')
        sanitize_svg(a.get('svg'))
    cursor=0
    for s in scenes:
        if s.get('kind')!='vector' or s.get('start_frame')!=cursor or type(s.get('end_frame')) is not int or not cursor<s['end_frame']<=total:raise ValueError('Invalid vector shot timeline')
        if not isinstance(s.get('label'),str) or not s['label'].strip():raise ValueError('Missing shot meaning')
        if not re.fullmatch(r'#[0-9a-fA-F]{6}',s.get('background','')):raise ValueError('Invalid background color')
        nodes=s.get('nodes',[])
        if not 2<=len(nodes)<=24:raise ValueError('Need 2..24 scene layers')
        ids=set();moves=[]
        for node in nodes:
            nid=node.get('id')
            if not isinstance(nid,str) or nid in ids:raise ValueError('Duplicate/missing node id')
            if node.get('parent') and node['parent'] not in ids:raise ValueError('Parent must precede child (no cycles)')
            ids.add(nid)
            if node.get('asset') and node['asset'] not in assets:raise ValueError('Missing custom asset')
            if not node.get('asset') and not any(x.get('parent')==nid for x in nodes):raise ValueError('Empty group')
            pivot=node.get('pivot',[.5,.5])
            if not isinstance(pivot,list) or len(pivot)!=2 or not all(finite(v,0,1) for v in pivot):raise ValueError('Invalid pivot')
            keys=node.get('keys',[])
            if not 2<=len(keys)<=10 or keys[0].get('t')!=0 or keys[-1].get('t')!=1:raise ValueError('Keyframes must cover 0..1')
            prev=-1
            for k in keys:
                if not finite(k.get('t'),0,1) or k['t']<=prev:raise ValueError('Unordered keyframes')
                prev=k['t']
                for name,lo,hi,default in [('x',-1080,1620,0),('y',-1920,2880,0),('rotation',-720,720,0),('scale',.05,4,1),('opacity',0,1,1)]:
                    if not finite(k.get(name,default),lo,hi):raise ValueError('Invalid transform '+name)
            wave=node.get('wave',{})
            for k,lo,hi in [('x',-80,80),('y',-80,80),('rotation',-50,50),('cycles',0,20),('phase',-10,10)]:
                if k in wave and not finite(wave[k],lo,hi):raise ValueError('Invalid motion wave')
            signature=json.dumps([[(k['t'],round(k.get('x',0)-keys[0].get('x',0),4),round(k.get('y',0)-keys[0].get('y',0),4),round(k.get('rotation',0)-keys[0].get('rotation',0),4),round(k.get('scale',1)/keys[0].get('scale',1),4)) for k in keys],wave],sort_keys=True)
            meaningful=any(any(abs(k.get(name,default)-keys[0].get(name,default))>threshold for name,default,threshold in [('x',0,3),('y',0,3),('rotation',0,3),('scale',1,.04)]) for k in keys[1:]) or any(abs(wave.get(k,0))>v for k,v in [('x',3),('y',3),('rotation',3)])
            if node.get('asset') and node.get('role','foreground')!='background' and meaningful:moves.append(signature)
        if len(set(moves))<2:raise ValueError('Need at least two independent foreground motions; camera motion does not count')
        cursor=s['end_frame']
    if cursor!=total:raise ValueError('Missing vector film ending')
    return plan

@lru_cache(maxsize=192)
def raster(svg,width,height):
    import cairosvg
    sanitize_svg(svg)
    raw=cairosvg.svg2png(bytestring=svg.encode(),output_width=int(width),output_height=int(height))
    return Image.open(io.BytesIO(raw)).convert('RGBA')

def values(node,t):
    keys=node['keys'];a,b=keys[-2],keys[-1]
    for i,k in enumerate(keys[1:]):
        if t<=k['t']:a,b=keys[i],k;break
    q=max(0,min(1,(t-a['t'])/(b['t']-a['t'])))
    if node.get('easing','smooth')!='linear':q=q*q*(3-2*q)
    v={n:a.get(n,d)+(b.get(n,d)-a.get(n,d))*q for n,d in [('x',0),('y',0),('rotation',0),('scale',1),('opacity',1)]}
    wave=node.get('wave',{});w=math.sin(math.tau*(t*wave.get('cycles',1)+wave.get('phase',0)))
    for n in ('x','y','rotation'):v[n]+=wave.get(n,0)*w
    return v

def basis(v):
    a=math.radians(v['rotation']);c=math.cos(a)*v['scale'];s=math.sin(a)*v['scale']
    return np.array([[c,-s,v['x']],[s,c,v['y']],[0,0,1.]])

def paste(im,asset,M,opacity,pivot):
    layer=raster(asset['svg'],int(asset['width']),int(asset['height']));w,h=layer.size
    T=M@np.array([[1,0,-pivot[0]*w],[0,1,-pivot[1]*h],[0,0,1.]])
    corners=T@np.array([[0,w,w,0],[0,0,h,h],[1,1,1,1]])
    left=max(0,math.floor(corners[0].min()));right=min(W,math.ceil(corners[0].max()))
    top=max(0,math.floor(corners[1].min()));bottom=min(H,math.ceil(corners[1].max()))
    if left>=right or top>=bottom or opacity<=0:return
    inv=np.linalg.inv(T);offset=inv@np.array([left,top,1])
    coeff=(inv[0,0],inv[0,1],offset[0],inv[1,0],inv[1,1],offset[1])
    tile=layer.transform((right-left,bottom-top),Image.Transform.AFFINE,coeff,resample=Image.Resampling.BICUBIC)
    if opacity<.999:tile.putalpha(tile.getchannel('A').point(lambda x:int(x*opacity)))
    im.alpha_composite(tile,(left,top))

def render_vector(plan,index,frame):
    scene=plan['scenes'][index];t=(frame-scene['start_frame'])/max(1,scene['end_frame']-scene['start_frame']-1)
    im=Image.new('RGBA',(W,H),scene['background']);matrices={};alphas={}
    for node in scene['nodes']:
        v=values(node,t);M=basis(v);opacity=v['opacity']
        if node.get('parent'):M=matrices[node['parent']]@M;opacity*=alphas[node['parent']]
        matrices[node['id']]=M;alphas[node['id']]=opacity
        if node.get('asset'):paste(im,plan['assets'][node['asset']],M,opacity,node.get('pivot',[.5,.5]))
    return im.convert('RGB')


def invisible_foreground_nodes(plan,index=0):
    """Find non-transparent foreground layers that never reach the canvas.
    Catches canvas coordinates accidentally applied again through a parent.
    Intentional entrances/exits are accepted when visible at any sampled time.
    """
    scene=plan['scenes'][index];seen=set();active=set()
    for t in (0,.1,.25,.5,.75,.9,1):
        matrices={};alphas={}
        for node in scene['nodes']:
            v=values(node,t);M=basis(v);alpha=v['opacity']
            if node.get('parent'):M=matrices[node['parent']]@M;alpha*=alphas[node['parent']]
            matrices[node['id']]=M;alphas[node['id']]=alpha
            if not node.get('asset') or node.get('role')=='background' or alpha<.2:continue
            active.add(node['id']);a=plan['assets'][node['asset']];w,h=a['width'],a['height'];px,py=node.get('pivot',[.5,.5])
            corners=M@np.array([[-px*w,(1-px)*w,(1-px)*w,-px*w],[-py*h,-py*h,(1-py)*h,(1-py)*h],[1,1,1,1]])
            left,right=corners[0].min(),corners[0].max();top,bottom=corners[1].min(),corners[1].max()
            overlap=max(0,min(W,right)-max(0,left))*max(0,min(H,bottom)-max(0,top))
            if overlap>=max(4,(right-left)*(bottom-top)*.03):seen.add(node['id'])
    return sorted(active-seen)
