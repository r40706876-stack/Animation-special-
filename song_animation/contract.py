import math

ACTIONS = {
    'thorn': 'A rose is pressed into an open palm; its thorn causes a small symbolic wound and red drop.',
    'wounded_heart': 'A heart develops visible scars; the recurring rose stays inside it.',
    'thorns': 'A walking person follows a curved route around thorn branches, leaving footprints.',
    'gift': 'One articulated hand brings a rose into the other palm; giver releases it.',
    'bloom': 'A layered rose opens and its centre expands into the following shot.',
    'crowd': 'Top-down pedestrians move past a solitary central person holding the rose.',
    'paths': 'Two people follow separate curved paths and move away from each other.',
    'heart': 'A hand-drawn heart accumulates coloured memory paths and pulses subtly.',
}
PALETTES = {
    'warm': {'paper':'#f5e7cf','ink':'#443c42','accent':'#c44757','blue':'#426a80','green':'#698b72','muted':'#b6aca0'},
    'hope': {'paper':'#eef0db','ink':'#344b4b','accent':'#d36551','blue':'#50879a','green':'#73a07b','muted':'#bdc5b8'},
    'memory': {'paper':'#e7e9ed','ink':'#3e475f','accent':'#b85074','blue':'#5d799e','green':'#789c92','muted':'#b6bac4'},
}

def validate(plan):
    if plan.get('version')==2:
        from .vector import validate_vector
        return validate_vector(plan)
    if plan.get('version') != 1: raise ValueError('Unsupported plan version')
    fps=plan.get('fps')
    if type(fps) is not int or not 12<=fps<=30: raise ValueError('fps must be an integer in 12..30')
    total=plan.get('total_frames')
    if type(total) is not int or not 1<=total<=fps*180: raise ValueError('Duration must be 0..180 seconds')
    if plan.get('palette') not in PALETTES: raise ValueError('Unsupported palette')
    scenes=plan.get('scenes',[])
    if not 1<=len(scenes)<=40: raise ValueError('Need 1..40 scenes')
    cursor=0
    for i,s in enumerate(scenes):
        if s.get('kind') not in ACTIONS: raise ValueError(f'Shot {i}: unsupported action {s.get("kind")}')
        a,b=s.get('start_frame'),s.get('end_frame')
        if type(a) is not int or type(b) is not int or a!=cursor or b<=a or b>total:
            raise ValueError(f'Shot {i}: gap/overlap/invalid frame bounds')
        if b-a<fps: raise ValueError('Shot too short to read action')
        if b-a>fps*8: raise ValueError('Shot exceeds eight-second action budget; split at a timed phrase')
        if not isinstance(s.get('reason'),str) or not s['reason'].strip(): raise ValueError('Missing visual meaning')
        cue=s.get('cue_frame')
        if type(cue) is not int or not a<=cue<b: raise ValueError('Cue must lie inside shot')
        for k in ('lyric_ids',):
            if not isinstance(s.get(k),list) or any(type(v) is not int or v<0 for v in s[k]): raise ValueError('Bad lyric references')
        cursor=b
    if cursor!=total: raise ValueError('Uncovered song tail')
    return plan

def validate_lyrics(words,duration):
    previous=0
    for w in words:
        a,b=w['start'],w['end']
        if not all(isinstance(x,(int,float)) and math.isfinite(x) for x in (a,b)) or not 0<=a<b<=duration+.05:
            raise ValueError('Invalid ASR timing; review transcript')
        if a<previous-.05: raise ValueError('Overlapping ASR words; review transcript')
        if not str(w.get('text','')).strip(): raise ValueError('Empty lyric word')
        previous=b
    return words
