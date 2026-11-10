"""Turn timed lyric phrases into kit shots.

Timing is decided here (deterministic); Gemini only composes each shot from the
kit vocabulary. Every model answer is validated and repaired; if the model is
unavailable, a keyword director composes the shots so a film is always made.
"""
import json,re
from .art import OBJECTS,PEOPLE,EFFECTS,SKIES,GROUNDS,WALLS

CAMERAS=('push_in','pull_out','pan_left','pan_right')

def cut_shots(words,duration,min_len=2.6,max_len=5.2):
    """Group phrases into shots of ~2.6..5.2 s that cover the whole clip."""
    cues=[w for w in words if w.get('text','').strip()]
    shots=[];cur=None
    for w in cues:
        if cur is None:cur={'start':0.0 if not shots else shots[-1]['end'],'end':w['end'],'lines':[w]}
        elif w['end']-cur['start']<=max_len or cur['end']-cur['start']<min_len:cur['end']=w['end'];cur['lines'].append(w)
        else:shots.append(cur);cur={'start':cur['end'],'end':w['end'],'lines':[w]}
    if cur:shots.append(cur)
    if not shots:  # instrumental: even shots
        n=max(1,round(duration/4));return [{'start':duration*i/n,'end':duration*(i+1)/n,'lines':[]} for i in range(n)]
    shots[-1]['end']=duration
    # split any over-long stretch (long instrumental gaps) evenly
    out=[]
    for s in shots:
        n=max(1,int((s['end']-s['start'])//(max_len+.01))+1) if s['end']-s['start']>max_len*1.25 else 1
        for i in range(n):out.append({'start':s['start']+(s['end']-s['start'])*i/n,'end':s['start']+(s['end']-s['start'])*(i+1)/n,'lines':s['lines'] if i==n-1 else []})
    return out

# ---------- keyword director (no model needed) ----------
RULES=[  # (regex on lyric text, composition pieces)
 (r'माँ|मां|माई|अम्मा|maa|mother',{'people':['mother']}),(r'पिता|बापू|बाबा|पापा|बाबूजी|father|papa',{'people':['father']}),
 (r'बचपन|बच्च|बालक|लाल|child',{'people':['child'],'objects':['kite']}),(r'दादी|दादा|बूढ़|बुज़ुर्ग',{'people':['oldman']}),
 (r'चूल्ह|रोटी|तवा|रसोई',{'setting':'indoor','objects':['chulha','matka']}),(r'कोल्हू|गन्न|गुड़',{'objects':['kolhu','sugarcane']}),
 (r'सरसों|पीले',{'ground':'mustard','sky':'golden'}),(r'खेत|फसल|किसान|हल',{'ground':'field','objects':['tractor','haystack']}),
 (r'सूरज|धूप|सवेर|सुबह',{'objects':['sun'],'sky':'dawn'}),(r'छुप|ढल|शाम|सांझ|साँझ',{'objects':['sun','pole'],'sky':'dusk','effects':['birds']}),
 (r'रात|चाँद|चांद|तारे|चंदा',{'objects':['moon'],'sky':'night','effects':['stars','fireflies']}),
 (r'बारिश|बरस|सावन|बादल|बूँद|भीग',{'sky':'rain','objects':['clouds'],'effects':['rain']}),(r'नदी|दरिया|किनार|नाव|गंगा',{'ground':'river','objects':['boat']}),
 (r'गाँव|गांव|गली|आँगन|आंगन',{'ground':'village','objects':['hut','tree']}),(r'शहर|चकाचौंध|भीड़|दिल्ली|बम्बई|मुंबई',{'ground':'city','sky':'night','objects':['citylights']}),
 (r'डिबिया|लौ|आले',{'setting':'indoor','light':'night','objects':['niche_lamp']}),(r'दीया|दिया|दीप|दिवाली|आरती',{'objects':['diyas'],'effects':['embers']}),
 (r'किवाड़|दरवाज़|दरवाज|ताल[ेा]|कुंडी|कड़ी',{'setting':'indoor','objects':['door']}),(r'खुला|खुल',{'door_open':True}),(r'जंग|बंद',{'door_locked':True}),
 (r'चरखा|दीमक',{'setting':'indoor','objects':['charkha'],'old':True}),(r'गाय|बछड़',{'objects':['cow']}),(r'बैल|गाड़ी|छकड़',{'objects':['cart']}),
 (r'रेल|ट्रेन|स्टेशन|सफ़र|सफर',{'objects':['train'],'moving':True}),(r'बस',{'objects':['bus']}),(r'फ़ोन|फोन|मोबाइल|कॉल',{'objects':['phone']}),
 (r'चिट्ठी|ख़त|खत|पाती',{'objects':['letter']}),(r'मंदिर|भगवान|राम|शिव|कृष्ण|प्रभु|माता|देवी|भोले',{'objects':['temple','diyas']}),
 (r'झूल',{'objects':['swing']}),(r'कुआँ|कुंआ|पनघट',{'objects':['well']}),(r'पेड़|नीम|पीपल|छाँव|छांव',{'objects':['tree']}),
 (r'प्यार|प्रेम|दिल|इश्क|सनम|साथ|हम तुम|तुम हम',{'people':['couple'],'objects':['flowers'],'effects':['petals']}),
 (r'याद|पुरान|बीत',{'objects':['photo'],'setting':'indoor'}),(r'घड़ी|वक़्त|वक्त|समय|पल',{'objects':['clock']}),(r'खिड़की',{'objects':['window']}),
 (r'साइकिल',{'objects':['cycle']}),(r'ट्रैक्टर',{'objects':['tractor']}),(r'मटका|पानी|घड़ा',{'objects':['matka']}),(r'पतंग',{'objects':['kite']}),
 (r'रेडियो|गाना|गीत',{'objects':['radio']}),(r'सड़क|राह|रास्त|बाट',{'ground':'road'}),(r'पहाड़|पर्बत|पर्वत',{'ground':'hills'}),
 (r'रेत|रेगिस्तान|थार',{'ground':'desert'}),(r'फूल|बाग|बगिया|कली',{'objects':['flowers'],'effects':['petals']}),
]
DEFAULTS=[  # used for lines with no keyword, cycling for variety
 {'ground':'village','sky':'golden','objects':['hut','tree'],'effects':['birds']},{'ground':'field','sky':'day','objects':['tree','cart'],'effects':['leaves']},
 {'setting':'indoor','objects':['window','charpai']},{'ground':'road','sky':'dusk','objects':['pole','tree'],'effects':['birds']},
 {'ground':'river','sky':'dawn','objects':['boat','palm']},{'setting':'indoor','light':'night','objects':['lantern','trunk'],'effects':['dust']},
]
INDOOR_ONLY={'chulha','niche_lamp','door','charkha','photo','clock','window','trunk','candle','radio','charpai','matka','lantern'}
SKY_ONLY={'sun','moon','clouds','kite','citylights'}

DEV='\u0900-\u097F'
WHOLE={'बस','पल','दिल','राम','लाल','हल','साथ','माता','याद'}  # short words that are also parts of other words
def _compile(rx):
    alts=[]
    for a in rx.split('|'):
        alts.append(f'(?<![{DEV}]){a}(?![{DEV}])' if a in WHOLE else f'(?<![{DEV}]){a}')
    return re.compile('|'.join(alts),re.I)
COMPILED=[(_compile(rx),add) for rx,add in RULES]
MINOR={'pole','haystack','bush','flowers','matka','streetlamp','diyas','candle','trunk','charpai','cart','tractor'}

def keyword_compose(text,index,prev_key=None):
    pieces={};hits=0
    for rx,add in COMPILED:
        if rx.search(text or ''):
            hits+=1
            for k,v in add.items():
                if isinstance(v,list):pieces[k]=pieces.get(k,[])+[x for x in v if x not in pieces.get(k,[])]
                else:pieces[k]=v
    if not hits:pieces=dict(DEFAULTS[index%len(DEFAULTS)])
    setting=pieces.get('setting','outdoor')
    if setting=='outdoor' and pieces.get('objects') and all(o in INDOOR_ONLY for o in pieces['objects']) and not any(k in pieces for k in('ground','sky')):setting='indoor'
    night=pieces.get('sky') in('night','rain') or pieces.get('light')=='night'
    shot={'setting':setting,'sky':pieces.get('sky','golden' if index%2 else 'day'),'ground':pieces.get('ground','field'),
          'wall':'mud','light':pieces.get('light','night' if night else 'day'),'effects':pieces.get('effects',[]),'camera':CAMERAS[index%4],'objects':[]}
    objs=[o for o in pieces.get('objects',[]) if o in OBJECTS][:4]
    if setting=='indoor':objs=[o for o in objs if o not in SKY_ONLY] or ['lantern']
    params={}
    if pieces.get('door_open'):params['door']={'open':True}
    elif pieces.get('door_locked'):params['door']={'locked':True}
    if pieces.get('old'):params['charkha']={'old':True}
    if pieces.get('moving'):params['train']={'moving':True}
    # layout: one clear main subject, at most two supporting objects, people beside (not on) the subject
    sky_y={'dusk':.5,'dawn':.46}.get(shot['sky'],.26);ground=[];side=[(.2,.7),(.8,.7)]
    for o in objs:
        pl=OBJECTS[o][1]
        if o=='sugarcane':
            for x in(.1,.9):shot['objects'].append({'name':o,'x':x,'y':.97,'scale':1.0,'params':{}})
        elif pl=='sky':shot['objects'].append({'name':o,'x':.5 if o=='citylights' else .66,'y':sky_y,'scale':1.0,'params':params.get(o,{})})
        else:ground.append(o)
    ground=sorted(ground,key=lambda o:o in MINOR)  # a real subject leads; small props support
    for k,o in enumerate(ground[:3]):
        pl=OBJECTS[o][1]
        if k==0:x,y,sc=.5,(.8 if setting=='indoor' else .8),(1.15 if len(ground)==1 else 1.0)
        else:x,y=side[k%2];sc=.55;y=.62 if pl=='wall' and setting=='indoor' else (.8 if setting=='indoor' else y)
        if pl=='wall' and setting=='indoor' and k==0:y=.62
        shot['objects'].append({'name':o,'x':x,'y':y,'scale':sc,'params':params.get(o,{})})
    for k,pp in enumerate(pieces.get('people',[])[:2]):
        if pp in PEOPLE:
            near_stove='chulha' in ground
            shot['objects'].append({'name':pp,'x':(.2 if k==0 else .8) if ground else .5,'y':.8 if setting=='indoor' else .77,'scale':1.1,
                'pose':'sit' if (near_stove and pp=='mother') else ('walk' if pp=='child' else 'stand')})
    return normalize(shot,index)

def normalize(shot,index):
    """Clamp a composition to safe values: vocabulary, placement bands, scale, count, draw order."""
    s={'setting':'indoor' if shot.get('setting')=='indoor' else 'outdoor','sky':shot.get('sky') if shot.get('sky') in SKIES else 'golden',
       'ground':shot.get('ground') if shot.get('ground') in GROUNDS else 'field','wall':shot.get('wall') if shot.get('wall') in WALLS else 'mud',
       'light':'night' if shot.get('light')=='night' else 'day','camera':shot.get('camera') if shot.get('camera') in CAMERAS else CAMERAS[index%4],
       'effects':[e for e in (shot.get('effects') or []) if e in EFFECTS][:2],'objects':[]}
    night=(s['setting']=='outdoor' and s['sky'] in('night','rain')) or (s['setting']=='indoor' and s['light']=='night')
    for o in (shot.get('objects') or [])[:7]:
        if not isinstance(o,dict):continue
        name=o.get('name')
        if name not in OBJECTS and name not in PEOPLE:continue
        if s['setting']=='indoor' and name in SKY_ONLY:continue
        pl='person' if name in PEOPLE else OBJECTS[name][1]
        x=float(o.get('x',.5)) if isinstance(o.get('x'),(int,float)) else .5;y=float(o.get('y',.8)) if isinstance(o.get('y'),(int,float)) else .8
        sc=float(o.get('scale',1)) if isinstance(o.get('scale'),(int,float)) else 1.0
        floor=.76 if s['setting']=='indoor' else .62
        if pl=='sky':y=min(.45,max(.12,y))
        elif pl=='wall':y=min(.68,max(.42,y)) if s['setting']=='indoor' else min(.9,max(floor+.05,y))
        else:y=min(.93,max(floor,y))
        x=min(.88,max(.12,x));sc=min(1.5,max(.35,sc))
        if pl=='hero':y=min(.82,max(.6,y))
        params=o.get('params') if isinstance(o.get('params'),dict) else {}
        params={k:v for k,v in params.items() if k in('open','locked','old','moving','rain','sky','color','scroll','web') and isinstance(v,(bool,str))}
        s['objects'].append({'name':name,'x':x,'y':y,'scale':sc,'pose':o.get('pose') if o.get('pose') in('stand','sit','walk') else 'stand','params':params,'_pl':pl})
    if not [o for o in s['objects'] if o['_pl']!='sky']:  # never an empty frame
        s['objects'].append({'name':'tree' if s['setting']=='outdoor' else 'lantern','x':.5,'y':.8,'scale':1.0,'pose':'stand','params':{},'_pl':'ground'})
    s['objects'].sort(key=lambda o:(o['_pl']!='sky',o['_pl']!='wall',o['y']))
    s['night']=night
    return s

# ---------- Gemini director ----------
SHOT_SCHEMA={'type':'OBJECT','properties':{'shots':{'type':'ARRAY','items':{'type':'OBJECT','properties':{
    'index':{'type':'INTEGER'},'setting':{'type':'STRING'},'sky':{'type':'STRING'},'ground':{'type':'STRING'},'wall':{'type':'STRING'},'light':{'type':'STRING'},
    'camera':{'type':'STRING'},'effects':{'type':'ARRAY','items':{'type':'STRING'}},
    'objects':{'type':'ARRAY','items':{'type':'OBJECT','properties':{'name':{'type':'STRING'},'x':{'type':'NUMBER'},'y':{'type':'NUMBER'},'scale':{'type':'NUMBER'},'pose':{'type':'STRING'},
        'params':{'type':'OBJECT','properties':{'open':{'type':'BOOLEAN'},'locked':{'type':'BOOLEAN'},'old':{'type':'BOOLEAN'},'moving':{'type':'BOOLEAN'},'rain':{'type':'BOOLEAN'},'sky':{'type':'STRING'}}}},
        'required':['name','x','y','scale']}}},'required':['index','setting','objects']}}},'required':['shots']}

def prompt(shots,meta):
    vocab='\n'.join(f'- {k}: {v[2]} [{v[1]}]' for k,v in OBJECTS.items())
    lines='\n'.join(f'{i}. {s["start"]:.1f}-{s["end"]:.1f}s: '+(' / '.join(w['text'] for w in s['lines']) or '(instrumental)') for i,s in enumerate(shots))
    return f'''You are the art director of a 30-second vertical (9:16) music reel drawn in a flat, warm, paper-grain illustration style.
Song mood: {meta.get("mood","")}. Summary: {meta.get("summary","")}. Language: {meta.get("language","")}.
For EACH shot below, compose ONE scene that shows what that lyric line literally talks about, using ONLY this vocabulary.

Objects (name: what it is [placement]):
{vocab}
People (flat silhouettes seen from behind/side, no faces): {", ".join(PEOPLE)} (pose: stand|sit|walk)
Outdoor: sky one of {list(SKIES)}; ground one of {list(GROUNDS)}.
Indoor: wall one of {list(WALLS)}; light day|night.
Effects (0-2): {list(EFFECTS)}. Camera: {list(CAMERAS)}.

Layout: x,y are fractions of the frame; (x,y) is the BOTTOM-CENTRE of an object. Outdoor horizon is y=0.58 so ground objects use y 0.62-0.93
(lower = closer = larger scale); sky objects y 0.12-0.45. Indoor floor starts at y=0.76; wall objects y 0.42-0.68. Scale 0.35-1.5, about 1 for the main subject.
Keep the bottom 12% visually calm (captions go there). Use 2-5 objects per shot; one clear main subject near the centre.
Make consecutive shots clearly different (setting, sky or main object), keep one continuous emotional journey, and never invent things the lyric does not suggest.
Params: door {{"open":true}} or {{"locked":true}}; charkha {{"old":true}}; train/cycle/tractor {{"moving":true}}; window {{"sky":"night","rain":true}}.

Shots:
{lines}

Return JSON {{"shots":[{{"index":0,"setting":"outdoor|indoor",...,"objects":[{{"name":..,"x":..,"y":..,"scale":..}}]}}...]}} with one entry per shot index.'''

def direct(words,duration,meta,out=None,use_model=True):
    shots=cut_shots(words,duration)
    composed=None;source='keywords'
    if use_model:
        try:
            from ..provider import generate_json
            reply=generate_json(prompt(shots,meta),out=out,tag='kit_director',schema=SHOT_SCHEMA,max_tokens=16384,timeout_seconds=120)
            composed={int(s.get('index',-1)):s for s in reply.get('shots',[]) if isinstance(s,dict)};source='gemini'
        except Exception as error:  # quota, outage, bad JSON: the keyword director still makes a film
            print('Director model unavailable, using keyword director:',str(error)[:300],flush=True)
    result=[];prev=None
    for i,s in enumerate(shots):
        text=' '.join(w['text'] for w in s['lines'])
        if composed and i in composed and composed[i].get('objects'):shot=normalize(composed[i],i);shot['source']='gemini'
        elif not text.strip() and result:  # instrumental bridge: stay in the previous world, new camera + gentle particles
            shot={k:v for k,v in result[-1].items() if k not in('start','end','text','lines')};shot['camera']=CAMERAS[(CAMERAS.index(shot['camera'])+2)%4]
            shot['effects']=(shot['effects'] or ['dust' if shot['setting']=='indoor' else 'leaves'])[:2];shot['source']='bridge'
        else:shot=keyword_compose(text,i);shot['source']='keywords'
        key=(shot['setting'],shot['sky'] if shot['setting']=='outdoor' else shot['wall'],tuple(o['name'] for o in shot['objects'][:2]))
        if key==prev:shot['camera']=CAMERAS[(CAMERAS.index(shot['camera'])+1)%4]
        prev=key;shot.update(start=s['start'],end=s['end'],text=text,lines=[{'start':w['start'],'end':w['end'],'text':w['text']} for w in s['lines']])
        result.append(shot)
    return {'source':source,'shots':result}
