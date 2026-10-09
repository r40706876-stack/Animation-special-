"""Transcript -> scene plan + unique SVG characters, using the free Gemini API."""
import json
import os
import re
import time
import xml.etree.ElementTree as ET

import requests

API = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"

ACTIONS = ["idle", "talk", "walk", "jump", "shake", "glow", "bow", "eat", "rise", "sit"]
ENTERS = ["none", "left", "right", "pop", "fade", "top"]
EXITS = ["none", "left", "right", "fade", "up"]
EMOTES = ["none", "heart", "sparkle", "surprise", "anger", "sweat", "tears", "question"]


# ---------------------------------------------------------------- Gemini call
def _gemini(prompt, json_mode=False, temperature=0.8):
    key = os.environ.get("GEMINI_API_KEY")
    if not key:
        raise SystemExit("GEMINI_API_KEY nahi mila. GitHub repo Settings > Secrets mein daalo.")
    model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    body = {
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": temperature},
    }
    if json_mode:
        body["generationConfig"]["responseMimeType"] = "application/json"
    last = None
    for attempt in range(5):
        try:
            r = requests.post(API.format(model=model), params={"key": key}, json=body, timeout=180)
            if r.status_code == 429 or r.status_code >= 500:
                last = f"HTTP {r.status_code}: {r.text[:200]}"
                wait = 20 * (attempt + 1)
                print(f"[gemini] {last} -> {wait}s ruk ke dobara")
                time.sleep(wait)
                continue
            r.raise_for_status()
            data = r.json()
            return "".join(p.get("text", "") for p in data["candidates"][0]["content"]["parts"])
        except (requests.RequestException, KeyError, IndexError) as e:
            last = str(e)
            time.sleep(10 * (attempt + 1))
    raise RuntimeError(f"Gemini fail: {last}")


# ---------------------------------------------------------------- plan
PLAN_PROMPT = """Tum ek animation director ho. Neeche ek Hindi katha (dharmik kahani) ka audio transcript hai,
har line ke aage uska start time (seconds) hai. Is audio ke upar 9:16 vertical 2D cartoon animation banana hai.
Jo shabd bola ja raha ho, wahi screen par dikhna chahiye.

TRANSCRIPT (total {dur:.1f} seconds):
{lines}

Sirf JSON lauto, is format mein:
{{
  "title": "कथा • <chhota hindi naam>",
  "backgrounds": [
    {{"id": "bg1", "prompt": "<ENGLISH description of an empty scene, no people, no animals, no text>"}}
  ],
  "characters": [
    {{"id": "bhola", "kind": "person|animal|god|demon|object",
      "look": "<ENGLISH visual description: age, clothes, colours, key features>"}}
  ],
  "scenes": [
    {{"start": 0.0, "bg": "bg1",
      "actors": [
        {{"id": "bhola", "x": 0.35, "y": 0.82, "size": 0.38, "flip": false,
          "enter": "none", "exit": "none", "action": "talk", "emote": "none"}}
      ]}}
  ]
}}

NIYAM:
- backgrounds: 2 se 5. Har prompt mein sirf jagah ho (gaon, khet, jungle, kuan, mandir, raat, mahal, aasmaan...). Koi insaan/janwar nahi.
- characters: kahani ke saare zaroori log, janwar aur khaas cheezein (jaise khichdi ki katori, deepak, bansuri). 2 se 8. id chhote english shabd.
- scenes: har 3-7 second par naya scene, jab kahani mein kuch naya ho. start time transcript ke time se milao. Pehla scene 0.0 se.
- Har scene mein 1-4 actors. x = 0.1 se 0.9 (screen ki chaudai ka hissa, actor ka beech). y = pairon ki line (0.75-0.88 zameen; aasmaan wali cheez 0.4-0.6). size = screen ki oonchai ka hissa (insaan 0.30-0.42, janwar 0.15-0.25, cheez 0.06-0.12, rakshas/bhagwan 0.5-0.65).
- Sab characters default mein DAAYEIN (right) dekhte hain. flip:true = baayein dekhe.
- enter: {enters}. exit: {exits}.
- action: {actions}.
- emote (sir ke upar): {emotes}.
- Jab koi naya character pehli baar kahani mein aaye, us scene mein uska enter "left"/"right"/"pop"/"top" rakho.
- Actors aapas mein overlap na karein.
"""


