"""Install image backends only when this exact source can actually use them."""
import hashlib,json,os
from pathlib import Path
from .pipeline_checkpoint import needs_scene_rewrite
from .source_art import apply
from .flux_layers import is_structural


def required(out,artwork='flux-layers'):
    result={'needs_cutouts':artwork=='flux-layers','needs_cpu':True,'reason':'uncovered_source'}
    if artwork!='flux-layers':return result
    out=Path(out)
    try:
        sha=hashlib.sha256((out/'source_clip.wav').read_bytes()).hexdigest()
        state=json.loads((out/'art_backend_choice.json').read_text()) if (out/'art_backend_choice.json').exists() else {}
        if state.get('source_clip_sha256')==sha and state.get('visual_quality_rejected') and 'rejection_reasons' in state:
            result['needs_cpu']=False
        recovery=json.loads((out/'pipeline_checkpoint.json').read_text())
        if needs_scene_rewrite(recovery,artwork):return result
        plan,assets,scenes=apply(recovery['plan'],sha)
        foreground={n.get('asset') for s in plan['scenes'] for n in s['nodes'] if n.get('asset') and n.get('role')!='background'}
        missing=[aid for aid in foreground if aid not in assets and not is_structural(dict(plan['assets'][aid],id=aid)) and min(plan['assets'][aid]['width'],plan['assets'][aid]['height'])>=45]
        if not missing and scenes==set(range(len(plan['scenes']))):
            result.update(needs_cutouts=False,needs_cpu=False,reason='exact_source_artwork_preserved')
    except (OSError,ValueError,KeyError,TypeError,AttributeError):pass
    return result

if __name__=='__main__':
    result=required('song_draft',os.getenv('ARTWORK','flux-layers'));print(json.dumps(result))
    if os.getenv('GITHUB_OUTPUT'):
        with open(os.environ['GITHUB_OUTPUT'],'a') as file:
            for key in ('needs_cutouts','needs_cpu'):file.write(key+'='+str(result[key]).lower()+'\n')
