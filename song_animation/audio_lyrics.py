"""Direct-audio phrase transcription. No fabricated word-level precision."""
import base64,json,tempfile,subprocess,re,unicodedata,hashlib
from pathlib import Path
from .analyze import duration
from .contract import validate_lyrics
from .provider import generate_json,ProviderUnavailable

INTERVAL={'type':'OBJECT','properties':{'start':{'type':'NUMBER'},'end':{'type':'NUMBER'}},'required':['start','end']}
MAX_TRANSCRIPT_ATTEMPTS=3

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


def strong_word_conflicts(segments,independent):
    """Hold consecutive confident lexical disagreements; never substitute ASR as truth."""
    def tokens(text):
        text=unicodedata.normalize('NFD',str(text)).casefold().replace('\u093c','')
        return [''.join(c for c in word if unicodedata.category(c)[0] in 'LM') for word in text.split()]
    def script(text):
        return {unicodedata.name(c,'').split()[0] for c in text if unicodedata.category(c).startswith('L')}
    conflicts=[];previous=None
    for word in (independent or {}).get('words',[]):
        try:
            start=float(word['start']);end=float(word['end']);confidence=float(word['probability'])
        except (KeyError,TypeError,ValueError):
            previous=None;continue
        lexical=tokens(word.get('text',''));lexical=[t for t in lexical if len(t)>=2]
        nearby=' '.join(str(s.get('text','')) for s in segments if float(s['start'])<end+.6 and float(s['end'])>start-.6)
        absent=bool(lexical) and confidence>=.7 and 0<=start<end and script(''.join(lexical))==script(nearby) and any(t not in tokens(nearby) for t in lexical)
        if absent:
            current={'start':start,'end':end,'text':word['text'],'confidence':confidence}
            if previous and start-previous['end']<=.7 and tokens(previous['text'])!=lexical and (confidence+previous['confidence'])/2>=.85:
                conflicts.append({'start':previous['start'],'end':end,'decoder_words':previous['text']+' '+word['text'],'proposed':nearby})
            previous=current
        else:previous=None
    return conflicts

def confirm_conflicts_from_audio(part,out,segments,conflicts,audio=None,language=None):
    """Blindly re-hear disputed phrases; never prefer ASR or a positive verdict.

    Independent singing ASR can split a compound into different words. Its high
    token confidence is not proof that the direct transcript is wrong. Resolve
    this only when a separate FULL-model audio transcription agrees letter for
    letter (ignoring spacing/punctuation) with the proposed complete phrases.
    The blind request receives times, not either transcript's suggested words.
    """
    selected=[s for s in segments if any(s['start']<c['end'] and s['end']>c['start'] for c in conflicts)]
    groups=[]
    for s in sorted(selected,key=lambda s:s['start']):
        if groups and s['start']<=groups[-1]['end']+.01:
            groups[-1]['end']=max(groups[-1]['end'],s['end']);groups[-1]['texts'].append(s['text'])
        else:groups.append({'start':s['start'],'end':s['end'],'texts':[s['text']]})
    if not groups:raise ValueError('Unresolved word disagreement has no audible phrase interval')
    windows=[{'region':i,'start':g['start'],'end':g['end']} for i,g in enumerate(groups)]
    prompt='Listen to the attached audio independently. Transcribe ONLY the actual audible words in each labelled region clip, preserving original script. No proposed words or song identity are supplied: do not recall lyrics or complete cut-off lines from memory. Singing ASR can confuse word boundaries, but do not assume either version is right. Return JSON {"regions":[{"region":0,"text":"exact heard phrase","uncertain":false}]}, exactly one result for each region. Mark uncertainty rather than guessing. Never use Roman transliteration for Hindi: use Devanagari for audible Hindi.\nLANGUAGE/SCRIPT HINT (verify from audio): '+str(language or 'unknown')+'\nSOURCE TIME WINDOWS: '+json.dumps(windows)
    if audio is not None:
        # A phrase timestamp can begin inside a sustained sung syllable. Supply
        # the same selected clip as listening context as well as physical region
        # crops; neither proposed words nor decoder guesses are exposed here.
        parts=[{'text':'CONTEXT AUDIO: use this selected clip only to recognize the musical phrase. Return words only for the labelled target regions below.'},part]
        with tempfile.TemporaryDirectory() as td:
            for w in windows:
                focused=Path(td)/f"region_{w['region']}.mp3"
                subprocess.run(['ffmpeg','-y','-v','error','-ss',str(w['start']),'-i',str(audio),'-t',str(w['end']-w['start']),'-vn','-ac','1','-ar','22050','-b:a','64k',str(focused)],check=True)
                parts.extend([{'text':f"REGION {w['region']}: this audio contains only the requested interval. Transcribe this clip only."},{'inline_data':{'mime_type':'audio/mpeg','data':base64.b64encode(focused.read_bytes()).decode()}}])
        blind=generate_json(prompt,out=out,tag='audio_conflict_blind',extra_parts=parts,prefer_quality=True,require_full_model=True)
    else:
        blind=generate_json(prompt,out=out,tag='audio_conflict_blind',audio_part=part,prefer_quality=True,require_full_model=True)
    model=blind.get('_provider_model','')
    rows=blind.get('regions')
    if not isinstance(model,str) or not model or 'lite' in model.lower() or not isinstance(rows,list) or len(rows)!=len(groups):
        raise ValueError('Strong independent word disagreement remains unresolved: missing full-model blind audio evidence')
    def letters(text):
        text=unicodedata.normalize('NFD',str(text)).casefold().replace('\u093c','')
        # Hindi alternatives such as a written half-r versus an implicit
        # consonant cluster must not consume the correction budget. Preserve
        # all other letters/vowels: different pronouns, negations and verbs
        # still fail. Full-audio meaning review remains mandatory afterwards.
        text=re.sub('र्(?=[क-ह])','र',text)
        return ''.join(c for c in text if unicodedata.category(c)[0] in 'LM')
    seen=set()
    for row in rows:
        i=row.get('region') if isinstance(row,dict) else None
        if type(i) is not int or not 0<=i<len(groups) or i in seen or row.get('uncertain') is not False or not isinstance(row.get('text'),str):
            raise ValueError('Strong independent word disagreement remains unresolved: incomplete blind audio evidence')
        seen.add(i);proposed=' '.join(groups[i]['texts'])
        if letters(row['text'])!=letters(proposed):
            raise ValueError('Strong independent word disagreement: blind audio transcription heard '+row['text']+' but proposed '+proposed+'. Correct the transcript from actual audio before creating scenes.')
    return blind