def _transcript_lines(words, gap=0.6, max_words=12):
    lines, cur = [], []
    for w in words:
        if cur and (w["s"] - cur[-1]["e"] > gap or len(cur) >= max_words):
            lines.append(cur)
            cur = []
        cur.append(w)
    if cur:
        lines.append(cur)
    return "\n".join(f"[{l[0]['s']:.1f}] " + " ".join(x["w"] for x in l) for l in lines)


def _clean_plan(plan, duration):
    chars = {c["id"]: c for c in plan.get("characters", []) if c.get("id")}
    bgs = [b for b in plan.get("backgrounds", []) if b.get("id")] or [
        {"id": "bg1", "prompt": "peaceful indian village at golden hour, banyan tree, mud houses"}
    ]
    bg_ids = {b["id"] for b in bgs}
    scenes = []
    for s in sorted(plan.get("scenes", []), key=lambda s: float(s.get("start", 0))):
        st = max(0.0, min(float(s.get("start", 0)), duration - 0.5))
        actors = []
        for a in s.get("actors", []):
            if a.get("id") not in chars:
                continue
            actors.append({
                "id": a["id"],
                "x": min(0.92, max(0.08, float(a.get("x", 0.5)))),
                "y": min(0.95, max(0.25, float(a.get("y", 0.82)))),
                "size": min(0.7, max(0.05, float(a.get("size", 0.35)))),
                "flip": bool(a.get("flip", False)),
                "enter": a.get("enter") if a.get("enter") in ENTERS else "none",
                "exit": a.get("exit") if a.get("exit") in EXITS else "none",
                "action": a.get("action") if a.get("action") in ACTIONS else "idle",
                "emote": a.get("emote") if a.get("emote") in EMOTES else "none",
            })
        scenes.append({"start": st, "bg": s.get("bg") if s.get("bg") in bg_ids else bgs[0]["id"], "actors": actors[:5]})
    if not scenes or scenes[0]["start"] > 0.01:
        scenes.insert(0, {"start": 0.0, "bg": bgs[0]["id"], "actors": []})
    # remove scenes that start at the same time
    dedup = []
    for s in scenes:
        if dedup and s["start"] - dedup[-1]["start"] < 0.8:
            if s["actors"]:  # bahut paas wala scene: purane ki jagah naya, start purana
                dedup[-1].update(bg=s["bg"], actors=s["actors"])
        else:
            dedup.append(s)
    for i, s in enumerate(dedup):
        s["end"] = dedup[i + 1]["start"] if i + 1 < len(dedup) else duration
    plan["characters"] = list(chars.values())
    plan["backgrounds"] = bgs
    plan["scenes"] = dedup
    plan["title"] = plan.get("title") or "कथा"
    return plan


# ---------------------------------------------------------------- characters
SVG_PROMPT = """Ek single SVG banao: {kind} character for an Indian devotional 2D cartoon story.
Look: {look}

ZAROORI:
- <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 300"> ... </svg>
- Pura shareer (full body) dikhe, side-3/4 view, chehra DAAYEIN (right) taraf. Pair bilkul neeche y=300 ko chhuen.{obj_note}
- Flat 2D vector cartoon style: saaf moti shapes, garam rang, halki shading (ek gehra shade), gol chehra, badi aankhein, pyara expression.
- Background transparent (koi rect background nahi). Koi text nahi. Koi <image>, <script>, <foreignObject>, external link nahi.
- Kam se kam 25 shapes, detail achhi ho (kapde ki seam, baal, gehne, tilak jo bhi look mein ho).
- 9000 characters se chhota.
Sirf SVG code lautao, aur kuch nahi."""

