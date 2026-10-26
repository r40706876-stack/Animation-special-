"""Automated Hindi science documentary shorts; run: python src/documentary.py"""
import asyncio, json, math, os, pathlib, random, re, subprocess, sys
import requests
from PIL import Image, ImageDraw, ImageFont
from planner import _gemini
import io, urllib.parse, time
ROOT=pathlib.Path(__file__).resolve().parent.parent
OUT=ROOT/"videos"; WORK=ROOT/"work"/"documentary"
TOPICS=json.loads((ROOT/"src"/"documentary_topics.json").read_text(encoding="utf-8"))["topics"]
W,H=720,1280
def command(args):
    subprocess.run(args,check=True)
def write_story(topic):
    prompt=("Create an ORIGINAL, fact-checked Hindi science explainer documentary about "+topic["subject"]+". "
      "Audience: curious Hindi speakers, age 12+. 110-145 natural conversational Hindi words. "
      "OPEN within the first 2 seconds with a startling specific question, never greetings or channel introduction. "
      "Build a connected causal story: surprising observation, common misconception, reveal, "
      "three clear mechanisms demonstrated visually, surprising implication and memorable factual ending. "
      "Avoid invented statistics, false certainty, fake experiments and anthropomorphism as fact. "
      "Do not copy either reference video's wording, story or composition. "
      "Return ONLY JSON: title (Hindi), narration (Hindi), scenes (exactly 8 objects). "
      "Each scene must have prompt (English, very specific biological subject or anatomical cross-section, "
      "accurate morphology, precise mechanism, clean educational visual, portrait 9:16, no text), "
      "label (2-5 Hindi words), fact (one short accurate Hindi line), "
      "motion (zoom, panleft, panright or push), visual_type (one of cinematic, diagram, comparison, mechanism), "
      "and beat (one of hook, observation, misconception, reveal, mechanism, consequence, conclusion). "
      "Require at least three diagram/mechanism/comparison scenes; alternate cinematic and explanatory scenes. "
      "In the first scene depict the hook's subject prominently, not an abstract title card. "
      "No copyrighted characters or misleading claims.")
    raw=_gemini(prompt,json_mode=True,temperature=0.65)
    data=json.loads(raw[raw.find("{"):raw.rfind("}")+1])
    if len(data.get("scenes",[]))!=8 or not data.get("narration"): raise ValueError("Invalid storyboard")
    if len(str(data["narration"]).split()) < 65: raise ValueError("Narration too short for documentary")
    kinds=[s.get("visual_type","cinematic") for s in data["scenes"]]
    if sum(t in ("diagram","comparison","mechanism") for t in kinds)<3:
        raise ValueError("Storyboard needs at least three explanatory visual scenes")
    for scene in data["scenes"]:
        if not isinstance(scene,dict) or len(str(scene.get("prompt",""))) < 35:
            raise ValueError("Scene is missing a detailed scientific visual prompt")
    return data
def font(size):
    for p in ["/usr/share/fonts/truetype/noto/NotoSansDevanagari-Bold.ttf",
              "/usr/share/fonts/truetype/noto/NotoSansDevanagari-Regular.ttf"]:
        if pathlib.Path(p).exists(): return ImageFont.truetype(p,size)
    return ImageFont.load_default()
