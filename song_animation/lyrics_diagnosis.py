"""Independent audio diagnoses; never certify lyrics from a single model."""
import base64,json,os,subprocess
from pathlib import Path
from .provider import generate_json
from .audio_lyrics import LYRICS_SCHEMA
p=Path("song_animation/inputs/ritik_new_song_20261030.mp3")
out=Path("song_diagnosis");out.mkdir(exist_ok=True)
prompt="""Listen carefully to the attached music. The previous transcription incorrectly called it Hindi Bhangra and returned meaningless Roman letters. Ignore that result completely. Identify the real language from the actual voice, including non-Hindi languages. Transcribe only genuinely intelligible audible sung words in the ORIGINAL writing system. If you cannot understand, mark the interval unclear and set uncertain true; never produce pseudo-words or assign a meaning to gibberish. Include all vocal passages, not just the opening. Describe the specific literal lyric meaning in summary only if you can actually understand it. Give 2-6-word phrase segments with approximate actual start/end times. Return the requested schema."""
part={"inline_data":{"mime_type":"audio/mpeg","data":base64.b64encode(p.read_bytes()).decode()}}
try:
    generate_json(prompt,out=out,tag="independent_audio",audio_part=part,schema=LYRICS_SCHEMA,prefer_quality=True)
except Exception as e:
    (out/"audio_error.json").write_text(json.dumps({"error":type(e).__name__}))

print("Audio-only corrected model selection finished",flush=True)