FALLBACK_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 300">
<ellipse cx="100" cy="292" rx="46" ry="7" fill="#000" opacity=".15"/>
<rect x="78" y="215" width="18" height="78" rx="8" fill="{skin}"/><rect x="104" y="215" width="18" height="78" rx="8" fill="{skin}"/>
<path d="M60 120 Q100 100 140 120 L150 230 L50 230 Z" fill="{cloth}"/>
<path d="M62 125 Q40 170 56 205" stroke="{skin}" stroke-width="16" fill="none" stroke-linecap="round"/>
<path d="M138 125 Q160 170 146 205" stroke="{skin}" stroke-width="16" fill="none" stroke-linecap="round"/>
<rect x="90" y="96" width="20" height="20" fill="{skin}"/>
<circle cx="104" cy="70" r="36" fill="{skin}"/>
<path d="M68 62 Q100 20 140 62 Q104 46 68 62Z" fill="#2b1a0e"/>
<circle cx="116" cy="70" r="4.5" fill="#2b1a0e"/><circle cx="96" cy="70" r="4.5" fill="#2b1a0e"/>
<path d="M98 88 Q108 94 118 88" stroke="#5a2e14" stroke-width="3" fill="none" stroke-linecap="round"/>
</svg>"""

_FALLBACK_COLORS = ["#e65100", "#1565c0", "#2e7d32", "#6a1b9a", "#c62828", "#00838f"]


def _sanitize_svg(text):
    m = re.search(r"<svg[\s\S]*?</svg>", text)
    if not m:
        return None
    svg = m.group(0)
    svg = re.sub(r"<(script|foreignObject|image)[\s\S]*?(</\1>|/>)", "", svg, flags=re.I)
    svg = re.sub(r"\son\w+\s*=\s*(\"[^\"]*\"|'[^']*')", "", svg, flags=re.I)
    svg = re.sub(r"(xlink:)?href\s*=\s*(\"(?!#)[^\"]*\"|'(?!#)[^']*')", "", svg, flags=re.I)
    if "xmlns=" not in svg[:200]:
        svg = svg.replace("<svg", '<svg xmlns="http://www.w3.org/2000/svg"', 1)
    try:
        ET.fromstring(svg)
    except ET.ParseError:
        return None
    if svg.count("<") < 12:  # too empty
        return None
    return svg


def make_character_svgs(characters):
    for i, c in enumerate(characters):
        kind = c.get("kind", "person")
        obj_note = " Ye ek cheez hai, isliye ise neeche ki taraf rakh kar poore box mein bada banao." if kind == "object" else ""
        svg = None
        for attempt in range(3):
            try:
                txt = _gemini(SVG_PROMPT.format(kind=kind, look=c.get("look", c["id"]), obj_note=obj_note), temperature=0.7)
                svg = _sanitize_svg(txt)
            except Exception as e:  # noqa: BLE001
                print(f"[svg] {c['id']} error: {e}")
            if svg:
                break
            print(f"[svg] {c['id']} SVG kharab, dobara ({attempt + 1})")
        if not svg:
            print(f"[svg] {c['id']} -> simple fallback character")
            svg = FALLBACK_SVG.format(skin="#c68a5a", cloth=_FALLBACK_COLORS[i % len(_FALLBACK_COLORS)])
        c["svg"] = svg
        time.sleep(4)  # free-tier rate limit ke liye
    return characters


def make_plan(words, duration):
    lines = _transcript_lines(words)
    prompt = PLAN_PROMPT.format(
        dur=duration, lines=lines,
        enters="|".join(ENTERS), exits="|".join(EXITS),
        actions="|".join(ACTIONS), emotes="|".join(EMOTES),
    )
    raw = None
    for attempt in range(3):
        raw = _gemini(prompt, json_mode=True, temperature=0.6)
        try:
            plan = json.loads(raw[raw.find("{"): raw.rfind("}") + 1])
            break
        except json.JSONDecodeError:
            print(f"[plan] JSON kharab, dobara ({attempt + 1})")
    else:
        raise RuntimeError("Gemini se plan JSON nahi bana:\n" + (raw or "")[:500])
    plan = _clean_plan(plan, duration)
    print(f"[plan] {len(plan['scenes'])} scenes, {len(plan['characters'])} characters, {len(plan['backgrounds'])} backgrounds")
    plan["characters"] = make_character_svgs(plan["characters"])
    return plan
