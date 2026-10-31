"""Resume a validated repair plan only for the exact audio/configuration."""
import hashlib,json
from pathlib import Path
from .vector import validate_vector

def identity(audio,lyrics,engine,artwork,width):
    from .film_standard import fingerprint
    data={'audio_sha256':hashlib.sha256(Path(audio).read_bytes()).hexdigest(),'lyrics':lyrics,'engine':engine,'artwork':artwork,'width':width,'film_standard':fingerprint()}
    return hashlib.sha256(json.dumps(data,sort_keys=True,ensure_ascii=False).encode()).hexdigest()

def save(out,key,plan,pass_index=0,assessment=None,completed=(),pending=False):
    record={'key':key,'plan':plan,'pass_index':pass_index,'assessment':assessment,'completed_shots':list(completed),'pending_repair':pending}
    path=Path(out)/'pipeline_checkpoint.json';temporary=path.with_suffix('.tmp')
    temporary.write_text(json.dumps(record,ensure_ascii=False));temporary.replace(path)

def load(out,key):
    try:
        record=json.loads((Path(out)/'pipeline_checkpoint.json').read_text())
        if record.get('key')!=key:return None
        if type(record.get('pass_index')) is not int or not 0<=record['pass_index']<=2:return None
        validate_vector(record['plan'])
        if type(record.get('pending_repair')) is not bool:return None
        done=record.get('completed_shots')
        if not isinstance(done,list) or any(type(i) is not int or not 0<=i<len(record['plan']['scenes']) for i in done):return None
        if record['pending_repair'] and (not isinstance(record.get('assessment'),dict) or not (Path(out)/'review_contact.jpg').is_file()):return None
        return record
    except (OSError,ValueError,KeyError,TypeError,AttributeError):return None
