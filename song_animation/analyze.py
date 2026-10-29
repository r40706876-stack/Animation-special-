"""Keep actual ASR word timings; never distribute time by character count."""
import json,subprocess
from pathlib import Path
from .contract import validate_lyrics

def duration(path):return float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',str(path)]))

def analyze(audio,out,model='small'):
    from faster_whisper import WhisperModel
    dur=duration(audio)
    if not 1<=dur<=180:raise ValueError('First version accepts 1..180 second segments')
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    segments,info=WhisperModel(model,device='cpu',compute_type='int8').transcribe(str(audio),language='hi',word_timestamps=True,vad_filter=False,condition_on_previous_text=False,beam_size=5)
    words=[]
    for seg in segments:
        for w in seg.words or []:
            if w.word.strip() and w.end>w.start:words.append({'id':len(words),'text':w.word.strip(),'start':round(w.start,3),'end':round(w.end,3),'probability':round(w.probability,4)})
    if not words:raise ValueError('No lyric words detected; supply verified timed lyrics')
    validate_lyrics(words,dur)
    result={'duration':dur,'language':'hi','timing_method':'faster-whisper word timestamps','timing_verified':False,
      'warnings':['Singing timestamps require listening review; no character-count retiming used'],
      'low_confidence_word_ids':[w['id'] for w in words if w['probability']<.55],'words':words}
    (out/'lyrics.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));return result

def music_features(audio,out):
    import librosa
    y,sr=librosa.load(str(audio),sr=22050);tempo,beats=librosa.beat.beat_track(y=y,sr=sr,units='time')
    data={'bpm':float(tempo.item() if hasattr(tempo,'item') else tempo),'beats':[round(float(t),3) for t in beats],'note':'Estimated beat grid; not lyric-word timing'}
    (Path(out)/'music.json').write_text(json.dumps(data,indent=2));return data
