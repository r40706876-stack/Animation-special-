"""Gemini audio sunta hai (sahi shabd + kya ho raha hai), Whisper sirf timing deta hai."""
import base64
import json
import re
import subprocess
import tempfile

from planner import _gemini

LISTEN_PROMPT = """Is audio ko shuru se aakhir tak dhyan se suno (peeche music ho sakta hai, use chhod do, sirf boli likho).
Audio ki lambai {dur:.1f} second hai.

Sirf JSON lautao:
{{
  "type": "<stand-up comedy | comedy sketch | katha | kahani | itihaas | jaankari | motivational | gaana | aur kuch>",
  "summary": "<Hindi mein 2-3 line: kaun bol raha hai, kis baare mein, joke/kahani kya hai, aur MAHAUL kaisa hai (jaise: modern city, office, gaon, mandir, comedy stage)>",
  "speakers": "<kitne log bol rahe, kaise hain, jaise 'ek comedian stage par'>",
  "lines": [
    {{"start": 0.0, "end": 2.5, "text": "<bilkul wahi shabd jo bole gaye>"}}
  ]
}}

NIYAM:
- text bilkul wahi likho jo bola gaya hai, apni taraf se kuch mat jodo, matlab mat badlo. Devanagari mein, angrezi shabd bhi Devanagari mein. Punctuation nahi.
- Har line 3 se 8 shabd ki ho. Poori audio cover karo, beech ka koi hissa mat chhodo.
- start/end seconds mein, jitna sahi ho sake.
- Jo samajh na aaye use chhod do, andaaza mat lagao.
"""

def _to_small_mp3(audio_path):
    tmp = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
    tmp.close()
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(audio_path),
                    "-vn", "-ac", "1", "-ar", "22050", "-b:a", "64k", tmp.name], check=True)
    return tmp.name

def gemini_listen(audio_path, duration):
    """Lautata hai dict(type, summary, speakers, lines) ya None."""
    mp3 = _to_small_mp3(audio_path)
    data = base64.b64encode(open(mp3, "rb").read()).decode()
    part = {"inline_data": {"mime_type": "audio/mp3", "data": data}}
    for attempt in range(2):
        try:
            raw = _gemini(LISTEN_PROMPT.format(dur=duration), json_mode=True, temperature=0.1, extra_parts=[part])
            res = json.loads(raw[raw.find("{"): raw.rfind("}") + 1])
        except Exception as e:
            print(f"[listen] Gemini audio nahi sun paya ({e})")
            continue
        lines = []
        for ln in res.get("lines", []):
            text = re.sub(r"[।,.!?;:\"'…]", " ", str(ln.get("text", ""))).split()
            try:
                s, e = float(ln.get("start", 0)), float(ln.get("end", 0))
            except (TypeError, ValueError):
                continue
            if text and 0 <= s < duration:
                lines.append({"start": s, "end": min(max(e, s + 0.3), duration), "words": text})
        if len(lines) >= 2:
            res["lines"] = sorted(lines, key=lambda x: x["start"])
            n = sum(len(l["words"]) for l in lines)
            print(f"[listen] {res.get('type')} | {len(lines)} lines, {n} shabd")
            print(f"[listen] summary: {res.get('summary', '')[:200]}")
            return res
        print("[listen] Gemini ne lines nahi di, dobara")
    return None

def merge_timing(lines, whisper_words, duration):
    """Gemini ke sahi shabd + Whisper ki timing. Har line ka start/end Whisper ke paas wale shabdon se sudhaaro."""
    out = []
    for i, ln in enumerate(lines):
        s, e = ln["start"], ln["end"]
        near = [w for w in whisper_words if w["s"] < e + 0.6 and w["e"] > s - 0.6]
        if near:
            s2, e2 = min(w["s"] for w in near), max(w["e"] for w in near)
            if abs(s2 - s) < 1.5:
                s = s2
            if abs(e2 - e) < 1.5:
                e = e2
        if out and s < out[-1]["e"]:
            s = out[-1]["e"]
        nxt = lines[i + 1]["start"] if i + 1 < len(lines) else duration
        e = max(min(e, nxt if nxt > s + 0.3 else e), s + 0.3)
        words = ln["words"]
        total = sum(len(w) for w in words) or 1
        t = s
        for w in words:
            d = (e - s) * len(w) / total
            out.append({"w": w, "s": round(t, 2), "e": round(t + d, 2)})
            t += d
    return out
