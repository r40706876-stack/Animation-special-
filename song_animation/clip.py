"""Deterministic, bounded-length source selection with original sound preserved."""
import hashlib,json,subprocess,math
from pathlib import Path
import numpy as np
from .analyze import duration

def select_start(audio,source_duration,limit=30):
    if source_duration<=45:return 0.,'opening of an already short clip'
    # Stream a low-rate analysis copy; never load an entire long song into RAM.
    p=subprocess.Popen(['ffmpeg','-v','error','-i',str(audio),'-vn','-ac','1','-ar','8000','-f','f32le','-'],stdout=subprocess.PIPE)
    energy=[]
    while True:
        raw=p.stdout.read(8000*4)
        if not raw:break
        a=np.frombuffer(raw[:len(raw)//4*4],dtype='<f4')
        energy.append(float(np.sqrt(np.mean(a*a)+1e-12)))
    if p.wait():raise RuntimeError('Audio selection analysis failed')
    window=int(limit);scores=[]
    for i in range(max(1,len(energy)-window+1)):
        x=np.asarray(energy[i:i+window]);scores.append(float(x.mean()+.2*x.std()))
    return float(min(int(np.argmax(scores)),max(0,source_duration-limit))),'strongest sustained musical energy window (not a semantic chorus guarantee)'

def prepare(audio,out,limit=30,start=None):
    audio=Path(audio);out=Path(out);out.mkdir(parents=True,exist_ok=True)
    source_duration=duration(audio)
    if not math.isfinite(source_duration) or source_duration<=0:raise ValueError('Audio has no finite duration')
    if start is None:start,method=select_start(audio,source_duration,limit)
    else:method='explicit user-selected start'
    if not 0<=start<source_duration:raise ValueError('Clip start lies outside the song')
    seconds=min(float(limit),source_duration-start)
    if seconds<1:raise ValueError('At least one second of audio is required')
    target=out/'source_clip.wav'
    subprocess.run(['ffmpeg','-y','-v','error','-ss',str(start),'-i',str(audio),'-vn','-t',str(seconds),'-ac','1','-ar','22050','-c:a','pcm_s16le',str(target)],check=True)
    info={'source_sha256':hashlib.sha256(audio.read_bytes()).hexdigest(),'source_duration':source_duration,
        'start':start,'duration':duration(target),'limit':limit,'method':method,'short_inputs_padded':False}
    (out/'selection.json').write_text(json.dumps(info,indent=2));return target,info
