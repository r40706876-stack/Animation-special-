"""Direct-audio phrase transcription. No fabricated word-level precision."""
import base64,json,tempfile,subprocess
from pathlib import Path
from .analyze import duration
from .contract import validate_lyrics
from .provider import generate_json

INTERVAL={'type':'OBJECT','properties':{'start':{'type':'NUMBER'},'end':{'type':'NUMBER'}},'required':['start','end']}
LYRICS_SCHEMA={'type':'OBJECT','properties':{
    'segments':{'type':'ARRAY','items':{'type':'OBJECT','properties':{
        'start':{'type':'NUMBER'},'end':{'type':'NUMBER'},'text':{'type':'STRING'},'uncertain':{'type':'BOOLEAN'}},
        'required':['start','end','text','uncertain']}},
    'instrumental':{'type':'ARRAY','items':INTERVAL},'unclear':{'type':'ARRAY','items':INTERVAL}},
    'required':['segments','instrumental','unclear']}

def analyze_audio(audio,out):
    out=Path(out);dur=duration(audio)
    if not 1<=dur<=180:raise ValueError('Use a 1..180 second song segment')
    with tempfile.TemporaryDirectory() as td:
        p=Path(td)/'analysis.mp3'
        subprocess.run(['ffmpeg','-y','-v','error','-i',str(audio),'-vn','-ac','1','-ar','22050','-b:a','64k',str(p)],check=True)
        part={'inline_data':{'mime_type':'audio/mpeg','data':base64.b64encode(p.read_bytes()).decode()}}
    prompt=f'''Listen to this actual {dur:.3f}-second Hindi song clip from beginning to end. Transcribe exactly the audible sung words in Devanagari. This is audio transcription, not lyric recall: do not fill words from a known song, infer missing endings or put sung text into instrumental/outro music. Include the opening and repeated final refrain; do not skip a repeated lyric. Keep original word choices, gender and repetition. If unclear, mark an unclear interval instead of guessing.
Return JSON only: {{"segments":[{{"start":0.0,"end":2.2,"text":"exact audible words","uncertain":false}}],"instrumental":[{{"start":30,"end":34}}],"unclear":[]}}.
Segment into meaningful phrases of about 2..6 words, using ACTUAL phrase boundaries in seconds. These are approximate phrase timings; do not fabricate individual-word timestamps or divide time evenly. Every audible vocal phrase must appear once and in order, including the very beginning. Instrumental portions contain no invented lyrics. Times must be within 0..{dur:.3f}. No translation, commentary, visual prompts or lyrics beyond this clip.'''
    data=generate_json(prompt,out=out,tag='audio_lyrics',audio_part=part,schema=LYRICS_SCHEMA)
    words=[]
    for segment in data.get('segments',[]):
        text=str(segment.get('text','')).strip()
        if not text:continue
        words.append({'id':len(words),'text':text,'start':float(segment['start']),
            'end':min(dur,float(segment['end'])),'uncertain':bool(segment.get('uncertain',True))})
    if not words:raise ValueError('Audio model returned no audible lyrics')
    validate_lyrics(words,dur)
    result={'duration':dur,'language':'hi','timing_method':'direct audio-model phrase boundaries',
        'timing_granularity':'phrase','timing_verified':False,'words':words,
        'instrumental':data.get('instrumental',[]),'unclear':data.get('unclear',[]),
        'leading_untranscribed_seconds':words[0]['start'],
        'warnings':['Approximate phrase timing only; ids identify phrases, not individual words. Listening review required.']}
    (out/'lyrics.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
    if result['unclear'] or any(w['uncertain'] for w in words):raise ValueError('Unclear sung phrases require review before rendering')
    # Explicit instrumental regions may explain a legitimate lead-in; otherwise hold.
    if words[0]['start']>1.5 and not any(float(s.get('start',99))<=.1 and float(s.get('end',0))>=words[0]['start']-.1 for s in result['instrumental']):
        raise ValueError('Opening lyrics may be missing; direct-audio transcription held')
    return result
