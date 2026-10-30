import argparse,copy,hashlib,json
from pathlib import Path
from .analyze import analyze,music_features,duration
from .clip import prepare
from .render import render
from .contract import validate_lyrics

def cached_reference(source,selection):
    """Only reuse exact-source analysis when no vocal phrase was cut in half."""
    if selection['start']!=0:return None
    p=Path(__file__).parent/'fixtures'/'lyrics_by_sha'/(selection['source_sha256']+'.json')
    if not p.exists():return None
    data=json.loads(p.read_text())
    if data.get('audio_sha256')!=selection['source_sha256']:return None
    lyrics=copy.deepcopy(data['lyrics']);end=selection['duration']
    if any(w['start']<end<w['end'] for w in lyrics['words']):return None
    lyrics['words']=[w for w in lyrics['words'] if w['end']<=end]
    for i,w in enumerate(lyrics['words']):w['id']=i
    lyrics['duration']=end
    lyrics['instrumental']=[dict(start=x['start'],end=min(end,x['end'])) for x in lyrics.get('instrumental',[]) if x['start']<end]
    lyrics['source_analysis']='cached direct-audio analysis for exact original source and uncut phrases'
    return lyrics

def main():
    a=argparse.ArgumentParser()
    a.add_argument('--audio',required=True);a.add_argument('--out',default='song_output');a.add_argument('--lyrics')
    a.add_argument('--model',default='large-v3-turbo');a.add_argument('--width',type=int,default=1080)
    a.add_argument('--start',type=float);a.add_argument('--engine',choices=['generated','classic'],default='generated')
    a.add_argument('--transcriber',choices=['audio-model','whisper'],default='audio-model')
    a.add_argument('--planner',choices=['auto','local'],default='auto');a.add_argument('--allow-local-recovery',action='store_true')
    args=a.parse_args();out=Path(args.out);out.mkdir(parents=True,exist_ok=True)
    try:
        clip,selection=prepare(args.audio,out,limit=30,start=args.start)
        if args.lyrics:
            lyrics=json.loads(Path(args.lyrics).read_text())
            if abs(lyrics['duration']-selection['duration'])>.1:raise ValueError('Supplied lyrics must be timed relative to the selected clip')
            validate_lyrics(lyrics['words'],selection['duration'])
        else:
            audio_hash=hashlib.sha256(clip.read_bytes()).hexdigest()
            key=audio_hash+'-'+args.model+'-'+args.transcriber+'-multilingual-v5-meaning-review'
            checkpoint=out/'analysis_checkpoint.json'
            if checkpoint.exists() and (out/'lyrics.json').exists() and json.loads(checkpoint.read_text()).get('key')==key:
                lyrics=json.loads((out/'lyrics.json').read_text());validate_lyrics(lyrics['words'],selection['duration'])
                print('Resuming matching clip transcript',flush=True)
            else:
                lyrics=cached_reference(args.audio,selection) if args.transcriber=='audio-model' else None
                if lyrics is None:
                    if args.transcriber=='audio-model':
                        from .audio_lyrics import analyze_audio
                        lyrics=analyze_audio(clip,out)
                    else:lyrics=analyze(clip,out,args.model)
                (out/'lyrics.json').write_text(json.dumps(lyrics,ensure_ascii=False,indent=2))
                checkpoint.write_text(json.dumps({'key':key}))
        music=music_features(clip,out)
        if args.engine=='generated':
            from .generative import build
            plan=build(lyrics,music,out)
        else:
            from .director import make_plan
            from .local_director import local_plan
            if args.planner=='local':plan=local_plan(lyrics)
            else:
                try:plan=make_plan(lyrics,music,out=out);plan['planner']='gemini_classic'
                except RuntimeError:
                    if not args.allow_local_recovery:raise
                    plan=local_plan(lyrics);plan['provider_recovery_used']=True
        plan['selection']=selection
        (out/'plan.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2))
        render(plan,out,clip,args.width)
        if args.engine=='generated':
            from .review import review,refine
            assessment=review(plan,out)
            (out/'visual_review_before.json').write_text(json.dumps(assessment,ensure_ascii=False,indent=2))
            plan,changed=refine(plan,out,assessment)
            if changed:
                render(plan,out,clip,args.width)
                assessment=review(plan,out)
            plan['visual_issues_remaining']=assessment.get('issues',[])
            (out/'plan.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2))
        (out/'status.json').write_text(json.dumps({'status':'review_draft','engine':args.engine,
            'open_vocabulary':args.engine=='generated','duration_limit':30,'automatic_publish':False,
            'universal_quality_certified':False,'visual_review_issues':assessment.get('issues',[]) if args.engine=='generated' else [],'visual_repair_applied':changed if args.engine=='generated' else False,'warnings':lyrics.get('warnings',[])},ensure_ascii=False,indent=2))
    except Exception as e:
        (out/'status.json').write_text(json.dumps({'status':'failed','error_type':type(e).__name__,'automatic_publish':False}))
        raise
if __name__=='__main__':main()
