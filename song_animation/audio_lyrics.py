"""Direct-audio phrase transcription. No fabricated word-level precision."""
import base64,json,tempfile,subprocess,re
from pathlib import Path
from .analyze import duration
from .contract import validate_lyrics
from .provider import generate_json

INTERVAL={'type':'OBJECT','properties':{'start':{'type':'NUMBER'},'end':{'type':'NUMBER'}},'required':['start','end']}
LYRICS_SCHEMA={'type':'OBJECT','properties':{
    'language':{'type':'STRING'},'genre':{'type':'STRING'},'mood':{'type':'STRING'},'summary':{'type':'STRING'},'has_vocals':{'type':'BOOLEAN'},
    'segments':{'type':'ARRAY','items':{'type':'OBJECT','properties':{
        'start':{'type':'NUMBER'},'end':{'type':'NUMBER'},'text':{'type':'STRING'},'uncertain':{'type':'BOOLEAN'}},
        'required':['start','end','text','uncertain']}},
    'instrumental':{'type':'ARRAY','items':INTERVAL},'unclear':{'type':'ARRAY','items':INTERVAL}},
    'required':['segments','instrumental','unclear','language','genre','mood','summary','has_vocals']}

def validate_transcript_script(data):
    """Reject an original-script violation; not a semantic certificate."""
    language=str(data.get('language','')).lower()
    text=' '.join(str(s.get('text','')) for s in data.get('segments',[]) if not s.get('uncertain',True))
    if ('hindi' in language or language=='hi') and re.search(r'[A-Za-z]',text) and not re.search(r'[\u0900-\u097f]',text):
        raise ValueError('Hindi transcript contains only Roman letters; original sung words need correction')


