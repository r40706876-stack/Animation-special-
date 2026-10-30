"""Connected song stories: persistent subjects, causal changes and an earned ending."""
import re
FIELDS=('premise','emotional_goal','opening','turning_point','payoff')
def validate_story(story,scenes):
    if not isinstance(story,dict):raise ValueError('Missing connected story, not a keyword slideshow')
    for key in FIELDS:
        if not isinstance(story.get(key),str) or len(story[key].strip())<8:raise ValueError('Story lacks '+key)
    entities=story.get('entities')
    if not isinstance(entities,dict) or not entities:raise ValueError('Story needs persistent subjects or relationships')
    state={}
    for key,item in entities.items():
        if not isinstance(key,str) or not re.fullmatch(r'[A-Za-z0-9_-]{1,80}',key) or not isinstance(item,dict):raise ValueError('Invalid story entity')
        for field in ('description','initial_state'):
            if not isinstance(item.get(field),str) or len(item[field].strip())<5:raise ValueError('Story entity lacks '+field)
        state[key]=item['initial_state']
    for i,scene in enumerate(scenes):
        beat=scene.get('story')
        if not isinstance(beat,dict):raise ValueError(f'Shot {i} lacks its narrative purpose')
        for field in ('purpose','link_from_previous','emotional_change'):
            if not isinstance(beat.get(field),str) or len(beat[field].strip())<8:raise ValueError(f'Shot {i} lacks '+field)
        incoming,outgoing=beat.get('state_in'),beat.get('state_out')
        if incoming!=state:raise ValueError(f'Shot {i} resets a carried story state; begin from the previous consequence')
        if not isinstance(outgoing,dict) or set(outgoing)!=set(state) or any(not isinstance(v,str) or len(v.strip())<5 for v in outgoing.values()):raise ValueError(f'Shot {i} loses a tracked subject/state')
        if outgoing==incoming:raise ValueError(f'Shot {i} has no story change; a camera move or repeated portrait is insufficient')
        state=dict(outgoing)
    return story

def narrative_decision(review,scene_count):
    reasons=[];repairs=[]
    if review.get('story_arc') is not True:
        reasons.append('No visually earned connected story/payoff')
    links=review.get('story_links')
    if not isinstance(links,list) or len(links)!=max(0,scene_count-1):
        reasons.append('Missing cross-shot story review')
    else:
        seen=set()
        for link in links:
            source=link.get('from') if isinstance(link,dict) else None
            dest=link.get('to') if isinstance(link,dict) else None
            if type(source) is not int or type(dest) is not int or dest!=source+1 or not 0<=source<scene_count-1 or source in seen:
                reasons.append('Invalid story transition review');continue
            seen.add(source)
            if any(link.get(key) is not True for key in ('causal_connection','state_continuity','emotional_progression')):
                note=f'Story connection from shot {source} to {dest} failed'
                reasons.append(note);repairs.append({'shot':dest,'issue':note+': '+str(link.get('reason','Show the preceding consequence and its emotional effect'))[:1200]})
    if review.get('story_arc') is not True and not repairs:
        repairs.extend({'shot':i,'issue':'Repair the connected emotional story and ending; do not replace individual nouns with disconnected illustrations.'} for i in range(scene_count))
    return reasons,repairs
