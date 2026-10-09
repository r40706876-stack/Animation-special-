"""Katha reel banane wala main script.

Chalane ka tarika:
    python src/main.py                 # audio/ folder ki agli file se video
    python src/main.py audio/xyz.mp3   # koi khaas file

Bani hui video: videos/<audio ka naam>.mp4
Kaam ho chuki audio: purani_audio/ mein chali jaati hai.
"""
import json
import pathlib
import shutil
import sys

from backgrounds import get_backgrounds
from planner import correct_words, make_plan
from render import audio_duration, render_video
from transcribe import transcribe

ROOT = pathlib.Path(__file__).resolve().parent.parent
AUDIO = ROOT / "audio"
DONE = ROOT / "purani_audio"
OUT = ROOT / "videos"
WORK = ROOT / "work"
EXTS = {".mp3", ".wav", ".m4a", ".aac", ".ogg", ".opus", ".mp4"}


def next_audio():
    AUDIO.mkdir(exist_ok=True)
    files = sorted(p for p in AUDIO.iterdir() if p.is_file() and p.suffix.lower() in EXTS)
    return files[0] if files else None


def main():
    audio = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else next_audio()
    if not audio:
        print("audio/ folder khaali hai. Koi nayi audio daalo.")
        return
    print(f"=== {audio.name} ===")
    work = WORK / audio.stem
    work.mkdir(parents=True, exist_ok=True)

    duration = audio_duration(audio)
    words = transcribe(audio)
    if not words:
        raise SystemExit("Audio mein koi shabd nahi mila.")
    (work / "words_raw.json").write_text(json.dumps(words, ensure_ascii=False, indent=1), encoding="utf-8")
    words = correct_words(words)
    (work / "words.json").write_text(json.dumps(words, ensure_ascii=False, indent=1), encoding="utf-8")

    plan = make_plan(words, duration)
    (work / "plan.json").write_text(json.dumps(plan, ensure_ascii=False, indent=1), encoding="utf-8")

    bgs = get_backgrounds(plan, work)
    out = OUT / f"{audio.stem}.mp4"
    render_video(plan, words, bgs, audio, out, work)

    if audio.parent.resolve() == AUDIO.resolve():
        DONE.mkdir(exist_ok=True)
        shutil.move(str(audio), DONE / audio.name)
    print(f"DONE -> {out}")


if __name__ == "__main__":
    main()
