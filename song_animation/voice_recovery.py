"""Recover candidate words from isolated vocals; all outputs remain unverified."""
import base64,json,subprocess
from pathlib import Path
from .provider import generate_json
from .audio_lyrics import LYRICS_SCHEMA
out=Path('song_recovery');out.mkdir(exist_ok=True)
source=Path('song_animation/inputs/ritik_new_song_20261030.mp3')
subprocess.run(['python','-m','demucs','-n','htdemucs','--two-stems','vocals','-d','cpu','--shifts','0','-j','1','-o',str(out/'stems'),str(source)],check=True,timeout=420)
vocals=next((out/'stems').rglob('vocals.wav'))
variants=[('original',source,None),('vocals',vocals,None),('pitch_up',vocals,'asetrate=44100*1.189207,resample=44100,atempo=0.840896'),('pitch_down',vocals,'asetrate=44100*0.840896,resample=44100,atempo=1.189207')]
# FFmpeg calls the resampling filter aresample.
variants=[(n,p,f.replace('resample=','aresample=') if f else f) for n,p,f in variants]
from faster_whisper import WhisperModel
engine=WhisperModel('large-v3',device='cpu',compute_type='int8',cpu_threads=2,num_workers=1)
for name,path,filters in variants:
    p=out/(name+'.wav')
    cmd=['ffmpeg','-v','error','-y','-i',str(path)]
    if filters:cmd+=['-af',filters]
    subprocess.run(cmd+['-ac','1','-ar','16000',str(p)],check=True)
    segments,info=engine.transcribe(str(p),word_timestamps=True,vad_filter=False,condition_on_previous_text=False,beam_size=5,temperature=0)
    data={'variant':name,'verified':False,'language':info.language,'language_probability':info.language_probability,'segments':[{'start':s.start,'end':s.end,'text':s.text,'avg_logprob':s.avg_logprob} for s in segments]}
    (out/(name+'.json')).write_text(json.dumps(data,ensure_ascii=False,indent=2))
    print(name,json.dumps(data,ensure_ascii=False),flush=True)
# Original unaltered-timing isolated stem provides separate model evidence.
p=out/'vocals.mp3'
subprocess.run(['ffmpeg','-v','error','-y','-i',str(vocals),'-ac','1','-b:a','128k',str(p)],check=True)
try:
    generate_json('Listen to isolated vocals and identify the ACTUAL language and intelligible original-script words. Never force Hindi. Ignore background instruments. Report unclear intervals instead of pseudo-words. Do not identify a song by guessing. All times must be within 0..15.279 seconds. Return the schema with phrase segments and literal summary if intelligible.',out=out,tag='separated_audio',audio_part={'inline_data':{'mime_type':'audio/mpeg','data':base64.b64encode(p.read_bytes()).decode()}},schema=LYRICS_SCHEMA,prefer_quality=True)
except Exception as e:
    (out/'audio_error.json').write_text(json.dumps({'error':type(e).__name__}))
