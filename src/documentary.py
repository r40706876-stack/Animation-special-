"""Automated Hindi science documentary shorts; run: python src/documentary.py"""
import asyncio, json, math, os, pathlib, random, re, subprocess, sys
import requests
from PIL import Image, ImageDraw, ImageFont
from planner import _gemini
from backgrounds import _pollinations
ROOT=pathlib.Path(__file__).resolve().parent.parent
OUT=ROOT/"videos"; WORK=ROOT/"work"/"documentary"
TOPICS=json.loads((ROOT/"src"/"documentary_topics.json").read_text(encoding="utf-8"))["topics"]
W,H=720,1280
def command(args):
    subprocess.run(args,check=True)
def write_story(topic):
    prompt=("Write an ORIGINAL, accurate, suspenseful Hindi nature documentary, 110-145 Hindi words, "
      "about "+topic["subject"]+". Begin with a striking factual hook. Each sentence advances "
      "the story; avoid invented statistics, anthropomorphism as fact, and unverified claims. "
      "End with an intriguing but factual conclusion. Return ONLY JSON with keys "
      "title (Hindi), narration (Hindi), scenes (array of exactly 8 objects, each with "
      "prompt (English, richly detailed scientific natural-history illustration matching the "
      "specific spoken facts, subject clearly visible, cinematic lighting, portrait composition, "
      "no words), label (2-5 Hindi words), motion (one of zoom, panleft, panright, push), "
      "fact (short Hindi factual line)). No copyrighted characters.")
    raw=_gemini(prompt,json_mode=True,temperature=0.65)
    data=json.loads(raw[raw.find("{"):raw.rfind("}")+1])
    if len(data.get("scenes",[]))!=8 or not data.get("narration"): raise ValueError("Invalid storyboard")
    return data
def font(size):
    for p in ["/usr/share/fonts/truetype/noto/NotoSansDevanagari-Bold.ttf",
              "/usr/share/fonts/truetype/noto/NotoSansDevanagari-Regular.ttf"]:
        if pathlib.Path(p).exists(): return ImageFont.truetype(p,size)
    return ImageFont.load_default()
def image_for(scene,idx):
    prompt=scene["prompt"]+", editorial science documentary, accurate anatomy, richly textured engraved illustration, deep teal and warm amber, 9:16, no typography, no watermark"
    im=_pollinations(prompt, 9100+idx)
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
    caption(d,scene.get("label","रहस्य"),60,(255,218,133),46)
    caption(d,scene.get("fact",""),H-210,(245,246,236),31)
    canvas=Image.alpha_composite(canvas.convert("RGBA"),overlay).convert("RGB")
    canvas.save(base)
    frames=max(1,round(seconds*24))
    direction=scene.get("motion","zoom")
    if direction=="panleft": xexpr="iw-iw/zoom"
    elif direction=="panright": xexpr="0"
    else:xexpr="(iw-iw/zoom)/2"
    vf=f"zoompan=z='min(zoom+0.00065,1.16)':x='{xexpr}':y='(ih-ih/zoom)/2':d={frames}:s={W}x{H}:fps=24,format=yuv420p"
    command(["ffmpeg","-y","-loglevel","error","-loop","1","-i",str(base),"-vf",vf,
             "-frames:v",str(frames),"-c:v","libx264","-preset","ultrafast","-crf","23",str(path)])
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
    segment=length/len(scenes)
    clips=[]
    for i,scene in enumerate(scenes):
        im=image_for(scene,i)
        clip=WORK/f"clip_{i:02}.mp4"
        render_scene(im,scene,i,segment,clip)
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
