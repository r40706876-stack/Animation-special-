"""Keep actual ASR word timings; never distribute time by character count."""
import json,subprocess,tempfile
from pathlib import Path
from .contract import validate_lyrics

def duration(path):return float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',str(path)]))

def analyze(audio,out,model='large-v3-turbo'):
    from faster_whisper import WhisperModel
    dur=duration(audio)
    if not 1<=dur<=180:raise ValueError('First version accepts 1..180 second segments')
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    engine=WhisperModel(model,device='cpu',compute_type='int8')
    def recognize(path,offset=0):
        segments,_=engine.transcribe(str(path),language='hi',word_timestamps=True,vad_filter=False,
            condition_on_previous_text=False,beam_size=5,no_speech_threshold=None,
            initial_prompt='यह हिंदी में गाया हुआ गाना है।')
        result=[]
        for seg in segments:
            for w in seg.words or []:
                if w.word.strip() and w.end>w.start:
                    result.append({'text':w.word.strip(),'start':round(w.start+offset,3),
                        'end':round(min(dur,w.end+offset),3),'probability':round(w.probability,4)})
        return result
    words=recognize(audio)
    recovered=False
    # Songs can lose their opening in a full-window decode. Retry that uncovered
    # leading window using the SAME model, without inventing or evenly spacing text.
    if words and words[0]['start']>1.5:
        boundary=words[0]['start']
        with tempfile.TemporaryDirectory() as td:
            clip=Path(td)/'opening.wav'
            subprocess.run(['ffmpeg','-y','-v','error','-i',str(audio),'-t',str(boundary),'-ac','1','-ar','16000',str(clip)],check=True)
            prefix=[w for w in recognize(clip) if w['end']<=boundary+.05]
        if prefix:
            words=prefix+words;recovered=True
    for i,w in enumerate(words):w['id']=i
    if not words:raise ValueError('No lyric words detected; supply verified timed lyrics')
    validate_lyrics(words,dur)
    result={'asr_model':model,'duration':dur,'language':'hi','timing_method':'faster-whisper word timestamps','timing_verified':False,'opening_recovery_used':recovered,
      'leading_untranscribed_seconds':words[0]['start'],
      'warnings':['Singing timestamps require listening review; no character-count retiming used'],
      'low_confidence_word_ids':[w['id'] for w in words if w['probability']<.55],'words':words}
    (out/'lyrics.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));return result

def music_features(audio,out):
    import librosa
    y,sr=librosa.load(str(audio),sr=22050);tempo,beats=librosa.beat.beat_track(y=y,sr=sr,units='time')
    data={'bpm':float(tempo.item() if hasattr(tempo,'item') else tempo),'beats':[round(float(t),3) for t in beats],'note':'Estimated beat grid; not lyric-word timing'}
    (Path(out)/'music.json').write_text(json.dumps(data,indent=2));return data
