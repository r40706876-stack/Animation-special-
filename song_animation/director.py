"""Bounded scene planner; no AI-written code is executed."""
import json,math,os,time
from pathlib import Path
from .contract import ACTIONS,validate,validate_lyrics
ROOT=Path(__file__).resolve().parents[1]

def make_plan(lyrics,music,fps=24,out=None):
    import requests
    validate_lyrics(lyrics['words'],lyrics['duration'])
    prompt='''Direct a connected illustrated music film. Hindi transcript below is imperfect ASR, not authoritative lyrics.
Understand the whole segment's emotional progression. Use only supported actions when their visible action fits the meaning. No invented unsupported assets/actions. If incompatible, return {"unsupported_reason":"reason"}.
Same rose recurs: gift transfers it, bloom opens it, crowd has a central rose owner, paths separates two people, heart holds a memory rose. Thorn visibly pricks a palm, thorns shows avoiding branches, wounded_heart shows scars. For pain/betrayal lyrics choose these supported injury metaphors, not cheerful romantic gifts. This is a LIMITED visual vocabulary. Do not force rose romance onto incompatible devotional, comic, political or unrelated lyrics.
Return JSON: {"title":"short Hindi title","intent":"Hindi emotional arc","palette":"warm|hope|memory","scenes":[{"kind":"supported kind","start_word_id":0,"cue_word_id":3,"lyric_ids":[0,1,2,3],"reason":"Hindi meaning and actual visible action"}]}.
Use 3..10 readable shots where possible, >=1 second each and no more than 8 seconds per shot. First starts at word 0, increasing start_word_id. Cover every word exactly once in contiguous lyric_ids ranges. Cue belongs to its shot; choose meaningful word for action. Group phrases rather than single words. Do not correct uncertain words. Code derives timestamps and covers instrumental gaps. No banners.
Timing granularity may be phrase-level; then each supplied id is a whole timed phrase, not a word. Do not invent within-phrase word timestamps. Use each original id exactly once.
SUPPORTED: '''+json.dumps(ACTIONS)+'\nLYRICS: '+json.dumps(lyrics,ensure_ascii=False)+'\nMUSIC: '+json.dumps(music)
    from .provider import generate_json
    return compile_plan(generate_json(prompt,out=out),lyrics,fps)

def compile_plan(data,lyrics,fps=24):
    if data.get('unsupported_reason'):raise ValueError('Unsupported song/story: '+str(data['unsupported_reason']))
    words=lyrics['words'];dur=lyrics['duration'];n=len(words);scenes=data.get('scenes',[])
    if not scenes or not 1<=len(scenes)<=10:raise ValueError('Invalid shot count')
    starts=[s.get('start_word_id') for s in scenes]
    if any(type(v) is not int or not 0<=v<n for v in starts) or starts[0]!=0 or starts!=sorted(set(starts)):raise ValueError('Invalid lyric boundaries')
    total=math.ceil(dur*fps);out=[]
    last_end=words[-1]['end']
    tail=any(float(x.get('start',dur))<=last_end+.15 and float(x.get('end',0))>=dur-.15 for x in lyrics.get('instrumental',[])) and dur-last_end>=1.0
    vocal_end=round(last_end*fps) if tail else total
    for i,s in enumerate(scenes):
        first=starts[i];last=starts[i+1] if i+1<len(starts) else n
        if s.get('lyric_ids')!=list(range(first,last)):raise ValueError('Every word must belong to exactly one contiguous shot')
        cue=s.get('cue_word_id')
        if type(cue) is not int or not first<=cue<last:raise ValueError('Cue outside its lyric phrase')
        a=0 if i==0 else round(words[first]['start']*fps);b=round(words[last]['start']*fps) if last<n else vocal_end
        cue_time=words[cue]['start']
        if lyrics.get('timing_granularity')=='phrase':
            cue_time+=min(1.5,(words[cue]['end']-words[cue]['start'])*.55)
        cf=min(b-1,round(cue_time*fps))
        if not a<=cf<b:raise ValueError('Cue outside shot after quantization')
        out.append({'kind':s['kind'],'start_frame':a,'end_frame':b,'cue_frame':cf,'lyric_ids':s['lyric_ids'],'reason':s['reason']})
    if tail:
        kind=data.get('epilogue_kind','heart')
        if kind not in ACTIONS:raise ValueError('Unsupported instrumental epilogue')
        out.append({'kind':kind,'start_frame':vocal_end,'end_frame':total,'cue_frame':(vocal_end+total)//2,
            'lyric_ids':[],'reason':'Instrumental ending: return to the established rose motif; no invented sung words.'})
    return validate({'version':1,'title':data.get('title','Song draft'),'intent':data.get('intent',''),'fps':fps,'total_frames':total,'palette':data.get('palette'),'scenes':out,'review_status':'draft','timing_method':lyrics.get('timing_method','supplied timings'),'timing_verified':False,'timing_granularity':lyrics.get('timing_granularity','word'),'cue_method':'art-directed emphasis within timed phrases' if lyrics.get('timing_granularity')=='phrase' else 'ASR word start'})
