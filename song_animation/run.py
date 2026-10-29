import argparse,json
from pathlib import Path
from .analyze import analyze,music_features,duration
from .director import make_plan
from .render import render
from .contract import validate_lyrics

def main():
    a=argparse.ArgumentParser();a.add_argument('--audio',required=True);a.add_argument('--out',default='song_output');a.add_argument('--lyrics');a.add_argument('--model',default='large-v3-turbo');a.add_argument('--width',type=int,default=540)
    args=a.parse_args();out=Path(args.out);out.mkdir(parents=True,exist_ok=True)
    try:
        if args.lyrics:
            lyrics=json.loads(Path(args.lyrics).read_text());actual=duration(args.audio)
            if abs(lyrics['duration']-actual)>.1:raise ValueError('Lyrics duration does not match audio')
            validate_lyrics(lyrics['words'],actual)
        else:lyrics=analyze(args.audio,out,args.model)
        music=music_features(args.audio,out);plan=make_plan(lyrics,music)
        (out/'plan.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2));render(plan,out,args.audio,args.width)
        (out/'status.json').write_text(json.dumps({'status':'review_draft','automatic_publish':False,'universal_song_support':False}))
    except Exception as e:
        (out/'status.json').write_text(json.dumps({'status':'failed','error_type':type(e).__name__,'automatic_publish':False}))
        raise
if __name__=='__main__':main()
