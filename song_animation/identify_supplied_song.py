import asyncio,json,subprocess
from pathlib import Path
from shazamio import Shazam
async def main():
 out=Path('song_identity');out.mkdir(exist_ok=True)
 async with Shazam() as client:
  for offset in [0,3]:
   p=out/('window_'+str(offset)+'.wav')
   subprocess.run(['ffmpeg','-v','error','-y','-ss',str(offset),'-i','song_animation/inputs/ritik_new_song_20261030.mp3','-t','12','-ac','1','-ar','44100',str(p)],check=True)
   try:
    r=await asyncio.wait_for(client.recognize(str(p)),timeout=50)
    (out/('match_'+str(offset)+'.json')).write_text(json.dumps(r,ensure_ascii=False,indent=2))
    track=r.get('track',{})
    print(json.dumps({'offset':offset,'title':track.get('title'),'artist':track.get('subtitle'),'url':track.get('url')},ensure_ascii=False),flush=True)
   except Exception as e:
    (out/('error_'+str(offset)+'.json')).write_text(json.dumps({'error':type(e).__name__}))
asyncio.run(main())
