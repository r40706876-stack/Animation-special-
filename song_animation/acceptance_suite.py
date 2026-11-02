"""Exercise real songs sequentially, with independent full-film evidence."""
import argparse,hashlib,json,os,signal,subprocess,sys,time
from pathlib import Path

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def load(path):
    try:return json.loads(Path(path).read_text())
    except (OSError,ValueError):return {}

def cases(root,manifest):
    root=Path(root).resolve();data=load(manifest);result=[];seen=set()
    for value in data.get('audio_paths',[]):
        p=(root/value).resolve()
        if not p.is_relative_to(root/'song_animation/inputs') or not p.is_file():raise ValueError('Acceptance input must exist under song_animation/inputs')
        digest=sha(p)
        if digest in seen:raise ValueError('Acceptance needs different audio bytes, not renamed copies')
        seen.add(digest);result.append({'audio_path':str(p.relative_to(root)),'source_sha256':digest})
    if len(result)<3:raise ValueError('At least three distinct real audio inputs are required')
    return result

def assess(audio,out):
    from .quality import visual_decision,inspect_export
    out=Path(out);plan=load(out/'plan.json');status=load(out/'status.json');gate=load(out/'quality_gate.json')
    reasons=[];selection=load(out/'selection.json')
    if status.get('status')!='checks_passed' or gate.get('passed') is not True:reasons.append('Production did not clear its full gate')
    if selection.get('source_sha256')!=sha(audio):reasons.append('Wrong source audio')
    visual={};technical={}
    if plan.get('scenes'):
        for name,source in [('composition_review','composition'),('visual_review','export')]:
            review=load(out/(name+'.json'))
            decision=visual_decision(review,len(plan['scenes']))
            if review.get('sample_source')!=source:decision={'passed':False,'reasons':['Wrong review sample source']}
            visual[name]=decision
            if not decision['passed']:reasons.append(name+' did not clear')
        if (out/'checked.mp4').is_file() and (out/'source_clip.wav').is_file():
            technical=inspect_export(out/'checked.mp4',out/'source_clip.wav',plan,1080)
            if not technical['passed']:reasons.append('Independent technical recheck failed')
        else:reasons.append('No checked MP4 and original selected clip')
    else:reasons.append('No generated scene plan')
    return {'passed':not reasons,'reasons':reasons,'visual':visual,'technical':technical,'production_status':status.get('status','not_started'),'manual_source_art_allowed':False,'universal_quality_certified':False}

def run(root,manifest,out,case_timeout=4800):
    root=Path(root).resolve();out=Path(out).resolve();out.mkdir(parents=True,exist_ok=True)
    inputs=cases(root,manifest);records=[];deferred=False
    environment=dict(os.environ,SONG_ACCEPTANCE_COLD_START='1')
    for index,item in enumerate(inputs):
        folder=out/(str(index)+'-'+Path(item['audio_path']).stem);folder.mkdir(exist_ok=True)
        record=dict(item,case=index,out=str(folder.relative_to(out)),cold_start=True)
        provenance_path=folder/'acceptance_origin.json';origin=load(provenance_path)
        if origin and (origin.get('source_sha256')!=item['source_sha256'] or origin.get('manual_source_art_allowed') is not False):raise ValueError('Acceptance checkpoint source/provenance changed')
        if not origin:
            if any(folder.iterdir()):raise ValueError('Refusing unbound production or manual assets inside a fresh acceptance case')
            origin={'source_sha256':item['source_sha256'],'manual_source_art_allowed':False,'acceptance_initialized_at':time.time(),'generation_commit':os.getenv('GITHUB_SHA','local')}
            provenance_path.write_text(json.dumps(origin,indent=2))
        previous=load(folder/'acceptance_case.json')
        if previous.get('passed') is True and assess(root/item['audio_path'],folder)['passed']:
            records.append(dict(previous,reused_verified_output=True));continue
        if previous.get('retry_not_before',0)>time.time():
            deferred=True;record['retry_not_before']=previous['retry_not_before']
        if deferred:
            record.update(passed=False,production_status='deferred_provider_cooldown',reasons=['Earlier case reached provider quota/service hold; no additional production launched'])
        else:
            started=time.time()
            try:
                process=subprocess.Popen([sys.executable,'-m','song_animation.resume','--audio',item['audio_path'],'--out',str(folder),'--width','1080','--artwork','flux-layers','--allow-local-recovery'],cwd=root,env=environment,start_new_session=True)
                record['returncode']=process.wait(timeout=case_timeout)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid,signal.SIGKILL);process.wait()
                record.update(returncode=124,timeout=True)
            record.update(assess(root/item['audio_path'],folder));record['elapsed_seconds']=round(time.time()-started,1)
            if record['returncode']!=0:
                record['passed']=False
                record['reasons'].append('Production process did not complete successfully')
            state=load(folder/'status.json')
            if state.get('status')=='waiting_for_provider':
                deferred=True
                record['retry_not_before']=time.time()+max(0,float(state.get('retry_after_seconds',0)))
        record['generation_commit']=origin['generation_commit']
        (folder/'acceptance_case.json').write_text(json.dumps(record,ensure_ascii=False,indent=2))
        records.append(record)
        report={'passed':len(records)==len(inputs) and all(r.get('passed') is True for r in records),'cases':records,'minimum_cases':3,'input_count':len(inputs),'manual_source_art_allowed':False,'universal_quality_certified':False}
        (out/'acceptance_report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
    if os.getenv('GITHUB_STEP_SUMMARY'):
        lines=['## Real-song automatic acceptance','', '| Input | Result |', '|---|---|']
        lines.extend('| '+r['audio_path']+' | '+('PASS' if r.get('passed') else r.get('production_status','blocked'))+' |' for r in records)
        lines+=['','Pass requires each actual composition/export review and independent MP4/audio verification. Unit tests alone cannot clear this suite.']
        with open(os.environ['GITHUB_STEP_SUMMARY'],'a') as f:f.write('\n'.join(lines)+'\n')
    # All cases may have resumed from verified completed outputs.
    report={'passed':len(records)==len(inputs) and all(r.get('passed') is True for r in records),'cases':records,'minimum_cases':3,'input_count':len(inputs),'manual_source_art_allowed':False,'universal_quality_certified':False}
    (out/'acceptance_report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
    return 0 if report['passed'] else 1

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--manifest',required=True);p.add_argument('--out',default='song_acceptance');a=p.parse_args()
    sys.exit(run(Path.cwd(),a.manifest,a.out))
