"""Timed Hindi phrase captions with real Devanagari shaping.
No fabricated word-level karaoke. The supplied phrase interval controls visibility.
"""
import os,re,subprocess
from pathlib import Path
from functools import lru_cache
from PIL import Image,ImageDraw,ImageFont,features

@lru_cache(maxsize=16)
def font(size,text="दिल"):
    if not features.check_feature('raqm'):raise RuntimeError('Hindi captions require Pillow with RAQM shaping')
    base='/usr/share/fonts/truetype/noto/'
    scripts=[(r'[\u0900-\u097f]','NotoSansDevanagari-Bold.ttf'),(r'[\u0a00-\u0a7f]','NotoSansGurmukhi-Bold.ttf'),
        (r'[\u0980-\u09ff]','NotoSansBengali-Bold.ttf'),(r'[\u0a80-\u0aff]','NotoSansGujarati-Bold.ttf'),
        (r'[\u0b80-\u0bff]','NotoSansTamil-Bold.ttf'),(r'[\u0c00-\u0c7f]','NotoSansTelugu-Bold.ttf'),
        (r'[\u0c80-\u0cff]','NotoSansKannada-Bold.ttf'),(r'[\u0d00-\u0d7f]','NotoSansMalayalam-Bold.ttf'),
        (r'[\u0600-\u06ff]','NotoNaskhArabic-Bold.ttf'),(r'[\u0e00-\u0e7f]','NotoSansThai-Bold.ttf')]
    chosen=next((name for pattern,name in scripts if re.search(pattern,text)), 'NotoSans-Bold.ttf')
    paths=[base+chosen]
    if re.search(r'[\u0900-\u097f]',text):paths.insert(0,os.getenv('SONG_LYRICS_FONT',''))
    if re.search(r'[\u3040-\u30ff\u3400-\u9fff\uac00-\ud7af]',text):paths.insert(0,'/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc')
    if chosen=='NotoSans-Bold.ttf':
        if any(ord(c)>0x500 for c in text):
            try:
                charset=' '.join(format(ord(c),'x') for c in set(text) if not c.isspace())
                found=subprocess.check_output(['fc-match','-f','%{file}',':style=Bold:charset='+charset],text=True,timeout=3).strip()
                if found:paths.insert(0,found)
            except (OSError,subprocess.SubprocessError):pass
        paths.append('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf')
    for p in paths:
        if p and Path(p).is_file():return ImageFont.truetype(p,size,layout_engine=ImageFont.Layout.RAQM)
    raise RuntimeError('Install fonts-noto-core or set SONG_LYRICS_FONT to a Devanagari font')

def cues_from_lyrics(lyrics,fps):
    units=lyrics['words'];groups=[]
    if lyrics.get('timing_granularity')=='phrase':groups=[[x] for x in units]
    else:
        current=[]
        for w in units:
            fits=True
            if current:
                try:layout(' '.join(x['text'] for x in current+[w]))
                except ValueError:fits=False
            if current and (not fits or w['start']-current[-1]['end']>.35 or len(current)>=6 or re.search(r'[।!?]$',current[-1]['text'])):
                groups.append(current);current=[]
            current.append(w)
        if current:groups.append(current)
    return [{'start_frame':round(g[0]['start']*fps),'end_frame':round(g[-1]['end']*fps),
        'text':' '.join(x['text'] for x in g),'timing':'phrase'} for g in groups]

def preflight(lyrics,fps=24):
    """Check readability before paying for story/art; never invent word times."""
    report=[]
    for cue in cues_from_lyrics(lyrics,fps):
        size,lines=layout(cue['text'])
        report.append({'text':cue['text'],'font_size':size,'lines':list(lines)})
    return report

@lru_cache(maxsize=256)
def layout(text):
    probe=ImageDraw.Draw(Image.new('RGB',(1,1)))
    for size in range(31,21,-1):
        f=font(size,text);lines=[];line=''
        cjk=bool(re.search(r'[\u3040-\u30ff\u3400-\u9fff\uac00-\ud7af]',text))
        for word in (list(text) if cjk else text.split()):
            candidate=(line+('' if cjk else ' ')+word).strip()
            if line and probe.textlength(candidate,font=f,language='hi')>448:
                lines.append(line);line=word
            else:line=candidate
        if line:lines.append(line)
        if len(lines)<=2 and all(probe.textlength(x,font=f,language='hi')<=448 for x in lines):return size,tuple(lines)
    raise ValueError('Lyric phrase too long for two readable lines; split at actual phrase timing')

def overlay(im,plan,frame):
    cue=next((c for c in plan.get('lyrics',[]) if c['start_frame']<=frame<c['end_frame']),None)
    if not cue:return im
    size,lines=layout(cue['text']);f=font(size,cue['text'])
    height=28+len(lines)*(size+10);top=842-height
    canvas=Image.new('RGBA',im.size);d=ImageDraw.Draw(canvas)
    fps=plan['fps'];age=(frame-cue['start_frame'])/fps
    opacity=min(1,age/.16+.15);lift=round(7*(1-min(1,age/.2)))
    top+=lift
    d.rounded_rectangle((23,top+4,517,top+height+4),radius=19,fill=(40,45,60,22))
    d.rounded_rectangle((22,top,518,top+height),radius=19,fill=(255,250,240,242),outline=(216,205,190,255),width=1)
    d.rounded_rectangle((247,top+8,293,top+11),radius=2,fill='#be5267')
    key=re.compile(r'दिल|फूल|गुलाब|कांट|काँट|जख्म|ज़ख्म|दोस्त|अपने|दूर')
    y=top+19
    for line in lines:
        x=(540-d.textlength(line,font=f,language='hi'))/2
        d.text((x,y),line,font=f,fill='#313e51',language='hi',stroke_width=0)
        for m in re.finditer(r'\S+',line):
            if key.search(m.group()):
                dx=d.textlength(line[:m.start()],font=f,language='hi')
                d.text((x+dx,y),m.group(),font=f,fill='#b8425e',language='hi')
        y+=size+10
    canvas.putalpha(canvas.getchannel('A').point(lambda a:int(a*opacity)))
    return Image.alpha_composite(im.convert('RGBA'),canvas).convert('RGB')

def export_srt(plan,path):
    def stamp(frame):
        ms=round(frame/plan['fps']*1000);h,ms=divmod(ms,3600000);m,ms=divmod(ms,60000);s,ms=divmod(ms,1000)
        return f'{h:02}:{m:02}:{s:02},{ms:03}'
    cues=plan.get('lyrics',[])
    Path(path).write_text('\n\n'.join(f"{i+1}\n{stamp(c['start_frame'])} --> {stamp(c['end_frame'])}\n{c['text']}" for i,c in enumerate(cues))+'\n',encoding='utf-8')


def shot_phrases(plan,shot):
    """Actual sung phrases overlapping this shot, independent of planner labels."""
    return [c['text'] for c in plan.get('lyrics',[]) if c['end_frame']>shot['start_frame'] and c['start_frame']<shot['end_frame']]