def image_for(scene,idx):
    style=(", crisp educational scientific diagram, readable visual comparison, isolated anatomy, clean ivory background, clear spatial separation, vivid subject colors" if scene.get("visual_type") in ("diagram","comparison","mechanism") else ", cinematic macro natural history photography, anatomically accurate subject, dramatic depth, rich organic detail")
    prompt=scene["prompt"]+style+", vertical 9:16, no text, no typography, no watermark"
    im=None
    for attempt in range(3):
        url="https://image.pollinations.ai/prompt/"+urllib.parse.quote(prompt)+"?width=720&height=1280&nologo=true&seed="+str(9100+idx+attempt*109)+"&model=flux"
        try:
            response=requests.get(url,timeout=90)
            response.raise_for_status()
            if not response.headers.get("content-type","").startswith("image/"): raise ValueError("Non-image response")
            candidate=Image.open(io.BytesIO(response.content)).convert("RGB")
        except (requests.RequestException,ValueError,OSError) as exc:
            print("IMAGE_RETRY",idx,attempt,str(exc)[:150])
            time.sleep(2)
            continue
        if candidate is None:
            continue
        probe=candidate.convert("RGB").resize((32,32))
        pixels=list(probe.getdata())
        spread=sum(max(px)-min(px) for px in pixels)/len(pixels)
        luminance=[sum(px)/3 for px in pixels]
        variance=sum((v-sum(luminance)/len(luminance))**2 for v in luminance)/len(luminance)
        if variance>180 and spread>8:
            im=candidate
            break
        print(f"[image QA] Scene {idx}: low-detail image rejected, attempt {attempt+1}")
    if im is None:
        if os.getenv("ALLOW_PLACEHOLDER_IMAGES","0") != "1":
            raise RuntimeError("Image API failed: refusing to publish placeholder-only documentary")
        print("IMAGE_API_UNAVAILABLE: using explicitly marked procedural backup")
        im=Image.new("RGB",(W,H),(15,28,37))
        d=ImageDraw.Draw(im); rng=random.Random(idx)
        for j in range(85):
            x=rng.randrange(W);y=rng.randrange(H)
            r=rng.randrange(3,45);d.ellipse((x-r,y-r,x+r,y+r),outline=(55,95,100),width=2)
    return im.convert("RGB")
def caption(draw,text,y,fill,fontsize=45):
    f=font(fontsize)
    words=str(text).split();lines=[];line=""
    for word in words:
        test=(line+" "+word).strip()
        if draw.textbbox((0,0),test,font=f)[2]>W-90 and line:
            lines.append(line);line=word
        else:line=test
    if line:lines.append(line)
    for k,s in enumerate(lines[:3]):
        yy=y+k*(fontsize+18)
        box=draw.textbbox((0,0),s,font=f,stroke_width=2)
        x=(W-(box[2]-box[0]))/2
        draw.rounded_rectangle((max(12,x-18),yy-7,min(W-12,x+box[2]-box[0]+18),yy+fontsize+20),radius=14,fill=(7,16,23))
        draw.text((x,yy),s,font=f,fill=fill,stroke_width=1,stroke_fill=(0,0,0))
async def voice(text,path):
    import edge_tts
    await edge_tts.Communicate(text,os.getenv("STORY_VOICE","hi-IN-SwaraNeural"),rate="-5%").save(str(path))
def duration(path):
    return float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","default=nw=1:nk=1",str(path)],text=True).strip())
