"""Durable completion receipts keep scheduled retries from redoing cleared songs."""
import base64,hashlib,json,os,re,time
from pathlib import Path

def source_hash(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
    return h.hexdigest()

def completed(root,audio):
    sha=source_hash(audio);p=Path(root)/'song_animation'/'completed'/(sha+'.json')
    if not p.is_file():return False
    try:data=json.loads(p.read_text())
    except (ValueError,OSError):return False
    if not isinstance(data,dict):return False
    return data.get('source_sha256')==sha and data.get('status')=='checks_passed'

def last_attempt(root,audio):
    p=Path(root)/'song_animation'/'attempted'/(source_hash(audio)+'.json')
    if not p.is_file():return 0
    try:return float(json.loads(p.read_text()).get('attempted_at',0))
    except (ValueError,TypeError):return 0

def receipt(audio,out):
    out=Path(out);status=json.loads((out/'status.json').read_text());gate=json.loads((out/'quality_gate.json').read_text())
    video=out/'checked.mp4'
    if status.get('status')!='checks_passed' or gate.get('passed') is not True or not video.is_file():raise ValueError('A failed/draft song cannot receive a completion receipt')
    actual=source_hash(video)
    if gate.get('technical',{}).get('video_sha256')!=actual:raise ValueError('Completion video does not match the checked export')
    source=source_hash(audio);selection=json.loads((out/'selection.json').read_text())
    if selection.get('source_sha256')!=source:raise ValueError('Completion belongs to a different uploaded song')
    clip_hash=source_hash(out/'source_clip.wav')
    if gate.get('technical',{}).get('source_clip_sha256')!=clip_hash:raise ValueError('The checked audio excerpt has changed')
    return {'source_sha256':source,'source_clip_sha256':clip_hash,'clip_start':selection['start'],'clip_duration':selection['duration'],'status':'checks_passed','video_sha256':actual,
        'run_id':os.getenv('GITHUB_RUN_ID',''),'commit':os.getenv('GITHUB_SHA',''),
        'human_approval':False,'universal_quality_certified':False}

def save_record(session,repo,token,folder,data):
    headers={'Authorization':'Bearer '+token,'Accept':'application/vnd.github+json'}
    url='https://api.github.com/repos/'+repo+'/contents/song_animation/'+folder+'/'+data['source_sha256']+'.json'
    for attempt in range(3):
        old=session.get(url,headers=headers,params={'ref':'main'},timeout=25)
        payload={'branch':'main','message':'Record song '+folder+' '+data['source_sha256'][:12],
            'content':base64.b64encode((json.dumps(data,indent=2)+'\n').encode()).decode()}
        if old.status_code==200:
            payload['sha']=old.json()['sha']
        elif old.status_code!=404:old.raise_for_status()
        r=session.put(url,headers=headers,json=payload,timeout=25)
        if r.status_code==409 and attempt<2:time.sleep(attempt+1);continue
        r.raise_for_status();return

def main():
    import argparse,requests
    a=argparse.ArgumentParser();a.add_argument('--audio',required=True);a.add_argument('--out',required=True)
    a.add_argument('--attempt',action='store_true');args=a.parse_args()
    if args.attempt:
        status=Path(args.out)/'status.json'
        if not status.is_file():print('No song processing status to record');return
        state=json.loads(status.read_text())
        data={'source_sha256':source_hash(args.audio),'status':state.get('status','unknown'),'attempted_at':time.time(),'run_id':os.getenv('GITHUB_RUN_ID','')}
    else:data=receipt(args.audio,args.out)
    repo=os.environ['GITHUB_REPOSITORY'];token=os.environ['GH_RECEIPT_TOKEN']
    if not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+',repo):raise ValueError('Invalid repository')
    save_record(requests,repo,token,'attempted' if args.attempt else 'completed',data)
    print('Saved song attempt record' if args.attempt else 'Saved checked-song completion receipt')
if __name__=='__main__':main()
