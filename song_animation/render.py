import argparse,hashlib,json,subprocess
from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np
from .art import render_frame
from .contract import validate
HERE=Path(__file__).parent

def digest(plan,audio):
    h=hashlib.sha256(json.dumps(plan,sort_keys=True).encode())
    for p in sorted(HERE.glob('*.py')):h.update(p.read_bytes())
    if audio:h.update(Path(audio).read_bytes())
    return h.hexdigest()

def render(plan,out,audio=None,width=540):
    validate(plan);out=Path(out);out.mkdir(parents=True,exist_ok=True)
    fps=plan['fps'];total=plan['total_frames'];duration=total/fps
    if width not in (540,1080):raise ValueError('Supported widths: 540 or 1080')
    final=out/'preview.mp4';key=digest(plan,audio)+f'-{width}';receipt=out/'receipt.json'
    if final.exists() and receipt.exists() and json.loads(receipt.read_text()).get('cache_key')==key and json.loads(receipt.read_text()).get('video_sha256')==hashlib.sha256(final.read_bytes()).hexdigest():
        print('Matching cached render',final);return final
    temp=out/'rendering.mp4'
    cmd=['ffmpeg','-y','-v','error','-f','rawvideo','-pix_fmt','rgb24','-s','540x960','-r',str(fps),'-i','-']
    if audio:cmd+=['-i',str(audio)]
    else:cmd+=['-f','lavfi','-i',f'anullsrc=r=44100:cl=stereo:d={duration}']
    cmd+=['-map','0:v','-map','1:a','-vf',f'scale={width}:{width*16//9}:flags=lanczos','-c:v','libx264','-crf','19','-preset','fast','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k','-af','apad','-t',str(duration),'-movflags','+faststart',str(temp)]
    sheets=[];motion=[]
    for i,s in enumerate(plan['scenes']):
        fs=[s['start_frame']+int((s['end_frame']-s['start_frame']-1)*q) for q in (.1,.45,.8)]
        imgs=[render_frame(plan,f) for f in fs]
        if plan.get('version')==2:
            from .vector import render_vector
            motion_imgs=[render_vector(plan,i,f) for f in fs]
        else:motion_imgs=imgs
        arrays=[np.asarray(x.resize((135,240)),dtype=np.float32) for x in motion_imgs]
        delta=max(float(np.abs(arrays[0]-x).mean()) for x in arrays[1:])
        motion.append({'shot':i,'kind':s['kind'],'sample_difference':round(delta,4),'note':'Pixel motion only; not semantic/retention certification'})
        if delta<.2:raise ValueError(f'Shot {i} has no readable sampled motion')
        for f,im in zip(fs,imgs):
            tile=im.resize((180,320));d=ImageDraw.Draw(tile);d.rectangle((0,297,180,320),fill='#fff7e6')
            d.text((5,302),f'{i+1} {s["kind"]} | {f/fps:.2f}s',fill='#343434');sheets.append(tile)
    contact=Image.new('RGB',(540,320*len(plan['scenes'])),'white')
    for i,im in enumerate(sheets):contact.paste(im,((i%3)*180,(i//3)*320))
    contact.save(out/'contact.jpg',quality=92)
    if plan.get('lyrics'):
        from .lyrics import export_srt
        export_srt(plan,out/'lyrics.srt')
    (out/'motion.json').write_text(json.dumps(motion,indent=2));(out/'plan.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2))
    with open(out/'ffmpeg.log','w') as log:
        proc=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=log)
        try:
            for f in range(total):
                proc.stdin.write(render_frame(plan,f).tobytes())
                if f%(fps*5)==0:print(f'Render {f}/{total}',flush=True)
            proc.stdin.close()
            if proc.wait():raise RuntimeError('FFmpeg failed; see ffmpeg.log')
        except BaseException:
            proc.kill();proc.wait();temp.unlink(missing_ok=True);raise
    probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_format','-show_streams','-of','json',str(temp)]))
    video=next(s for s in probe['streams'] if s['codec_type']=='video')
    if abs(float(video['duration'])-duration)>1/fps+.01:raise ValueError('Video duration drift')
    if int(video['nb_frames'])!=total:raise ValueError('Missing frames')
    if not any(s['codec_type']=='audio' for s in probe['streams']):raise ValueError('Missing audio stream')
    subprocess.run(['ffmpeg','-v','error','-xerror','-i',str(temp),'-f','null','-'],check=True)
    temp.replace(final)
    receipt.write_text(json.dumps({'video_sha256':hashlib.sha256(final.read_bytes()).hexdigest(),'cache_key':key,'frames':total,'duration':duration,'dimensions':[width,width*16//9],
        'lyrics_enabled':bool(plan.get('lyrics')),'caption_timing':'phrase' if plan.get('lyrics') else None,'audio':'source' if audio else 'intentional silent animation proof','status':'review_draft','lyric_sync_verified':False,'technical_checks':'passed','human_review_required':True},indent=2))
    return final

def main():
    a=argparse.ArgumentParser();a.add_argument('--plan',required=True);a.add_argument('--out',required=True);a.add_argument('--audio');a.add_argument('--width',type=int,default=540)
    args=a.parse_args();print(render(json.loads(Path(args.plan).read_text()),args.out,args.audio,args.width))
if __name__=='__main__':main()
