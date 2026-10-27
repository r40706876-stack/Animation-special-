"""Free Hindi voice-over and ambient bed for the 30s jewel wasp documentary.
Usage: python src/jewel_wasp_audio.py; writes videos/jewel_audio.m4a.
Fallback ambient is used if free online TTS is temporarily unavailable.
"""
import asyncio, pathlib, subprocess, os
OUT=pathlib.Path("videos");OUT.mkdir(exist_ok=True)
text=("क्या एक छोटी ततैया कॉकरोच के भागने का फैसला बदल सकती है? "
"पहले वह उसके सीने के पास डंक मारती है, जिससे अगले पैर कुछ देर कमजोर पड़ते हैं। "
"फिर दूसरा डंक सिर के पास! ज़हर तंत्रिका तंत्र पर असर डालता है। "
"कॉकरोच चल सकता है, मगर सामान्य तरह से भागता नहीं। "
"अब ज्वेल वास्प उसका एंटीना पकड़कर बिल तक ले जाती है। "
"वहाँ उसके लार्वा को भोजन मिलता है।")
def run(args):subprocess.run(args,check=True)
run(["ffmpeg","-y","-loglevel","error","-f","lavfi","-i",
     "anoisesrc=color=brown:amplitude=0.01:sample_rate=44100:duration=30",
     "-c:a","aac",str(OUT/"jewel_ambient.m4a")])
narration=False
try:
 import edge_tts
 asyncio.run(asyncio.wait_for(edge_tts.Communicate(text,"hi-IN-SwaraNeural",rate="+18%").save(str(OUT/"jewel_narration.mp3")),timeout=65))
 narration=(OUT/"jewel_narration.mp3").stat().st_size>1000
except Exception as exc:
 print("VOICE_PROVIDER_UNAVAILABLE",str(exc)[:160],flush=True)
if narration:
 run(["ffmpeg","-y","-loglevel","error","-i",str(OUT/"jewel_narration.mp3"),
      "-i",str(OUT/"jewel_ambient.m4a"),"-filter_complex",
      "[0:a]volume=1.0,apad=pad_dur=30[voice];[1:a]volume=0.13[bed];[voice][bed]amix=inputs=2:duration=first:dropout_transition=0[a]",
      "-map","[a]","-t","30","-c:a","aac",str(OUT/"jewel_audio.m4a")])
else:
 (OUT/"jewel_audio.m4a").write_bytes((OUT/"jewel_ambient.m4a").read_bytes())
(OUT/"jewel_narration_present.txt").write_text(str(narration).lower())
print("JEWEL_AUDIO_READY narration_present="+str(narration).lower(),flush=True)
