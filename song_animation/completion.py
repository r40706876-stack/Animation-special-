"""Durable completion receipts keep scheduled retries from redoing cleared songs."""
import base64,hashlib,json,os,re
from pathlib import Path

def source_hash(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
    return h.hexdigest()

def completed(root,audio):
    sha=source_hash(audio);p=Path(root)/'song_animation'/'completed'/(sha+'.json')
    if not p.is_file():return False
    data=json.loads(p.read_text())
    return data.get('source_sha256')==sha and data.get('status')=='checks_passed'

def receipt(audio,out):
    out=Path(out);status=json.loads((out/'status.json').read_text());gate=json.loads((out/'quality_gate.json').read_text())
    video=out/'checked.mp4'
    if status.get('status')!='checks_passed' or gate.get('passed') is not True or not video.is_file():raise ValueError('A failed/draft song cannot receive a completion receipt')
    actual=source_hash(video)
    if gate.get('technical',{}).get('video_sha256')!=actual:raise ValueError('Completion video does not match the checked export')
    return {'source_sha256':source_hash(audio),'status':'checks_passed','video_sha256':actual,
        'run_id':os.getenv('GITHUB_RUN_ID',''),'commit':os.getenv('GITHUB_SHA',''),
        'human_approval':False,'universal_quality_certified':False}

def main():
    import argparse,requests
    a=argparse.ArgumentParser();a.add_argument('--audio',required=True);a.add_argument('--out',required=True);args=a.parse_args()
    data=receipt(args.audio,args.out);repo=os.environ['GITHUB_REPOSITORY'];token=os.environ['GH_RECEIPT_TOKEN']
    if not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+',repo):raise ValueError('Invalid repository')
    headers={'Authorization':'Bearer '+token,'Accept':'application/vnd.github+json'}
    url='https://api.github.com/repos/'+repo+'/contents/song_animation/completed/'+data['source_sha256']+'.json'
    old=requests.get(url,headers=headers,params={'ref':'main'},timeout=25)
    if old.status_code==200:
        print('Completion receipt already exists');return
    if old.status_code!=404:old.raise_for_status()
    r=requests.put(url,headers=headers,json={'branch':'main','message':'Record checked song '+data['source_sha256'][:12],
        'content':base64.b64encode((json.dumps(data,indent=2)+'\n').encode()).decode()},timeout=25)
    r.raise_for_status();print('Saved checked-song completion receipt')
if __name__=='__main__':main()