def analyze_audio(audio,out):
    out=Path(out);dur=duration(audio)
    if not 1<=dur<=180:raise ValueError('Use a 1..180 second song segment')
    candidate_path=out/'audio_candidate.json'
    candidate_key=hashlib.sha256(Path(audio).read_bytes()+b'blind-phrase-v1').hexdigest()
    pending={}
    try:
        saved=json.loads(candidate_path.read_text())
        if saved.get('key')==candidate_key and isinstance(saved.get('data'),dict):pending=saved
    except (OSError,ValueError,AttributeError):pass
    with tempfile.TemporaryDirectory() as td:
        p=Path(td)/'analysis.mp3'
        subprocess.run(['ffmpeg','-y','-v','error','-i',str(audio),'-vn','-ac','1','-ar','22050','-b:a','64k',str(p)],check=True)
        part={'inline_data':{'mime_type':'audio/mpeg','data':base64.b64encode(p.read_bytes()).decode()}}
    prompt=f'''Listen to this actual {dur:.3f}-second song clip (language and genre unknown; identify them from the audio) from beginning to end. Transcribe exactly the audible sung words in their original script (Hindi, Punjabi, English or the actual detected language). This is audio transcription, not lyric recall: do not fill words from a known song, infer missing endings or put sung text into instrumental/outro music. Include the opening and repeated final refrain; do not skip a repeated lyric. Keep original word choices, gender and repetition. If unclear, mark an unclear interval instead of guessing.
HARD SCRIPT REQUIREMENT: Hindi/hi text must use Devanagari (including vocalizations such as आ), and Punjabi text must use the detected native script. Roman transliteration of Hindi or Punjabi fails validation. Re-listen to action verbs and negations rather than completing familiar song lyrics from memory.
Return JSON only: {{"segments":[{{"start":0.0,"end":2.2,"text":"exact audible words","uncertain":false}}],"instrumental":[{{"start":30,"end":34}}],"unclear":[],"language":"detected language","genre":"free description","mood":"free description","summary":"what the music/lyrics express","has_vocals":true}}.
Segment into meaningful phrases of about 2..6 words, using ACTUAL phrase boundaries in seconds. These are approximate phrase timings; do not fabricate individual-word timestamps or divide time evenly. Every audible vocal phrase must appear once and in order, including the very beginning. Instrumental portions contain no invented lyrics. Times must be within 0..{dur:.3f}. Instrumental-only music is valid: return segments=[] and has_vocals=false, describing genre/mood/summary. Describe unclear vocals in unclear intervals without inventing captions. No translation, commentary, visual prompts or lyrics beyond this clip.'''
    errors=[];evidence={};verification={};independent=pending.get('independent');conflict_evidence=None
    if not isinstance(independent,dict) or not isinstance(independent.get('words'),list):independent=None
    for attempt in range(MAX_TRANSCRIPT_ATTEMPTS):
        try:
            extra='\nRECOVERY EVIDENCE (not verified lyrics): '+json.dumps(evidence,ensure_ascii=False) if evidence else ''
            if errors:extra+='\nThe prior attempt failed: '+errors[-1]+'. Correct the actual language/words; never repeat unsupported guesses.'
            data=pending['data'] if attempt==0 and pending else generate_json(prompt+extra,out=out,tag='audio_lyrics' if attempt==0 else 'audio_lyrics_recovered'+(f'_{attempt}' if attempt>1 else ''),audio_part=part,schema=LYRICS_SCHEMA,prefer_quality=True,require_full_model=True)
            validate_transcript_script(data)
            if data.get('has_vocals',True) and (data.get('unclear') or any(x.get('uncertain',True) for x in data.get('segments',[]))):
                raise ValueError('Unclear sung words require correction before semantic scenes are generated')
            units=[dict(id=i,**{k:x[k] for k in ('text','start','end')}) for i,x in enumerate(data.get('segments',[]))]
            validate_lyrics(units,dur)
            from .lyrics import preflight
            preflight({'words':units,'timing_granularity':'phrase'})
            if data.get('has_vocals',True) and not units:raise ValueError('Vocal text omitted')
            for region in data.get('instrumental',[])+data.get('unclear',[]):
                if not 0<=region['start']<region['end']<=dur+.03:raise ValueError('Audio interval exceeds selected clip')
            candidate_path.write_text(json.dumps({'key':candidate_key,'data':data,'independent':independent},ensure_ascii=False))
            if data.get('has_vocals',True) and independent is None:
                from .recognition import independent_audio_text
                independent=independent_audio_text(audio,out,data.get('language'))
                candidate_path.write_text(json.dumps({'key':candidate_key,'data':data,'independent':independent},ensure_ascii=False))
            conflict_evidence=None
            conflicts=strong_word_conflicts(data.get('segments',[]),independent)
            if conflicts:
                conflict_evidence=confirm_conflicts_from_audio(part,out,data.get('segments',[]),conflicts,audio=audio,language=data.get('language'))
            verification=generate_json('Independently listen to the AUDIO, not just the proposed text. Reject pseudo-words, wrong language or meaning, invented lyrics, missing/repeated vocals labelled instrumental, or completing a cut-off line from song memory. Return JSON {"valid":boolean,"reasons":["specific reason"],"meaning":"literal meaning only if audible"}. A genre, beat or fingerprint match is not proof of words. Compare the independent ASR too: a coherent transcript can still contain a wrong action verb (writing versus lifting, for example). Resolve disagreements by listening to the actual audio; do not rubber-stamp the proposed text or blindly trust ASR. Proposed transcript: '+json.dumps(data,ensure_ascii=False)+'\nINDEPENDENT DECODER EVIDENCE: '+json.dumps(independent,ensure_ascii=False),out=out,tag='audio_verification_'+str(attempt),audio_part=part,prefer_quality=True,require_full_model=True)
            if verification.get('valid') is not True:raise ValueError('Audio transcript failed independent meaning review: '+json.dumps(verification.get('reasons',[]),ensure_ascii=False))
            break
        except ProviderUnavailable:
            raise
        except (ValueError,RuntimeError,KeyError,TypeError) as e:
            candidate_path.unlink(missing_ok=True);pending={}
            errors.append(str(e)[:1200])
            if attempt==0:
                from .recognition import recovery_evidence
                evidence={'independent_asr':independent} if independent else recovery_evidence(audio,out,dur)
    else:
        (out/'audio_hold.json').write_text(json.dumps({'status':'needs_lyrics','attempts':MAX_TRANSCRIPT_ATTEMPTS,'reasons':errors},ensure_ascii=False,indent=2))
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
        'timing_granularity':'phrase','timing_verified':False,'audio_verification':verification,'independent_asr_used':independent is not None,'independent_asr':independent,'blind_conflict_evidence':conflict_evidence,'recovery_used':bool(errors),'words':words,
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
    candidate_path.unlink(missing_ok=True)
    return result
