"""Choose exact new/changed uploads; never inject file names into shell source."""
import json,os,subprocess
from pathlib import Path
EXTS={'.mp3','.wav','.m4a','.aac','.ogg','.opus','.mp4'}

def select(root,before='',head='',manual=None,event='push'):
    root=Path(root).resolve()
    def checked(path):
        p=(root/path).resolve()
        if not p.is_relative_to(root) or not p.is_file() or p.suffix.lower() not in EXTS:
            raise ValueError('Audio must be an existing repository audio file')
        return str(p.relative_to(root))
    if event=='workflow_dispatch':return [checked(manual)] if manual else []
    changed=[]
    if before and before.strip('0'):
        p=subprocess.run(['git','diff','--name-only','-z',before,head,'--','song_animation/inputs/'],cwd=root,capture_output=True,check=False)
        if p.returncode:raise ValueError('Cannot resolve upload diff; refusing to process the wrong audio')
        changed=p.stdout.decode().split('\0')
    files=[]
    for p in changed:
        if p and Path(p).suffix.lower() in EXTS and (root/p).is_file():files.append(checked(p))
    # Code-only pushes run the checked-in reference as an integration test.
    if not files:files=[checked('song_animation/inputs/reference.mp3')]
    return sorted(set(files))

def main():
    files=select(Path.cwd(),os.getenv('PUSH_BEFORE',''),os.getenv('PUSH_HEAD',''),os.getenv('MANUAL_AUDIO'),os.getenv('EVENT_NAME','push'))
    value=json.dumps(files)
    print('Selected audio files:',value)
    if os.getenv('GITHUB_OUTPUT'):
        with open(os.environ['GITHUB_OUTPUT'],'a') as f:f.write('audio='+value+'\n')
if __name__=='__main__':main()
