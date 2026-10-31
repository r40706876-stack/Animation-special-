"""One content-independent production standard taken from the approved film."""
import base64,hashlib,json
from pathlib import Path

HERE=Path(__file__).parent

def profile():
    return json.loads((HERE/'production_profile.json').read_text())

def fingerprint():
    p=profile();reference=HERE/'assets'/'quality'/p['reference']
    return hashlib.sha256(json.dumps(p,sort_keys=True).encode()+reference.read_bytes()).hexdigest()

def direction():
    p=profile()
    return p['finish']+'\n'+p['direction']+'\nQUALITY REFERENCE VERSION: '+fingerprint()

def reference_parts():
    p=profile();raw=(HERE/'assets'/'quality'/p['reference']).read_bytes()
    return [{'text':'APPROVED FILM FINISH AND STAGING REFERENCE ONLY. Compare detail, readability, viewpoint and coherent visual progression. Do not copy its people, props, lyrics or plot; use THIS song. This is not an approval of any newly generated artwork.'},
            {'inline_data':{'mime_type':'image/jpeg','data':base64.b64encode(raw).decode()}}]
