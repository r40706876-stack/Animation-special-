"""Render source-bound repaired scene samples; never publish them as a final film."""
import base64,hashlib,json,subprocess
from pathlib import Path
from .source_art import ROOT
from .render import render


def run(out='song_source_proofs'):
    outputs=[];repo=Path(__file__).resolve().parents[1]
    for spec in sorted(ROOT.glob('*/proof.json')):
        data=json.loads(spec.read_text());folder=spec.parent
        manifest=json.loads((folder/'manifest.json').read_text());plan=data['plan']
        for aid,item in manifest['assets'].items():
            p=(folder/item['file']).resolve()
            if not p.is_relative_to(folder.resolve()):raise ValueError('Proof artwork leaves source folder')
            raw=p.read_bytes()
            if hashlib.sha256(raw).hexdigest()!=item['sha256']:raise ValueError('Proof image bytes changed')
            plan['assets'][aid]['raster_png']=base64.b64encode(raw).decode()
        audio=(repo/data['source_input']).resolve()
        if not audio.is_relative_to(repo) or hashlib.sha256(audio.read_bytes()).hexdigest()!=data['source_input_sha256']:
            raise ValueError('Scene proof requires its exact uploaded audio')
        dest=Path(out)/folder.name;dest.mkdir(parents=True,exist_ok=True);clip=dest/'scene_audio.wav'
        subprocess.run(['ffmpeg','-y','-v','error','-ss',str(data['source_start_seconds']),'-i',str(audio),'-t',str(plan['total_frames']/plan['fps']),'-ac','2','-ar','44100','-c:a','pcm_s16le',str(clip)],check=True)
        video=render(plan,dest,clip,width=540)
        (dest/'DRAFT.json').write_text(json.dumps({'status':'isolated_scene_repair_DRAFT','source_scene_index':data['source_scene_index'],'full_song_complete':False,'visual_approval':False,'source_input':data['source_input'],'note':'Original audio excerpt with actual repaired scene motion. All full-film quality gates still required.'},indent=2))
        outputs.append(str(video))
    return outputs

if __name__=='__main__':print(json.dumps(run()))
