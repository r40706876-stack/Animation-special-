"""Advisory visual review of the actual export samples; not audience certification."""
import base64,json
from pathlib import Path
from .provider import generate_json

def review(plan,out):
    out=Path(out)
    try:
        image={'inline_data':{'mime_type':'image/jpeg','data':base64.b64encode((out/'review_contact.jpg').read_bytes()).decode()}}
        descriptions=[{'shot':i,'meaning':s.get('label',s.get('reason','')),'action':s.get('action','')} for i,s in enumerate(plan['scenes'])]
        prompt='''Review the ACTUAL sampled rendered frames of this illustrated song film. Each row contains three moments from one shot. Compare recognisable objects/actions against the shot descriptions and shared art bible. Identify concrete mismatches, blank/poorly composed art, clipping, inconsistent characters, unreadable captions and repeated static compositions. Do not assume a script instruction was rendered successfully. This is advisory AI review, not proof of exact lyric/audio timing, copyright status or viewer retention. Return JSON {"needs_review":true,"issues":[{"shot":0,"issue":"specific visible problem"}],"strengths":["visible strengths"]}. If no concrete issue is visible return issues=[], but never certify human approval or engagement.\nBIBLE: '''+json.dumps(plan.get('bible',{}),ensure_ascii=False)+'\nSHOTS: '+json.dumps(descriptions,ensure_ascii=False)
        result=generate_json(prompt,out=out,tag='visual_review',extra_parts=[image])
        result['advisory_only']=True;result['human_approval']=False
    except (RuntimeError,ValueError,KeyError) as e:
        result={'status':'unavailable','error_type':type(e).__name__,'advisory_only':True,'human_approval':False}
    (out/'visual_review.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));return result
