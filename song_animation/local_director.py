"""Transparent, limited semantic-rule recovery for relationship/pain lyrics.
This is not an LLM, transcript correction or a universal song director.
"""
import re
from .director import compile_plan

RULES=[
 ('thorn',r'फूल|फुल|गुलाब|rose|flower', 'फूल के साथ चोट का विरोधाभास: काँटा हथेली तक पहुँचता है।'),
 ('thorns',r'काँट|कांट|काटों|काटो|thorn', 'काँटों से बचना: पात्र टेढ़े रास्ते से गुजरता है।'),
 ('wounded_heart',r'ज़ख|जख|दखम|जग्म|घाव|चोट|दिल|heart|wound', 'दिल और चोट का भाव: दिल पर निशान उभरते हैं।'),
 ('paths',r'अपने|आजमा|आज़मा|आदमा|दूर|जुदा|छोड़|बिछ|apart', 'दूरी या भरोसा टूटना: दो परिचित अलग दिशाओं में चलते हैं।'),
 ('crowd',r'दोस्त|गैर|अजनबी|भीड़|friend|stranger', 'लोगों के बीच अकेलापन: दूसरे चलते हैं और मुख्य पात्र ठहरता है।'),
]

def local_plan(lyrics,fps=24):
    words=lyrics['words']
    if not words or words[0]['start']>1.5:raise ValueError('Untranscribed opening: retry opening ASR or supply timed lyrics before local scene planning')
    text=' '.join(w['text'] for w in words)
    if re.search(r'प्रश्न|विकल्प|परीक्षा|सही उत्तर|किलोग्राम|अनुच्छेद',text):
        raise ValueError('Local director does not support instructional lyrics')
    supported=[r for r in RULES if re.search(r[1],text,re.I)]
    if len(supported)<2:raise ValueError('Local director cannot represent this song faithfully; new assets or AI plan required')
    # Phrase boundaries use pauses/punctuation, never equal-duration invented words.
    starts=[0]
    for i in range(1,len(words)):
        prev=words[i-1];elapsed=words[i]['start']-words[starts[-1]]['start']
        if elapsed>=1.2 and (words[i]['start']-prev['end']>.4 or re.search(r'[,।!?]$',prev['text']) or elapsed>=6):starts.append(i)
    # Avoid a tiny final shot; no unsupported rapid flash cuts.
    if len(starts)>1 and lyrics['duration']-words[starts[-1]]['start']<1.2:starts.pop()
    if len(starts)>10:raise ValueError('Local director needs a shorter song segment')
    scenes=[]
    for j,first in enumerate(starts):
        end=starts[j+1] if j+1<len(starts) else len(words)
        phrase=' '.join(w['text'] for w in words[first:end])
        match=next((r for r in RULES if re.search(r[1],phrase,re.I)),None)
        contextual=match is None
        if contextual:
            # Carry the established motif through an adjoining phrase, transparently.
            match=next((r for r in supported if r[0]=='wounded_heart'),supported[0])
        kind,pattern,reason=match
        cues=[i for i in range(first,end) if re.search(pattern,words[i]['text'],re.I)]
        cue=cues[0] if cues else first
        scenes.append({'kind':kind,'start_word_id':first,'cue_word_id':cue,'lyric_ids':list(range(first,end)),
            'reason':reason+(' समीप की पंक्तियों के संदर्भ से चुना गया; अर्थ की समीक्षा जरूरी।' if contextual else '')})
    data={'title':'गीत का स्थानीय दृश्य मसौदा','intent':'दर्द, भरोसा और दूरी; नियमों से चुने सीमित प्रतीक','palette':'memory','scenes':scenes}
    plan=compile_plan(data,lyrics,fps)
    plan.update(planner='local_rules',semantic_verified=False,universal_song_support=False,
        warnings=['Local rule-based recovery, not an AI-authored story; verify ASR wording, meaning and scene continuity.'])
    return plan
