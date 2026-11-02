"""Choose one coherent artwork backend for a source, with a local fallback."""
import hashlib,json
from pathlib import Path
from .provider import ProviderUnavailable
from .free_image import SPACE
from . import flux_layers

def paint(plan,out,audio):
    out=Path(out);key=hashlib.sha256(Path(audio).read_bytes()).hexdigest();state=out/'art_backend_choice.json'
    from .source_art import apply
    plan,preserved_assets,preserved_scenes=apply(plan,key)
    keep_assets={'preserved_assets':preserved_assets} if preserved_assets else {}
    keep_scenes={'preserved_scenes':preserved_scenes} if preserved_scenes else {}
    selected='flux'
    if state.exists():
        try:
            saved=json.loads(state.read_text())
            if saved.get('source_clip_sha256')==key and saved.get('backend')=='cpu' and not saved.get('visual_quality_rejected'):selected='cpu'
        except (OSError,ValueError,AttributeError):pass
    if selected=='flux':
        try:
            candidate=flux_layers.paint_foreground(plan,out,**keep_assets)
            return flux_layers.paint_environments(candidate,out,**keep_scenes)
        except ProviderUnavailable as error:
            if not any(x.get('model')==SPACE for x in error.attempts):raise
            # A rejected local film is evidence against repeating that fallback.
            # Preserve its assets, but wait for the better backend instead of
            # spending another full production run on known-bad artwork.
            try:rejected=json.loads(state.read_text())
            except (OSError,ValueError):rejected={}
            if rejected.get('source_clip_sha256')==key and rejected.get('visual_quality_rejected'):
                raise
            print('Public image service unavailable; switching the WHOLE source to original local artwork',flush=True)
            # Never mix incompatible generations within one source on resume.
            state.write_text(json.dumps({'source_clip_sha256':key,'backend':'cpu','reason':'public_image_service_unavailable','quality_certified':False}))
    from .local_image import generate_image
    from .environments import REVISION
    namespace='cpu-original-v1-'+REVISION[:12]
    candidate=flux_layers.paint_foreground(plan,out,image_generator=generate_image,namespace=namespace,**keep_assets)
    return flux_layers.paint_environments(candidate,out,image_generator=generate_image,namespace=namespace,**keep_scenes)

def reject_local_backend(out):
    """Do not pin later attempts to a backend whose actual film failed review."""
    state=Path(out)/'art_backend_choice.json'
    try:data=json.loads(state.read_text())
    except (OSError,ValueError):return
    if data.get('backend')=='cpu':
        data['visual_quality_rejected']=True
        state.write_text(json.dumps(data))
