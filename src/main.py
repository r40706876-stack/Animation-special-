"""Katha reel banane wala main script.

Chalane ka tarika:
    python src/main.py                 # audio/ folder ki agli file se video
    python src/main.py audio/xyz.mp3   # koi khaas file

Bani hui video: videos/VIDEO_<date>_<audio ka naam>.mp4 (+ .txt jisme subtitle/scenes)
Kaam ho chuki audio: purani_audio/ mein chali jaati hai.
"""
import json
import pathlib
from datetime import date
import shutil
import sys

from backgrounds import get_backgrounds
from listen import gemini_listen, merge_timing
from planner import check_characters, correct_words, make_plan
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


def report(path, info, words, plan):
    """Video ke saath ek txt: AI ne kya suna aur kya dikhaya (galti pakadne ke liye)."""
    lines = [f"TITLE: {plan.get('title', '')}"]
    if info:
        lines += [f"TYPE: {info.get('type', '')}", f"SUMMARY: {info.get('summary', '')}",
                  f"SPEAKERS: {info.get('speakers', '')}"]
    lines += ["", "=== SUBTITLE (jo suna gaya) ==="]
    cur, start = [], None
    for w in words:
        if start is None:
            start = w["s"]
        cur.append(w["w"])
        if len(cur) >= 8:
            lines.append(f"[{start:5.1f}] " + " ".join(cur))
            cur, start = [], None
    if cur:
        lines.append(f"[{start:5.1f}] " + " ".join(cur))
    lines += ["", "=== SCENES (jo dikhaya gaya) ==="]
    looks = {c["id"]: c.get("look", "") for c in plan.get("characters", [])}
    for sc in plan.get("scenes", []):
        who = ", ".join(f"{a['id']}({a['action']})" for a in sc["actors"]) or "-"
        lines.append(f"[{sc['start']:5.1f}-{sc['end']:5.1f}] bg={sc['bg']} | {who}")
    lines += ["", "=== CHARACTERS ==="] + [f"{k}: {v}" for k, v in looks.items()]
    lines += ["", "=== BACKGROUNDS ==="] + [f"{b['id']}: {b['prompt']}" for b in plan.get("backgrounds", [])]
    path.write_text("\n".join(lines), encoding="utf-8")


def main():
    audio = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else next_audio()
    if not audio:
        print("audio/ folder khaali hai. Koi nayi audio daalo.")
        return
    print(f"=== {audio.name} ===")
    work = WORK / audio.stem
    work.mkdir(parents=True, exist_ok=True)

    duration = audio_duration(audio)
    try:
        whisper_words = transcribe(audio)  # timing ke liye
    except Exception as e:  # noqa: BLE001
        print(f"[whisper] fail ({e}), sirf Gemini se chalayenge")
        whisper_words = []
    (work / "words_whisper.json").write_text(json.dumps(whisper_words, ensure_ascii=False, indent=1), encoding="utf-8")

    info = gemini_listen(audio, duration)  # sahi shabd + audio kya hai
    if info:
        words = merge_timing(info["lines"], whisper_words, duration)
    elif whisper_words:
        print("[main] Gemini audio nahi sun paya, Whisper + spelling sudhaar se chalayenge")
        words = correct_words(whisper_words)
    else:
        raise SystemExit("Audio mein koi shabd nahi mila.")

    plan = make_plan(words, duration, info)
    plan["characters"] = check_characters(plan["characters"])
    (work / "plan.json").write_text(json.dumps(plan, ensure_ascii=False, indent=1), encoding="utf-8")

    bgs = get_backgrounds(plan, work)
    name = f"VIDEO_{date.today():%Y-%m-%d}_{audio.stem}"
    out = OUT / f"{name}.mp4"
    render_video(plan, words, bgs, audio, out, work)
    report(OUT / f"{name}.txt", info, words, plan)

    if audio.parent.resolve() == AUDIO.resolve():
        DONE.mkdir(exist_ok=True)
        shutil.move(str(audio), DONE / audio.name)
    print(f"DONE -> {out}")


if __name__ == "__main__":
    main()