def render_scene(im,scene,idx,seconds,path):
    # Pre-render static layers and animate continuously using ffmpeg zoompan.
    base=WORK/f"scene_{idx:02}.png"
    canvas=Image.new("RGB",(W,H)); iw,ih=im.size
    scale=max(W/iw,H/ih)*1.16
    im=im.resize((math.ceil(iw*scale),math.ceil(ih*scale)),Image.Resampling.LANCZOS)
    x=(im.width-W)//2;y=(im.height-H)//2
    canvas.paste(im.crop((x,y,x+W,y+H)))
    overlay=Image.new("RGBA",(W,H),(0,0,0,0))
    d=ImageDraw.Draw(overlay)
    d.rectangle((0,0,W,175),fill=(5,13,22,145))
    d.rectangle((0,H-280,W,H),fill=(5,13,22,185))
    # Documentary identity, chapter counter, and a visible progress line.
    d.rounded_rectangle((28,16,245,51),radius=12,fill=(10,31,39,220))
    d.text((43,21),"SCIENCE FILES",font=font(20),fill=(255,221,148))
    d.text((W-100,22),f"{idx+1:02}/08",font=font(24),fill=(255,255,255))
    d.rectangle((0,H-9,round(W*(idx+1)/8),H),fill=(255,194,91))
    caption(d,scene.get("label","रहस्य"),60,(255,218,133),46)
    caption(d,scene.get("fact",""),H-210,(245,246,236),31)
    # Animated infographic: a highlighted subject ring and a directional callout.
    if scene.get("visual_type") in ("diagram","mechanism") or (idx % 3 == 1 and scene.get("visual_type")!="cinematic"):
        cx,cy=W//2,H//2-55
        d.ellipse((cx-150,cy-150,cx+150,cy+150),outline=(255,199,95,230),width=7)
        d.line((cx+110,cy-110,cx+190,cy-200),fill=(255,199,95,240),width=6)
        d.ellipse((cx+184,cy-206,cx+196,cy-194),fill=(255,199,95,255))
    elif scene.get("visual_type")=="comparison" or idx % 3 == 2:
        for j in range(4):
            yline=320+j*120
            d.line((38,yline,W-38,yline),fill=(121,217,216,90),width=2)
        d.rectangle((32,310,W-32,790),outline=(121,217,216,155),width=3)
    canvas=Image.alpha_composite(canvas.convert("RGBA"),overlay).convert("RGB")
    canvas.save(base)
    frames=max(1,round(seconds*24))
    direction=scene.get("motion","zoom")
    if direction=="panleft": xexpr="iw-iw/zoom"
    elif direction=="panright": xexpr="0"
    else:xexpr="(iw-iw/zoom)/2"
    vf=f"zoompan=z='min(zoom+0.00065,1.16)':x='{xexpr}':y='(ih-ih/zoom)/2':d={frames}:s={W}x{H}:fps=24,format=yuv420p"
    # Mild cinematic grade, stable across FFmpeg versions.
    vf += ",eq=contrast=1.05:saturation=1.10"
    if idx % 3 == 2:
        # Independently animated translucent scanner, moving across the anatomy frame.
        scanner=Image.new("RGBA",(W,160),(0,0,0,0))
        sd=ImageDraw.Draw(scanner)
        for yy in range(160):
            strength=max(0,1-abs(yy-80)/80)
            sd.line((0,yy,W,yy),fill=(74,225,223,int(45*strength)))
        sd.line((0,80,W,80),fill=(160,255,244,210),width=5)
        scanfile=WORK/f"scanner_{idx:02}.png"
        scanner.save(scanfile)
        graph=f"[0:v]{vf}[bg];[bg][1:v]overlay=x=0:y='-160+mod(t*260,{H+160})':eval=frame:shortest=1,format=yuv420p[v]"
        args=["ffmpeg","-y","-loglevel","error","-loop","1","-i",str(base),
              "-loop","1","-i",str(scanfile),"-filter_complex",graph,"-map","[v]"]
    else:
        args=["ffmpeg","-y","-loglevel","error","-loop","1","-i",str(base),"-vf",vf]
    command(args+["-frames:v",str(frames),"-c:v","libx264","-preset","ultrafast","-crf","23",str(path)])
def main():
    OUT.mkdir(exist_ok=True);WORK.mkdir(parents=True,exist_ok=True)
    state=ROOT/"documentary_state.json"
    index=json.loads(state.read_text()).get("next",0) if state.exists() else 0
    topic=TOPICS[index%len(TOPICS)]
    data=write_story(topic)
    audio=WORK/"narration.mp3"
    asyncio.run(voice(data["narration"],audio))
    length=duration(audio)
    scenes=data["scenes"]
    # Allocate more screen time to complex captions, instead of equal-length slides.
    weights=[max(8,len(str(s.get("fact","")))+len(str(s.get("label","")))) for s in scenes]
    total_weight=sum(weights)
    clips=[]
    for i,scene in enumerate(scenes):
        im=image_for(scene,i)
        clip=WORK/f"clip_{i:02}.mp4"
        render_scene(im,scene,i,length*weights[i]/total_weight,clip)
        clips.append(clip)
    manifest=WORK/"concat.txt"
    manifest.write_text("".join("file '"+str(p.resolve())+"'\n" for p in clips))
    silent=WORK/"silent.mp4"
    command(["ffmpeg","-y","-loglevel","error","-f","concat","-safe","0","-i",str(manifest),"-c","copy",str(silent)])
    output=OUT/f"SCIENCE_EP_{index+1:03}.mp4"
    command(["ffmpeg","-y","-loglevel","error","-i",str(silent),"-i",str(audio),
             "-map","0:v:0","-map","1:a:0","-c:v","copy","-c:a","aac","-b:a","160k",
             "-t",str(length),"-movflags","+faststart",str(output)])
    # Verify that the encoded output is not empty or truncated.
    actual=duration(output)
    if abs(actual-length)>1.5 or output.stat().st_size<100000:
        raise RuntimeError(f"Video QA failed: expected {length:.1f}s, got {actual:.1f}s")
    (OUT/f"SCIENCE_EP_{index+1:03}.json").write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding="utf-8")
    state.write_text(json.dumps({"next":index+1},indent=2))
    print("SUCCESS",output)
if __name__=="__main__":main()
