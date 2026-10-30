"""Explicit output gates. Passing automated checks is not universal/human approval."""
import json,subprocess,math,hashlib
from pathlib import Path
from .narrative import narrative_decision
import numpy as np
CHECKS=('lyric_meaning','artwork_detail','story_motion','anatomy_continuity','caption_legibility')
class QualityHold(RuntimeError):pass

def visual_decision(review,scene_count):
    reasons=[];repair=[]
    if not isinstance(review,dict):return {'passed':False,'reasons':['No visual assessment'],'repair_issues':[]}
    if review.get('status')=='unavailable':reasons.append('Visual review unavailable')
    if review.get('needs_review') is not False:reasons.append('Review did not explicitly clear the film')
    if not isinstance(review.get('issues'),list):reasons.append('Missing issue list')
    elif review['issues']:
        reasons.append('Unresolved visual issues')
        for issue in review['issues']:
            if isinstance(issue,dict) and type(issue.get('shot')) is int and isinstance(issue.get('issue'),str):repair.append(issue)
    model=review.get('reviewer_model')
    if not isinstance(model,str) or not model or 'lite' in model.lower():
        reasons.append('Full-capability visual reviewer did not verify this film')
        return {'passed':False,'reasons':reasons,'repair_issues':[]}
    story_reasons,story_repairs=narrative_decision(review,scene_count)
    reasons.extend(story_reasons);repair.extend(story_repairs)
    if review.get('reference_quality_met') is not True:
        reasons.append('Artwork did not meet the stored finish reference')
        repair.extend({'shot':i,'issue':'Artwork is below the stored finish reference. Redraw large detailed organic objects with legible bright composition, not placeholder geometric shapes.'} for i in range(scene_count))
    shots=review.get('shots')
    if not isinstance(shots,list) or len(shots)!=scene_count:
        reasons.append('Missing complete per-shot visual evidence')
    else:
        seen=set()
        for shot in shots:
            i=shot.get('shot') if isinstance(shot,dict) else None
            if type(i) is not int or not 0<=i<scene_count or i in seen:
                reasons.append('Invalid or repeated shot review');continue
            seen.add(i)
            for check in CHECKS:
                if shot.get(check) is not True:
                    note=f'{check} did not pass for shot {i}'
                    reasons.append(note);repair.append({'shot':i,'issue':note+': '+str(shot.get('reason','No explanation'))[:1400]})
    return {'passed':not reasons,'reasons':reasons,'repair_issues':repair}

def inspect_export(video,audio,plan,width):
    """Check actual encoded stream, complete decoding, timing and source audio."""
    video=Path(video)
    if not video.is_file():return {'passed':False,'reasons':['No encoded video']}
    reasons=[];data={}
    try:
        meta=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(video)]))
        v=next(s for s in meta['streams'] if s['codec_type']=='video')
        a=next(s for s in meta['streams'] if s['codec_type']=='audio')
        target=plan['total_frames']/plan['fps'];actual=float(meta['format']['duration'])
        data={'duration':actual,'width':v['width'],'height':v['height'],'video_codec':v['codec_name'],'audio_codec':a['codec_name']}
        if v['codec_name']!='h264' or v.get('pix_fmt')!='yuv420p' or a['codec_name']!='aac':reasons.append('Unsupported playback codec')
        if v['width']!=width or abs(v['height']-width*16/9)>2:reasons.append('Wrong output size')
        if not math.isfinite(actual) or abs(actual-target)>.12 or actual>30.12:reasons.append('Wrong clip duration')
        subprocess.run(['ffmpeg','-v','error','-xerror','-i',str(video),'-f','null','-'],check=True,capture_output=True,timeout=90)
        def pcm(p):
            return np.frombuffer(subprocess.check_output(['ffmpeg','-v','error','-i',str(p),'-vn','-ac','1','-ar','8000','-f','f32le','-']),dtype='<f4')
        source=pcm(audio);encoded=pcm(video);n=min(len(source),len(encoded))
        if abs(len(source)-len(encoded))/8000>.12:reasons.append('Audio duration changed')
        source=source[:n].astype(float);encoded=encoded[:n].astype(float)
        if n==0:reasons.append('Missing decoded audio')
        elif np.dot(source,source)>1e-8:
            correlation=float(np.dot(source,encoded)/max(1e-12,np.linalg.norm(source)*np.linalg.norm(encoded)))
            data['source_audio_correlation']=round(correlation,5)
            if not math.isfinite(correlation) or correlation<.9:reasons.append('Export audio does not match original clip')
    except (OSError,ValueError,KeyError,StopIteration,subprocess.SubprocessError) as e:
        reasons.append('Export validation failed: '+type(e).__name__)
    if not reasons:
        data['video_sha256']=hashlib.sha256(video.read_bytes()).hexdigest()
        data['source_clip_sha256']=hashlib.sha256(Path(audio).read_bytes()).hexdigest()
    return dict(data,passed=not reasons,reasons=reasons)
