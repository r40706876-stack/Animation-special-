"""Bounded recovery evidence; a fingerprint is never a license or lyric certificate."""
import asyncio,json,subprocess,tempfile
from pathlib import Path

def consistent_matches(results,offsets):
    if len(results)!=2:return None
    tracks=[x.get('track',{}) for x in results]
    matches=[x.get('matches',[]) for x in results]
    if not all(t.get('key') and t.get('title') for t in tracks) or tracks[0]['key']!=tracks[1]['key']:return None
    if not all(m and m[0].get('id')==tracks[i]['key'] for i,m in enumerate(matches)):return None
    try:
        if abs((float(matches[1][0]['offset'])-float(matches[0][0]['offset']))-(offsets[1]-offsets[0]))>.3:return None
    except (KeyError,TypeError,ValueError):return None
    return {'title':tracks[0]['title'],'track_key':tracks[0]['key'],'url':tracks[0].get('url'),'windows':offsets,'lyric_verified':False,'artist_attribution_verified':False}

def recovery_evidence(audio,out,duration):
    out=Path(out);evidence={}
    if duration>=5:
        try:
            from shazamio import Shazam
            offsets=[0,min(3,max(.5,duration-12))]
            async def identify():
                results=[]
                async with Shazam() as client:
                    with tempfile.TemporaryDirectory() as td:
                        for i,offset in enumerate(offsets):
                            p=Path(td)/(str(i)+'.wav')
                            subprocess.run(['ffmpeg','-v','error','-y','-ss',str(offset),'-i',str(audio),'-t','12','-ac','1','-ar','44100',str(p)],check=True,capture_output=True)
                            results.append(await asyncio.wait_for(client.recognize(str(p)),timeout=35))
                return results
            evidence['identity']=consistent_matches(asyncio.run(identify()),offsets)
        except Exception as e:
            evidence['identity_error']=type(e).__name__
    if not evidence.get('identity'):
        try:
            from .analyze import analyze
            folder=out/'independent_asr';folder.mkdir(exist_ok=True)
            evidence['independent_asr']=analyze(audio,folder,'large-v3-turbo')
        except Exception as e:evidence['asr_error']=type(e).__name__
    (out/'audio_recovery.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2))
    return evidence


def independent_audio_text(audio,out,language):
    """Use a second decoder, with a language hint only when explicitly identified."""
    from .analyze import analyze
    hints={'hindi':'hi','urdu':'ur','punjabi':'pa','english':'en','bengali':'bn','marathi':'mr','gujarati':'gu','tamil':'ta','telugu':'te','kannada':'kn','malayalam':'ml','nepali':'ne','spanish':'es','french':'fr','arabic':'ar'}
    hint=hints.get(str(language).strip().lower())
    folder=Path(out)/'independent_verification';folder.mkdir(parents=True,exist_ok=True)
    result=analyze(audio,folder,'large-v3',language_hint=hint)
    return {'status':'available','language_hint':hint,'language':result['language'],'words':result['words'],'note':'ASR is independent evidence, not automatic ground truth. High-confidence verb differences require focused listening.'}
