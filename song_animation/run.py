import argparse,json,hashlib
from pathlib import Path
from .analyze import analyze,music_features,duration
from .director import make_plan
from .render import render
from .contract import validate_lyrics

def main():
    a=argparse.ArgumentParser();a.add_argument('--audio',required=True);a.add_argument('--out',default='song_output');a.add_argument('--lyrics');a.add_argument('--model',default='large-v3-turbo');a.add_argument('--width',type=int,default=540);a.add_argument('--transcriber',choices=['audio-model','whisper'],default='audio-model');a.add_argument('--planner',choices=['auto','local'],default='auto');a.add_argument('--allow-local-recovery',action='store_true')
    args=a.parse_args();out=Path(args.out);out.mkdir(parents=True,exist_ok=True)
    try:
        if args.lyrics:
            lyrics=json.loads(Path(args.lyrics).read_text());actual=duration(args.audio)
            if abs(lyrics['duration']-actual)>.1:raise ValueError('Lyrics duration does not match audio')
            validate_lyrics(lyrics['words'],actual)
        else:
            key=hashlib.sha256(Path(args.audio).read_bytes()).hexdigest()+'-'+args.model+'-'+args.transcriber+'-v3'
            checkpoint=out/'analysis_checkpoint.json'
            if checkpoint.exists() and (out/'lyrics.json').exists() and json.loads(checkpoint.read_text()).get('key')==key:
                lyrics=json.loads((out/'lyrics.json').read_text());validate_lyrics(lyrics['words'],duration(args.audio))
                print('Resuming matching ASR checkpoint',flush=True)
            else:
                
                if args.transcriber=='audio-model':
                    from .audio_lyrics import analyze_audio
                    lyrics=analyze_audio(args.audio,out)
                else:lyrics=analyze(args.audio,out,args.model)
                checkpoint.write_text(json.dumps({'key':key}))
        music=music_features(args.audio,out)
        from .local_director import local_plan
        if args.planner=='local':
            plan=local_plan(lyrics)
        else:
            try:
                plan=make_plan(lyrics,music,out=out);plan['planner']='gemini'
            except RuntimeError:
                if not args.allow_local_recovery:raise
                plan=local_plan(lyrics)
                plan['provider_recovery_used']=True
                print('Provider unavailable; generating explicitly labelled local-rule draft',flush=True)
        (out/'plan.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2));render(plan,out,args.audio,args.width)
        (out/'status.json').write_text(json.dumps({'status':'review_draft','automatic_publish':False,'universal_song_support':False}))
    except Exception as e:
        (out/'status.json').write_text(json.dumps({'status':'failed','error_type':type(e).__name__,'automatic_publish':False}))
        raise
if __name__=='__main__':main()
