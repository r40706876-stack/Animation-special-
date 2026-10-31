"""Advisory visual review of the actual export samples; not audience certification."""
import base64,json,subprocess,io
from pathlib import Path
from .provider import generate_json,ProviderUnavailable

def encoded_sample(video,seconds):
    from PIL import Image
    raw=subprocess.check_output(['ffmpeg','-v','error','-ss',str(max(0,seconds)),'-i',str(video),'-frames:v','1','-vf','scale=540:960','-f','image2pipe','-vcodec','png','-'],timeout=25)
    im=Image.open(io.BytesIO(raw));im.load();return im.convert('RGB')

def review(plan,out):
    out=Path(out)
    measured=None
    try:
        import io
        from PIL import Image
        images=[];samples=[];contact=Image.new('RGB',(540,320*len(plan['scenes'])))
        for index,scene in enumerate(plan['scenes']):
            strip=Image.new('RGB',(1620,960))
            shot_samples=[]
            for column,q in enumerate((.1,.5,.9)):
                frame=scene['start_frame']+int((scene['end_frame']-scene['start_frame']-1)*q)
                sample=encoded_sample(out/'preview.mp4',frame/plan['fps']);shot_samples.append(sample)
                strip.paste(sample,(column*540,0))
            samples.append(shot_samples)
            contact.paste(strip.resize((540,320)),(0,index*320))
            buffer=io.BytesIO();strip.save(buffer,format='JPEG',quality=88)
            images.extend([{'text':f'SHOT {index}: left=10%, middle=50%, right=90% of shot time.'},{'inline_data':{'mime_type':'image/jpeg','data':base64.b64encode(buffer.getvalue()).decode()}}])
        contact.save(out/'review_contact.jpg',quality=90)
        from .variety import measure
        measured=measure(samples,plan['scenes'],plan['fps'])
        (out/'visual_variety.json').write_text(json.dumps(measured,indent=2))
        benchmark=Path(__file__).parent/'assets'/'quality'/'finish_reference.jpg'
        if not benchmark.is_file():raise RuntimeError('Stored finish reference is missing')
        images.extend([{'text':'FINISH REFERENCE ONLY: the next image shows the required illustration detail and readability. Do NOT borrow its objects or story; select subjects from the actual song. Compare the film against this finish, rather than rewarding any internally consistent simple geometric style.'},{'inline_data':{'mime_type':'image/jpeg','data':base64.b64encode(benchmark.read_bytes()).decode()}}])
        from .lyrics import shot_phrases
        descriptions=[{'shot':i,'sung_words':shot_phrases(plan,s),'meaning':s.get('meaning',s.get('label',s.get('reason',''))),'action':s.get('action',''),'story':s.get('story')} for i,s in enumerate(plan['scenes'])]
        prompt='''Review the ACTUAL decoded MP4 frames of this illustrated song film. Each labelled input image contains three full-size moments from one shot. Compare positions and limb poses across the three panels. Evaluate the connected story across ALL shots, not a list of noun matches. Check who/what the viewer follows, the desire or relationship, visible event/choice, carried consequence and earned final gesture. Judge whether each shot makes the next matter emotionally, and whether prior physical/relationship states persist. The emotional meaning of sung_words must remain faithful, but a creative narrative need not literally illustrate every noun. Reject individually pretty but disconnected pictures, unexplained prop/identity/state resets and repeated portraits with no developing relationship. A visually successful but lyrically unrelated storyboard is still a failure. Flag missing central objects, absent causes/consequences, repetitive generic standing people and metaphors that reverse the lyric (e.g. thorns causing the wound where the words say flowers caused it). Identify concrete mismatches, blank/poorly composed art, clipping, inconsistent characters, unreadable captions and repeated static compositions. Do not assume a script instruction was rendered successfully. This is advisory AI review, not proof of exact lyric/audio timing, copyright status or viewer retention. Check VISUAL VARIETY across the actual decoded panels: for five or more shots require at least THREE distinct staged setups, including different blocking/interactions and meaningfully different compositions. Crops, camera pans/zooms, color changes, or new words drawn on the same desk are still ONE visual. Variety must remain causally connected; arbitrary new locations fail story continuity. Return JSON with lyric_story_connection:boolean, visual_variety:boolean, story_arc:boolean (coherent emotional progression and earned ending), story_links:[{from:0,to:1,causal_connection:boolean,state_continuity:boolean,emotional_progression:boolean,reason:"actual visible transition evidence"}] (EVERY adjacent shot pair, empty for one shot), reference_quality_met:boolean (true only when the actual film matches the supplied illustration finish/detail/readability), needs_review:boolean, issues:[{shot:0,issue:"specific visible problem"}], strengths:["visible strengths"], and shots:[{shot:0,lyric_meaning:boolean,artwork_detail:boolean,story_motion:boolean,narrative_advance:boolean,anatomy_continuity:boolean,caption_legibility:boolean,reason:"visible evidence"}]. Review EVERY shot exactly once. All six checks must be explicitly true to clear a shot. Artwork_detail requires finished attractive organic illustration at phone size, not rough geometric people, icons or placeholders. Story_motion requires a visible meaningful action/change, not only camera pans, particles or a wobbling still picture. Judge the actual images, not promises in the plan. Missing/ambiguous evidence is false. If no issue is visible return needs_review=false and issues=[], but never certify human approval, exact lyric timing or engagement.\nBIBLE: '''+json.dumps(plan.get('bible',{}),ensure_ascii=False)+'\nCONNECTED STORY: '+json.dumps(plan.get('story',{}),ensure_ascii=False)+'\nSHOTS: '+json.dumps(descriptions,ensure_ascii=False)
        prompt+='\nADDITIONAL REQUIRED CHECKS: Return lyric_story_connection:boolean for whether the overall story expresses THIS song, and narrative_advance:boolean inside EVERY shot for an actual visible event/reaction/consequence advancing the carried story. A pretty still portrait, a new camera crop, a decorative particle, or a new noun illustration alone is false. All SIX per-shot checks must pass.\nDECODED VISUAL-VARIETY MEASUREMENT: '+json.dumps(measured)
        result=generate_json(prompt,out=out,tag='visual_review',extra_parts=images,prefer_quality=True,require_full_model=True)
        result['reviewer_model']=result.pop('_provider_model',None)
        result['advisory_only']=True;result['human_approval']=False
    except ProviderUnavailable as e:
        result={'status':'unavailable','provider_wait':True,'retry_after_seconds':e.retry_after_seconds,'advisory_only':True,'human_approval':False}
    except (RuntimeError,ValueError,KeyError,OSError,subprocess.SubprocessError) as e:
        result={'status':'unavailable','error_type':type(e).__name__,'advisory_only':True,'human_approval':False}
    # This field always comes from decoded frames, never from model assertions.
    result['visual_variety_measurement']=measured
    (out/'visual_review.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));return result


def refine(plan,out,assessment,pass_index=1,scene_limit=6):
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
    for index,notes in list(groups.items())[:scene_limit]:
        row=contact.crop((0,index*320,540,(index+1)*320));buf=io.BytesIO();row.save(buf,format='JPEG')
        raw=buf.getvalue();image={'inline_data':{'mime_type':'image/jpeg','data':base64.b64encode(raw).decode()}}
        candidate['scenes'][index]['visual_correction']={
            'issues':notes,'reference_sha256':hashlib.sha256(raw).hexdigest(),
            'instruction':'Correct the VISIBLE mistakes in the attached three frames. Preserve lyric timing, character identity and the connected story. Keep this shot state_in consistent with the preceding shot state_out, and deliver the planned consequence for the next shot. Do not fix a shot by inventing an unrelated prop, scene or character. Missing people must be drawn and visible. Walking requires visible legs/feet, a clear change of position and alternating leg poses. Keep body parts attached. Show the described action through distinct start, middle and end poses; camera or particles alone cannot replace it. Keep main action above y=750. Return a complete corrected scene package.'}
        try:
            scene,assets=scene_package(candidate,index,out,candidate['assets'],reference_image=image)
            candidate['scenes'][index]=scene;candidate['assets']=assets
            from .choreography import retarget
            candidate,rigged=retarget(candidate,index,notes)
            report.append({'shot':index,'status':'replaced','connected_rig':rigged,'issues':notes})
        except (ValueError,RuntimeError,KeyError,TypeError) as e:
            candidate['scenes'][index]=copy.deepcopy(plan['scenes'][index])
            report.append({'shot':index,'status':'failed','error':str(e)[:1200]})
    (out/f'visual_repair_{pass_index}.json').write_text(json.dumps({'pass_limit':2,'pass':pass_index,'scene_limit':scene_limit,'results':report},ensure_ascii=False,indent=2))
    (out/'visual_repair.json').write_text((out/f'visual_repair_{pass_index}.json').read_text())
    return candidate,any(x['status']=='replaced' for x in report)
