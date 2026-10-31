"""Resume checkpoints after bounded transient provider outages within the same job."""
import argparse,json,subprocess,sys,time
from pathlib import Path

def execute(args,delays=(20,40,60)):
    parser=argparse.ArgumentParser(add_help=False)
    parser.add_argument('--out',default='song_output')
    known,_=parser.parse_known_args(args)
    out=Path(known.out);out.mkdir(parents=True,exist_ok=True)
    history=[]
    for attempt in range(len(delays)+1):
        # Never retry based on a stale status from an earlier invocation.
        (out/'status.json').unlink(missing_ok=True)
        result=subprocess.run([sys.executable,'-m','song_animation.run',*args])
        if result.returncode==0:return 0
        try:status=json.loads((out/'status.json').read_text())
        except (OSError,ValueError):return result.returncode
        if not isinstance(status,dict) or status.get('status')!='waiting_for_provider' or status.get('retryable') is not True or attempt==len(delays):return result.returncode
        wait=delays[attempt]
        try:server_wait=float(status.get('retry_after_seconds',0))
        except (TypeError,ValueError):return result.returncode
        # Do not turn long server-directed waits into repeated immediate calls.
        if server_wait>60:return result.returncode
        wait=max(wait,server_wait)
        history.append({'attempt':attempt+1,'wait_seconds':wait,'reason':'transient_provider_failure'})
        (out/'provider_resume.json').write_text(json.dumps(history,indent=2))
        print(f'Provider temporarily busy; resume saved work in {wait:g}s (retry {attempt+1}/{len(delays)})',flush=True)
        time.sleep(wait)
    return 1

if __name__=='__main__':sys.exit(execute(sys.argv[1:]))
