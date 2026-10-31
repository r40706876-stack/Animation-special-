import argparse,copy,hashlib,json,shutil,math
from pathlib import Path
from .analyze import analyze,music_features,duration
from .clip import prepare
from .render import render
from .contract import validate_lyrics
from .quality import QualityHold,visual_decision,inspect_export
from .provider import ProviderUnavailable
from .lyrics import preflight as caption_preflight

def load_analysis_checkpoint(out,key,duration):
    out=Path(out)
    try:
        if json.loads((out/'analysis_checkpoint.json').read_text()).get('key')!=key:return None
        lyrics=json.loads((out/'lyrics.json').read_text())
        if not math.isfinite(float(lyrics['duration'])) or abs(float(lyrics['duration'])-duration)>.05:return None
        validate_lyrics(lyrics['words'],duration);caption_preflight(lyrics)
        return lyrics
    except (OSError,ValueError,KeyError,TypeError,AttributeError):return None

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
    a.add_argument('--artwork',choices=['vector','painted-sets','painted-layers'],default='vector')
    a.add_argument('--stage',choices=['all','plan'],default='all')
    a.add_argument('--transcriber',choices=['audio-model','whisper'],default='audio-model')
    a.add_argument('--planner',choices=['auto','local'],default='auto');a.add_argument('--allow-local-recovery',action='store_true')
    args=a.parse_args();out=Path(args.out);out.mkdir(parents=True,exist_ok=True)
    # Never leave a stale checked output visible after a failed rerun.
    for name in ('checked.mp4','preview.mp4','quality_gate.json','audio_hold.json'):
        (out/name).unlink(missing_ok=True)
    (out/'status.json').write_text(json.dumps({'status':'running','automatic_publish':False}))
    try:
        clip,selection=prepare(args.audio,out,limit=30,start=args.start)
        if args.lyrics:
            lyrics=json.loads(Path(args.lyrics).read_text())
            if abs(lyrics['duration']-selection['duration'])>.1:raise ValueError('Supplied lyrics must be timed relative to the selected clip')
            validate_lyrics(lyrics['words'],selection['duration'])
        else:
            audio_hash=hashlib.sha256(clip.read_bytes()).hexdigest()
            key=audio_hash+'-'+args.model+'-'+args.transcriber+'-multilingual-v8-strong-independent-words'
            checkpoint=out/'analysis_checkpoint.json'
            lyrics=load_analysis_checkpoint(out,key,selection['duration'])
            if lyrics is not None:
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
        captions=caption_preflight(lyrics)
        (out/'caption_preflight.json').write_text(json.dumps(captions,ensure_ascii=False,indent=2))
        music=music_features(clip,out)
        if args.engine=='generated':
            from .generative import build
            plan=build(lyrics,music,out,artwork=args.artwork,plan_only=args.stage=='plan')
        else:
            from .director import make_plan
            from .local_director import local_plan
            if args.planner=='local':plan=local_plan(lyrics)
            else:
                try:plan=make_plan(lyrics,music,out=out);plan['planner']='gemini_classic'
                except RuntimeError:
                    if not args.allow_local_recovery:raise
                    plan=local_plan(lyrics);plan['provider_recovery_used']=True
        if args.stage=='plan':
            (out/'status.json').write_text(json.dumps({'status':'planned','automatic_publish':False,'checked_file':None}))
            return
        if args.engine=='generated' and args.artwork in ('painted-sets','painted-layers'):
            from .environments import paint_environments
            plan=paint_environments(plan,out)
            if args.artwork=='painted-layers':
                from .paint_layers import paint_foreground
                plan=paint_foreground(plan,out)
        plan['selection']=selection
        (out/'plan.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2))
        render(plan,out,clip,args.width)
        changed=False;assessment={};passes=[]
        if args.engine=='generated':
            from .review import review,refine
            for pass_index in range(3):
                assessment=review(plan,out)
                decision=visual_decision(assessment,len(plan['scenes']))
                (out/f'visual_review_pass_{pass_index}.json').write_text(json.dumps(assessment,ensure_ascii=False,indent=2))
                passes.append({'pass':pass_index,**decision})
                if decision['passed'] or pass_index==2 or not decision['repair_issues']:break
                plan,replaced=refine(plan,out,dict(assessment,issues=decision['repair_issues']),pass_index=pass_index+1)
                changed=changed or replaced
                if not replaced:break
                if args.artwork in ('painted-sets','painted-layers'):plan=paint_environments(plan,out)
                if args.artwork=='painted-layers':plan=paint_foreground(plan,out)
                render(plan,out,clip,args.width)
            plan['visual_issues_remaining']=decision['reasons']
            (out/'plan.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2))
        else:decision={'passed':False,'reasons':['Classic engine output is an unchecked draft']}
        technical=inspect_export(out/'preview.mp4',clip,plan,args.width)
        passed=decision['passed'] and technical['passed']
        gate={'passed':passed,'visual':decision,'technical':technical,'repair_passes':passes,'human_approval':False,'universal_quality_certified':False}
        (out/'quality_gate.json').write_text(json.dumps(gate,ensure_ascii=False,indent=2))
        status={'status':'checks_passed' if passed else 'blocked','engine':args.engine,'open_vocabulary':args.engine=='generated','duration_limit':30,'automatic_publish':False,'universal_quality_certified':False,'visual_repair_applied':changed,'warnings':lyrics.get('warnings',[]),'quality_gate':gate}
        if assessment.get('provider_wait'):status.update(provider_wait=True,retry_after_seconds=assessment.get('retry_after_seconds',0))
        if passed:
            shutil.copyfile(out/'preview.mp4',out/'checked.mp4')
            status['checked_file']='checked.mp4'
        (out/'status.json').write_text(json.dumps(status,ensure_ascii=False,indent=2))
        if not passed:raise QualityHold('Video checks did not pass; only review draft retained')
    except ProviderUnavailable as e:
        (out/'status.json').write_text(json.dumps({'status':'waiting_for_provider','error':str(e),'retry_after_seconds':e.retry_after_seconds,'automatic_publish':False}))
        raise
    except QualityHold as e:
        status_path=out/'status.json'
        current=json.loads(status_path.read_text()) if status_path.exists() else {}
        if current.get('status')!='blocked':
            status_path.write_text(json.dumps({'status':'blocked','error_type':'QualityHold','error':str(e)[:1200],'automatic_publish':False,'universal_quality_certified':False}))
        raise
    except Exception as e:
        (out/'status.json').write_text(json.dumps({'status':'failed','error_type':type(e).__name__,'error':str(e)[:1200],'automatic_publish':False}))
        raise
if __name__=='__main__':main()