def analyze_audio(audio,out):
    out=Path(out);dur=duration(audio)
    if not 1<=dur<=180:raise ValueError('Use a 1..180 second song segment')
    with tempfile.TemporaryDirectory() as td:
        p=Path(td)/'analysis.mp3'
        subprocess.run(['ffmpeg','-y','-v','error','-i',str(audio),'-vn','-ac','1','-ar','22050','-b:a','64k',str(p)],check=True)
        part={'inline_data':{'mime_type':'audio/mpeg','data':base64.b64encode(p.read_bytes()).decode()}}
    prompt=f'''Listen to this actual {dur:.3f}-second song clip (language and genre unknown; identify them from the audio) from beginning to end. Transcribe exactly the audible sung words in their original script (Hindi, Punjabi, English or the actual detected language). This is audio transcription, not lyric recall: do not fill words from a known song, infer missing endings or put sung text into instrumental/outro music. Include the opening and repeated final refrain; do not skip a repeated lyric. Keep original word choices, gender and repetition. If unclear, mark an unclear interval instead of guessing.
Return JSON only: {{"segments":[{{"start":0.0,"end":2.2,"text":"exact audible words","uncertain":false}}],"instrumental":[{{"start":30,"end":34}}],"unclear":[],"language":"detected language","genre":"free description","mood":"free description","summary":"what the music/lyrics express","has_vocals":true}}.
Segment into meaningful phrases of about 2..6 words, using ACTUAL phrase boundaries in seconds. These are approximate phrase timings; do not fabricate individual-word timestamps or divide time evenly. Every audible vocal phrase must appear once and in order, including the very beginning. Instrumental portions contain no invented lyrics. Times must be within 0..{dur:.3f}. Instrumental-only music is valid: return segments=[] and has_vocals=false, describing genre/mood/summary. Describe unclear vocals in unclear intervals without inventing captions. No translation, commentary, visual prompts or lyrics beyond this clip.'''
    errors=[];evidence={};verification={};independent=None
    for attempt in range(2):
        try:
            extra='\nRECOVERY EVIDENCE (not verified lyrics): '+json.dumps(evidence,ensure_ascii=False) if evidence else ''
            if errors:extra+='\nThe prior attempt failed: '+errors[-1]+'. Correct the actual language/words; never repeat unsupported guesses.'
            data=generate_json(prompt+extra,out=out,tag='audio_lyrics' if attempt==0 else 'audio_lyrics_recovered',audio_part=part,schema=LYRICS_SCHEMA,prefer_quality=True)
            validate_transcript_script(data)
            if data.get('has_vocals',True) and (data.get('unclear') or any(x.get('uncertain',True) for x in data.get('segments',[]))):
                raise ValueError('Unclear sung words require correction before semantic scenes are generated')
            units=[dict(id=i,**{k:x[k] for k in ('text','start','end')}) for i,x in enumerate(data.get('segments',[]))]
            validate_lyrics(units,dur)
            if data.get('has_vocals',True) and not units:raise ValueError('Vocal text omitted')
            for region in data.get('instrumental',[])+data.get('unclear',[]):
                if not 0<=region['start']<region['end']<=dur+.03:raise ValueError('Audio interval exceeds selected clip')
            if data.get('has_vocals',True) and independent is None:
                from .recognition import independent_audio_text
                independent=independent_audio_text(audio,out,data.get('language'))
            verification=generate_json('Independently listen to the AUDIO, not just the proposed text. Reject pseudo-words, wrong language or meaning, invented lyrics, missing/repeated vocals labelled instrumental, or completing a cut-off line from song memory. Return JSON {"valid":boolean,"reasons":["specific reason"],"meaning":"literal meaning only if audible"}. A genre, beat or fingerprint match is not proof of words. Compare the independent ASR too: a coherent transcript can still contain a wrong action verb (writing versus lifting, for example). Resolve disagreements by listening to the actual audio; do not rubber-stamp the proposed text or blindly trust ASR. Proposed transcript: '+json.dumps(data,ensure_ascii=False)+'\nINDEPENDENT DECODER EVIDENCE: '+json.dumps(independent,ensure_ascii=False),out=out,tag='audio_verification_'+str(attempt),audio_part=part,prefer_quality=True,require_full_model=True)
            if verification.get('valid') is not True:raise ValueError('Audio transcript failed independent meaning review: '+json.dumps(verification.get('reasons',[]),ensure_ascii=False))
            break
        except (ValueError,RuntimeError,KeyError,TypeError) as e:
            errors.append(str(e)[:1200])
            if attempt==0:
                from .recognition import recovery_evidence
                evidence=recovery_evidence(audio,out,dur)
    else:
        (out/'audio_hold.json').write_text(json.dumps({'status':'needs_lyrics','attempts':2,'reasons':errors},ensure_ascii=False,indent=2))
        raise ValueError('Audio meaning review failed after automatic recovery; invented scenes blocked')
    words=[]
    for segment in data.get('segments',[]):
        text=str(segment.get('text','')).strip()
        if not text:continue
        words.append({'id':len(words),'text':text,'start':float(segment['start']),
            'end':min(dur,float(segment['end'])),'uncertain':bool(segment.get('uncertain',True))})
    if not words and data.get('has_vocals',True) and not data.get('unclear'):raise ValueError('Audio model omitted vocal text without marking uncertainty')
    validate_lyrics(words,dur)
    result={'duration':dur,'language':data.get('language','unknown'),'genre':data.get('genre',''),'mood':data.get('mood',''),'summary':data.get('summary',''),'has_vocals':data.get('has_vocals',bool(words)),'timing_method':'direct audio-model phrase boundaries',
        'timing_granularity':'phrase','timing_verified':False,'audio_verification':verification,'independent_asr_used':independent is not None,'recovery_used':bool(errors),'words':words,
        'instrumental':data.get('instrumental',[]),'unclear':data.get('unclear',[]),
        'leading_untranscribed_seconds':words[0]['start'] if words else 0,
        'warnings':['Approximate phrase timing only; ids identify phrases, not individual words. Listening review required.']}
    (out/'lyrics.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
    if result['unclear'] or any(w['uncertain'] for w in words):
        result['warnings'].append('Uncertain vocal intervals are left without invented captions; review needed')
        result['words']=[w for w in words if not w['uncertain']]
        for i,w in enumerate(result['words']):w['id']=i
        (out/'lyrics.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
    # Explicit instrumental regions may explain a legitimate lead-in; otherwise hold.
    if words and words[0]['start']>1.5 and not any(float(s.get('start',99))<=.1 and float(s.get('end',0))>=words[0]['start']-.1 for s in result['instrumental']):
        result['warnings'].append('Opening vocals may be missing; caption coverage requires listening review')
        (out/'lyrics.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
    return result
