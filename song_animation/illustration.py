"""Finish one isolated story asset, then judge its actual pixels before film rendering."""
import argparse,base64,copy,hashlib,io,json
from pathlib import Path
from PIL import Image
from .provider import generate_json,ProviderUnavailable
from .vector import raster,sanitize_svg

def part(image):
    buffer=io.BytesIO();image.save(buffer,format='PNG')
    return {'inline_data':{'mime_type':'image/png','data':base64.b64encode(buffer.getvalue()).decode()}}

def illustrate(asset,bible,out):
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    original=raster(asset['svg'],int(asset['width']),int(asset['height']))
    reference=Image.open(Path(__file__).parent/'assets/quality/finish_reference.jpg').convert('RGB')
    prompt='''You are drawing ONE finished isolated illustration asset, not writing a storyboard or rig. The attached first image is a coarse POSE/BLOCKING sketch, not the desired finish. REDRAW this subject with rich organic contours, attractive natural anatomy, expressive features, material modeling, controlled highlights and shadows. A person with a blank oval face is unfinished: draw the actual facial features appropriate to this pose and age. Draw clothing folds, organic hair and articulated fingers where present. Do not add faces to objects. Avoid geometric icon people, triangles for torsos, mitten/banana hands, empty faces and flat single-color fills. The second image is a FINISH benchmark only: match its illustration sophistication, never copy its subject or scenery.
Keep the asset's original local viewBox, approximate pose, facing, contact/attachment positions and outer occupied bounds, so it can replace this specific rig part. A head-only asset stays head-only; a hand-only asset stays hand-only; a whole person stays a whole person. Keep a transparent background. No new scenery, framing cards, captions or extra characters. Use detailed static SVG curves, layered shading and gradients rather than photographic raster images. All artwork must be self-contained SVG. No script, text, images, use, style, filters, external resources, animation or font attributes. Local gradient ids allowed. Return JSON {"svg":"complete standalone SVG"}. Keep SVG under 14000 characters and finish the JSON.
SUBJECT: '''+str(asset.get('description',asset['id']))+'\nLOCAL DIMENSIONS: '+str([asset['width'],asset['height']])+'\nCHARACTER/STYLE BIBLE: '+json.dumps(bible,ensure_ascii=False)+'\nPOSE SVG: '+asset['svg']
    key=hashlib.sha256(prompt.encode()).hexdigest()[:16]
    candidate_path=out/(key+'_candidate.json');notes=[]
    for attempt in range(2):
        if attempt==0 and candidate_path.exists():candidate=json.loads(candidate_path.read_text())
        else:
            result=generate_json(prompt+'\nPREVIOUS VISIBLE PROBLEMS: '+json.dumps(notes),out=out,tag=f'illustration_{attempt}',schema={'type':'OBJECT','properties':{'svg':{'type':'STRING'}},'required':['svg']},extra_parts=[{'text':'POSE SKETCH'},part(original),{'text':'FINISH BENCHMARK'},part(reference)],prefer_quality=True,require_full_model=True,thinking_level='low',max_tokens=16384,timeout_seconds=180)
            svg=result['svg'];sanitize_svg(svg)
            candidate=copy.deepcopy(asset);candidate['svg']=svg
            candidate.pop('raster_png',None);candidate.pop('painted_actor',None)
            candidate_path.write_text(json.dumps(candidate,ensure_ascii=False))
        rendered=raster(candidate['svg'],int(asset['width']),int(asset['height']))
        if rendered.getchannel('A').getbbox() is None:raise ValueError('Illustrator returned an empty asset')
        sheet=Image.new('RGB',(900,600),'#fff8e9')
        for i,image in enumerate([original,rendered,reference]):
            image=image.copy();image.thumbnail((280,560));sheet.paste(image,(i*300+(300-image.width)//2,(600-image.height)//2),image if image.mode=='RGBA' else None)
        sheet.save(out/'comparison.jpg',quality=94)
        rendered.save(out/'finished_asset.png')
        review=generate_json('Judge this isolated asset against the supplied finish reference. Be strict: simple geometric heads/bodies, blank faces and flat icon shapes fail even if coherent. This is asset review only, not film or universal certification. Return JSON {"detail":boolean,"anatomy_or_object_shape":boolean,"subject_and_pose_preserved":boolean,"reference_finish":boolean,"issues":["specific visible defect"]}. Subject: '+str(asset.get('description',asset['id'])),out=out,tag=f'illustration_review_{attempt}',extra_parts=[{'text':'ORIGINAL POSE'},part(original),{'text':'CANDIDATE'},part(rendered),{'text':'FINISH REFERENCE'},part(reference)],prefer_quality=True,require_full_model=True)
        passed=all(review.get(k) is True for k in ('detail','anatomy_or_object_shape','subject_and_pose_preserved','reference_finish')) and review.get('issues')==[]
        (out/'asset_review.json').write_text(json.dumps({'passed':passed,'review':review,'film_quality_certified':False,'universal_quality_certified':False},ensure_ascii=False,indent=2))
        if passed:return candidate
        notes=review.get('issues',[]);candidate_path.unlink(missing_ok=True)
    raise ValueError('Isolated artwork did not meet finish benchmark; expensive film rendering blocked')

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--input',required=True);ap.add_argument('--out',required=True);args=ap.parse_args()
    out=Path(args.out);out.mkdir(parents=True,exist_ok=True)
    try:
        data=json.loads(Path(args.input).read_text());asset=illustrate(data['asset'],data['bible'],out)
        (out/'asset.json').write_text(json.dumps(asset,ensure_ascii=False,indent=2))
        (out/'status.json').write_text(json.dumps({'status':'asset_checks_passed','film_quality_certified':False}))
    except ProviderUnavailable as e:
        (out/'status.json').write_text(json.dumps({'status':'waiting_for_provider','retryable':e.retryable,'retry_after_seconds':e.retry_after_seconds,'blocked_models':e.blocked_models}));raise

if __name__=='__main__':main()
