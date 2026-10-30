"""Shot coverage is story staging, not merely a count of cuts or camera zooms."""
import re

def validate_coverage(scenes,duration):
    if duration<20:return
    if len(scenes)<5:raise ValueError('A 20..30 second film needs at least five developing shots')
    setups=set();events=set();last=None;run=0
    for i,scene in enumerate(scenes):
        c=scene.get('coverage')
        if not isinstance(c,dict):raise ValueError(f'Shot {i} needs staged visual coverage')
        for key in ('environment','staging','framing','visible_event'):
            if not isinstance(c.get(key),str) or len(c[key].strip())<4:raise ValueError(f'Shot {i} coverage lacks {key}')
        # Repeated setup IDs must be repeated verbatim; changing a camera cannot
        # invent a new location. Actual decoded images receive a separate review.
        setup=tuple(re.sub(r'\s+',' ',c[k].strip().lower()) for k in ('environment','staging'))
        setups.add(setup);events.add(c['visible_event'].strip().lower())
        run=run+1 if setup==last else 1;last=setup
        if run>2:raise ValueError('Three consecutive shots repeat one setup; move the story into a new staging')
    if len(setups)<3:raise ValueError('Need at least three genuinely distinct story setups, not crops of one picture')
    if len(events)<4:raise ValueError('Need at least four distinct visible story events')

def coverage_decision(review,scene_count):
    if scene_count<5:return [],[]
    if review.get('visual_variety') is True:return [],[]
    note='The film repeats one visual setup. Change the actual staging, action and compositions across the connected story; renaming shots or zooming is insufficient.'
    return [note],[{'shot':i,'issue':note} for i in range(scene_count)]
