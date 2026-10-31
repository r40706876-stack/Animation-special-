"""Choose one coherent artwork backend for a source, with a local fallback."""
import hashlib,json
from pathlib import Path
from .provider import ProviderUnavailable
from .free_image import SPACE
from . import flux_layers

def paint(plan,out,audio):
    out=Path(out);key=hashlib.sha256(Path(audio).read_bytes()).hexdigest();state=out/'art_backend_choice.json'
    selected='flux'
    if state.exists():
        try:
            saved=json.loads(state.read_text())
            if saved.get('source_clip_sha256')==key and saved.get('backend')=='cpu':selected='cpu'
        except (OSError,ValueError,AttributeError):pass
    if selected=='flux':
        try:
            candidate=flux_layers.paint_foreground(plan,out)
            return flux_layers.paint_environments(candidate,out)
        except ProviderUnavailable as error:
            if not any(x.get('model')==SPACE for x in error.attempts):raise
            print('Public image service unavailable; switching the WHOLE source to original local artwork',flush=True)
            # Never mix incompatible generations within one source on resume.
            state.write_text(json.dumps({'source_clip_sha256':key,'backend':'cpu','reason':'public_image_service_unavailable','quality_certified':False}))
    from .local_image import generate_image
    from .environments import REVISION
    namespace='cpu-original-v1-'+REVISION[:12]
    candidate=flux_layers.paint_foreground(plan,out,image_generator=generate_image,namespace=namespace)
    return flux_layers.paint_environments(candidate,out,image_generator=generate_image,namespace=namespace)
