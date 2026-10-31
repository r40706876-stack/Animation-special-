"""Measure repetitive visual setups in decoded video, with captions excluded.

This is a conservative similarity heuristic, not a semantic story certificate.
It must pass alongside the full-model lyric, causal-story and artwork reviews.
"""
import numpy as np
from PIL import Image

SIMILARITY=.97

def signatures(image):
    im=image.convert('RGB');w,h=im.size
    # Captions live below the scene action; changing subtitles cannot create cuts.
    # Two-line captions can begin at y=732 in the 960px canvas.
    im=im.crop((round(w*.025),round(h*.035),round(w*.975),round(h*.75)))
    w,h=im.size;result=[]
    for scale in (1,.92,.84):
        dx=(1-scale)*w/2;dy=(1-scale)*h/2
        a=np.asarray(im.crop((dx,dy,w-dx,h-dy)).resize((24,36),Image.Resampling.BILINEAR),dtype=float)/255
        rgb=a.ravel();rgb=rgb/max(1e-9,np.linalg.norm(rgb))
        gray=a@np.array([.299,.587,.114]);flat=float(gray.std())<.012
        structure=(gray-gray.mean()).ravel();structure=structure/max(1e-9,np.linalg.norm(structure))
        result.append((rgb,structure,flat))
    return result

def similarity(a,b):
    score=-1
    for rgb_a,shape_a,flat_a in a:
        for rgb_b,shape_b,flat_b in b:
            if flat_a and flat_b:return 1.
            value=float(np.dot(rgb_a,rgb_b))
            if not flat_a and not flat_b:value=max(value,float(np.dot(shape_a,shape_b)))
            score=max(score,value)
    return score

def measure(samples,scenes,fps):
    if len(samples)!=len(scenes) or not samples or any(len(s)!=3 for s in samples):raise ValueError('Need three decoded moments from every shot')
    features=[[signatures(im) for im in shot] for shot in samples]
    count=len(scenes);scores=np.eye(count);groups=[];membership=[]
    for i in range(count):
        for j in range(i):
            # Median over the nine comparisons tolerates motion within one setup.
            scores[i,j]=scores[j,i]=float(np.median([similarity(a,b) for a in features[i] for b in features[j]]))
        for g,members in enumerate(groups):
            # Complete-link grouping avoids collapsing a gradual sequence merely
            # because neighbouring pictures each resemble the next one.
            if all(scores[i,j]>=SIMILARITY for j in members):members.append(i);membership.append(g);break
        else:membership.append(len(groups));groups.append([i])
    duration=scenes[-1]['end_frame']/fps
    required=3 if duration>=20 else 2 if duration>=8 else 1
    repeat=0.;max_repeat=0.;last=None;run=[];long_runs=[]
    for i,s in enumerate(scenes):
        seconds=(s['end_frame']-s['start_frame'])/fps
        if membership[i]!=last:
            if repeat>8.1:long_runs.extend(run[1:] or run)
            repeat=0.;run=[]
        repeat+=seconds;run.append(i);last=membership[i];max_repeat=max(max_repeat,repeat)
    if repeat>8.1:long_runs.extend(run[1:] or run)
    reasons=[]
    if len(groups)<required:reasons.append('Too few distinct visual setups in actual encoded frames')
    if duration>=8 and max_repeat>8.1:reasons.append('One visual setup continues for over eight seconds across cuts')
    repeated=[i for group in groups for i in group[1:]]
    targets=sorted(set(long_runs+(repeated if len(groups)<required else []))) if reasons else []
    return {'source':'decoded_mp4','passed':not reasons,'sampled_shots':count,'sample_count':3*count,
        'required_groups':required,'observed_groups':len(groups),'groups':groups,
        'max_same_setup_seconds':round(max_repeat,3),'similarity_threshold':SIMILARITY,
        'reasons':reasons,'repair_shots':targets or (list(range(count)) if reasons else []),
        'semantic_quality_certified':False}

def decision(report,scene_count):
    if report is None and scene_count==1:return [],[]
    valid=isinstance(report,dict) and report.get('source')=='decoded_mp4' and report.get('sampled_shots')==scene_count and report.get('sample_count')==scene_count*3
    if not valid:
        note='Missing complete decoded-frame visual-variety evidence'
        return [note],[{'shot':i,'issue':note} for i in range(scene_count)]
    if report.get('passed') is True and type(report.get('required_groups')) is int and type(report.get('observed_groups')) is int and 1<=report['required_groups']<=report['observed_groups']<=scene_count:return [],[]
    note='Actual frames repeat the same visual setup; change story staging and action, not captions, colours or a small zoom.'
    targets=report.get('repair_shots',list(range(scene_count)))
    targets=[i for i in targets if type(i) is int and 0<=i<scene_count]
    return [note],[{'shot':i,'issue':note} for i in targets or range(scene_count)]
