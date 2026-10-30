"""Advisory visual review of the actual export samples; not audience certification."""
import base64,json
from pathlib import Path
from .provider import generate_json

def review(plan,out):
    out=Path(out)
    try:
        import io
        from PIL import Image
        from .art import render_frame
        images=[]
        for index,scene in enumerate(plan['scenes']):
            strip=Image.new('RGB',(1620,960))
            for column,q in enumerate((.1,.5,.9)):
                frame=scene['start_frame']+int((scene['end_frame']-scene['start_frame']-1)*q)
                strip.paste(render_frame(plan,frame),(column*540,0))
            buffer=io.BytesIO();strip.save(buffer,format='JPEG',quality=88)
            images.extend([{'text':f'SHOT {index}: left=10%, middle=50%, right=90% of shot time.'},{'inline_data':{'mime_type':'image/jpeg','data':base64.b64encode(buffer.getvalue()).decode()}}])
        from .lyrics import shot_phrases
        descriptions=[{'shot':i,'sung_words':shot_phrases(plan,s),'meaning':s.get('meaning',s.get('label',s.get('reason',''))),'action':s.get('action','')} for i,s in enumerate(plan['scenes'])]
        prompt='''Review the ACTUAL sampled rendered frames of this illustrated song film. Each labelled input image contains three full-size moments from one shot. Compare positions and limb poses across the three panels. Compare recognisable objects/actions FIRST against the actual sung_words and their meaning, then against the proposed action and art bible. A visually successful but lyrically unrelated storyboard is still a failure. Flag missing central objects, absent causes/consequences, repetitive generic standing people and metaphors that reverse the lyric (e.g. thorns causing the wound where the words say flowers caused it). Identify concrete mismatches, blank/poorly composed art, clipping, inconsistent characters, unreadable captions and repeated static compositions. Do not assume a script instruction was rendered successfully. This is advisory AI review, not proof of exact lyric/audio timing, copyright status or viewer retention. Return JSON {"needs_review":true,"issues":[{"shot":0,"issue":"specific visible problem"}],"strengths":["visible strengths"]}. If no concrete issue is visible return issues=[], but never certify human approval or engagement.\nBIBLE: '''+json.dumps(plan.get('bible',{}),ensure_ascii=False)+'\nSHOTS: '+json.dumps(descriptions,ensure_ascii=False)
        result=generate_json(prompt,out=out,tag='visual_review',extra_parts=images)
        result['advisory_only']=True;result['human_approval']=False
    except (RuntimeError,ValueError,KeyError) as e:
        result={'status':'unavailable','error_type':type(e).__name__,'advisory_only':True,'human_approval':False}
    (out/'visual_review.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));return result


def refine(plan,out,assessment):
    """One bounded visual correction pass using actual shot images and review notes."""
    import copy,hashlib,io
    from PIL import Image
    from .generative import scene_package
    out=Path(out);groups={};report=[];candidate=copy.deepcopy(plan)
    for item in assessment.get('issues',[]):
        index=item.get('shot');note=item.get('issue')
        if type(index) is int and 0<=index<len(plan['scenes']) and isinstance(note,str) and note.strip():
            groups.setdefault(index,[]).append(note[:1800])
    contact=Image.open(out/'review_contact.jpg') if groups else None
    for index,notes in list(groups.items())[:3]:
        row=contact.crop((0,index*320,540,(index+1)*320));buf=io.BytesIO();row.save(buf,format='JPEG')
        raw=buf.getvalue();image={'inline_data':{'mime_type':'image/jpeg','data':base64.b64encode(raw).decode()}}
        candidate['scenes'][index]['visual_correction']={
            'issues':notes,'reference_sha256':hashlib.sha256(raw).hexdigest(),
            'instruction':'Correct the VISIBLE mistakes in the attached three frames. Preserve lyric timing and character identity. Missing people must be drawn and visible. Walking requires visible legs/feet, a clear change of position and alternating leg poses. Keep body parts attached. Show the described action through distinct start, middle and end poses; camera or particles alone cannot replace it. Keep main action above y=750. Return a complete corrected scene package.'}
        try:
            scene,assets=scene_package(candidate,index,out,candidate['assets'],reference_image=image)
            candidate['scenes'][index]=scene;candidate['assets']=assets
            from .choreography import retarget
            candidate,rigged=retarget(candidate,index,notes)
            report.append({'shot':index,'status':'replaced','connected_rig':rigged,'issues':notes})
        except (ValueError,RuntimeError,KeyError,TypeError) as e:
            candidate['scenes'][index]=copy.deepcopy(plan['scenes'][index])
            report.append({'shot':index,'status':'failed','error':str(e)[:1200]})
    (out/'visual_repair.json').write_text(json.dumps({'pass_limit':1,'scene_limit':3,'results':report},ensure_ascii=False,indent=2))
    return candidate,any(x['status']=='replaced' for x in report)
