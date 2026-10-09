"""Transcript -> scene plan + unique SVG characters, using the free Gemini API."""
import json
import os
import re
import time
import xml.etree.ElementTree as ET

import requests

BASE = "https://generativelanguage.googleapis.com/v1beta"
API = BASE + "/models/{model}:generateContent"

ACTIONS = ["idle", "talk", "walk", "jump", "shake", "glow", "bow", "eat", "rise", "sit"]
ENTERS = ["none", "left", "right", "pop", "fade", "top"]
EXITS = ["none", "left", "right", "fade", "up"]
EMOTES = ["none", "heart", "sparkle", "surprise", "anger", "sweat", "tears", "question"]


# ---------------------------------------------------------------- Gemini call
SKIP_WORDS = ("tts", "audio", "image", "live", "embed", "robotic", "computer", "vision", "aqa", "learnlm", "gemma", "omni")
_models_cache = None
_working = None  # jo model chal gaya, aage wahi use hoga


def _key():
    key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not key:
        raise SystemExit("GEMINI_API_KEY nahi mila. GitHub repo Settings > Secrets mein daalo.")
    return key


def _rank(name):
    """Naya Flash pehle, phir Pro, phir Lite; preview/exp sabse peeche."""
    n = name.lower()
    ver = re.search(r"gemini-(\d+(?:\.\d+)?)", n)
    v = float(ver.group(1)) if ver else 0.0
    if "flash" in n and "lite" not in n:
        tier = 0
    elif "pro" in n:
        tier = 1
    elif "lite" in n:
        tier = 2
    else:
        tier = 3
    unstable = 1 if ("preview" in n or "exp" in n) else 0
    return (unstable, tier, -v, n)


def candidate_models():
    """Aapki key par jo models generateContent kar sakte hain, unki list (best pehle)."""
    global _models_cache
    if _models_cache is not None:
        return _models_cache
    names = []
    try:
        r = requests.get(f"{BASE}/models", params={"key": _key(), "pageSize": 1000}, timeout=60)
        r.raise_for_status()
        for m in r.json().get("models", []):
            name = m.get("name", "").replace("models/", "")
            if "generateContent" not in m.get("supportedGenerationMethods", []):
                continue
            if not name.startswith("gemini") or any(w in name.lower() for w in SKIP_WORDS):
                continue
            names.append(name)
    except (requests.RequestException, ValueError) as e:
        print(f"[gemini] model list nahi mili ({e}), default naam try karenge")
    names = sorted(set(names), key=_rank)
    for fallback in ("gemini-flash-latest", "gemini-2.5-flash", "gemini-2.0-flash"):
        if fallback not in names:
            names.append(fallback)
    pinned = os.getenv("GEMINI_MODEL", "").strip()
    if pinned:
        names = [pinned] + [n for n in names if n != pinned]
    _models_cache = names
    print(f"[gemini] models (pehle 6): {names[:6]}")
    return names


def _call_one(model, body):
    """Ek model par call. Lautata hai (text, None) ya (None, 'skip'/'retry' + reason)."""
    try:
        r = requests.post(API.format(model=model), params={"key": _key()}, json=body, timeout=240)
    except requests.RequestException as e:
        return None, ("retry", str(e))
    if r.status_code in (400, 403, 404):
        return None, ("skip", f"HTTP {r.status_code}: {r.text[:200]}")
    if r.status_code == 429 or r.status_code >= 500:
        return None, ("retry", f"HTTP {r.status_code}: {r.text[:200]}")
    try:
        data = r.json()
        parts = data["candidates"][0]["content"]["parts"]
        text = "".join(p.get("text", "") for p in parts if not p.get("thought"))
    except (ValueError, KeyError, IndexError):
        return None, ("retry", f"khaali jawab: {r.text[:200]}")
    if not text.strip():
        return None, ("retry", "khaali jawab")
    return text, None


def _gemini(prompt, json_mode=False, temperature=0.8, extra_parts=None):
    global _working
    body = {
        "contents": [{"role": "user", "parts": list(extra_parts or []) + [{"text": prompt}]}],
        "generationConfig": {"temperature": temperature},
    }
    if json_mode:
        body["generationConfig"]["responseMimeType"] = "application/json"
    models = candidate_models()
    if _working in models:
        models = [_working] + [m for m in models if m != _working]
    errors = []
    for model in models[:8]:
        for attempt in range(3):
            text, err = _call_one(model, body)
            if text is not None:
                if _working != model:
                    print(f"[gemini] model chal gaya: {model}")
                _working = model
                return text
            kind, msg = err
            errors.append(f"{model}: {msg}")
            if kind == "skip":
                print(f"[gemini] {model} nahi chala ({msg[:80]}) -> agla model")
                break
            wait = 15 * (attempt + 1)
            print(f"[gemini] {model} busy ({msg[:80]}) -> {wait}s ruk ke dobara")
            time.sleep(wait)
    raise RuntimeError("Koi Gemini model nahi chala:\n" + "\n".join(errors[-6:]))


# ---------------------------------------------------------------- plan
PLAN_PROMPT = """Tum ek animation director ho. Neeche ek Hindi audio ka transcript hai,
har line ke aage uska start time (seconds) hai. Is audio ke upar 9:16 vertical 2D cartoon animation banana hai.
Jo shabd bola ja raha ho, wahi screen par dikhna chahiye.

AUDIO KYA HAI: {kind}
KYA HO RAHA HAI: {summary}
KAUN BOL RAHA HAI: {speakers}

TRANSCRIPT (total {dur:.1f} seconds):
{lines}

SABSE ZAROORI NIYAM:
- Sirf wahi dikhao jo transcript mein sach mein bola gaya hai. Apni taraf se koi kahani, yuddh, raja, bhagwan
  ya naya vishay mat jodo. Agar koi shabd sirf misaal ya mazaak mein aaya hai, to use mazaak ki tarah hi dikhao.
- Audio ke type ke hisaab se dikhao:
  * stand-up comedy: ek comedian (mic ke saath) stage par, peeche spotlight. Jab wo kisi cheez/insaan ki baat kare
    (biwi, boss, padosi, dost...), to wo character usi scene mein aaye aur joke wala kaam karta dikhe. Mazedaar emote use karo.
  * comedy sketch: jo log baat kar rahe hain wahi characters, rozmarra ki jagah (ghar, office, dukaan, gali).
  * katha/kahani: kahani ke log aur jagah.
  * jaankari/itihaas: jis cheez ki baat ho rahi hai wahi cheez aur ek samjhane wala character.

Sirf JSON lauto, is format mein:
{{
  "title": "<3-6 shabd ka aakarshak Hindi title, jaisa vishay ho (katha ho to 'कथा • ...', warna seedha naam)>",
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
- backgrounds: 2 se 5. Har prompt mein sirf KHAALI jagah ho jo audio se mel khaaye (comedy stage with spotlight, ghar ka kamra, office, gali, gaon, mandir...). Prompt mein "empty, nobody" likho; koi insaan, janwar, parchhaai, bheed nahi.
- characters: kahani ke saare zaroori log, janwar aur khaas cheezein (jaise khichdi ki katori, deepak, machine, aujaar). 2 se 8. id chhote english shabd.
- scenes: har 3-7 second par naya scene, jab kahani mein kuch naya ho. start time transcript ke time se milao. Pehla scene 0.0 se.
- Har scene mein 1-4 actors. x = 0.1 se 0.9 (screen ki chaudai ka hissa, actor ka beech). y = pairon ki line (0.75-0.88 zameen; aasmaan wali cheez 0.4-0.6). size = screen ki oonchai ka hissa (insaan 0.30-0.42, janwar 0.15-0.25, cheez 0.06-0.12, rakshas/bhagwan 0.5-0.65).
- Sab characters default mein DAAYEIN (right) dekhte hain. flip:true = baayein dekhe.
- enter: {enters}. exit: {exits}.
- action: {actions}.
- emote (sir ke upar): {emotes}.
- Jab koi naya character pehli baar kahani mein aaye, us scene mein uska enter "left"/"right"/"pop"/"top" rakho.
- Actors aapas mein overlap na karein.
"""


def _transcript_lines(words):
    return "\n".join(f"[{l[0]['s']:.1f}] " + " ".join(x["w"] for x in l) for l in _split_lines(words))


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
    plan["title"] = (plan.get("title") or "").strip()[:40]
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


def make_plan(words, duration, info=None):
    info = info or {}
    lines = _transcript_lines(words)
    prompt = PLAN_PROMPT.format(
        kind=info.get("type") or "pata nahi (transcript se samjho)",
        summary=info.get("summary") or "transcript se samjho",
        speakers=info.get("speakers") or "transcript se samjho",
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


# ---------------------------------------------------------------- subtitle spelling fix
FIX_PROMPT = """Neeche ek Hindi audio ka speech-to-text hai, line by line (JSON list). Machine ne bahut si spelling
galat likhi hai (jaise "आंदर" -> "अंदर", "कुथ समवे" -> "कुछ समय", "सलंडर" -> "सिलेंडर").
Har line ki sahi shuddh Hindi (Devanagari) spelling likho. Angrezi shabd bhi Devanagari mein hi rakho.

NIYAM:
- Lines ki ginti bilkul utni hi rahe ({n} lines), kram wahi.
- Har line mein shabd utne hi rakhne ki koshish karo, naye vaakya mat jodo, matlab mat badlo.
- Sirf spelling/shabd sudhaaro. Punctuation mat lagao.

Sirf JSON lautao: {{"lines": ["...", "..."]}}

INPUT:
{lines}
"""


def _split_lines(words, gap=0.6, max_words=12):
    lines, cur = [], []
    for w in words:
        if cur and (w["s"] - cur[-1]["e"] > gap or len(cur) >= max_words):
            lines.append(cur)
            cur = []
        cur.append(w)
    if cur:
        lines.append(cur)
    return lines


def _retime(line, new_words):
    """Purane shabdon ki timing naye shabdon par baanto."""
    if len(new_words) == len(line):
        return [{"w": nw, "s": o["s"], "e": o["e"]} for nw, o in zip(new_words, line)]
    start, end = line[0]["s"], line[-1]["e"]
    total = sum(len(w) for w in new_words) or 1
    out, t = [], start
    for nw in new_words:
        d = (end - start) * len(nw) / total
        out.append({"w": nw, "s": round(t, 2), "e": round(t + d, 2)})
        t += d
    return out


def correct_words(words):
    lines = _split_lines(words)
    texts = [" ".join(w["w"] for w in l) for l in lines]
    try:
        raw = _gemini(FIX_PROMPT.format(n=len(texts), lines=json.dumps(texts, ensure_ascii=False)),
                      json_mode=True, temperature=0.2)
        fixed = json.loads(raw[raw.find("{"): raw.rfind("}") + 1]).get("lines", [])
    except Exception as e:  # noqa: BLE001
        print(f"[fix] spelling sudhaar nahi hua ({e}), purane shabd hi rahenge")
        return words
    if len(fixed) != len(lines):
        print(f"[fix] lines ki ginti mismatch ({len(fixed)} vs {len(lines)}), purane shabd hi rahenge")
        return words
    out, changed = [], 0
    for line, new_text in zip(lines, fixed):
        new_words = [w for w in re.sub(r"[।,.!?;:\"']", " ", str(new_text)).split() if w]
        # bahut zyada badla ho to purana rakho (galat line se bachne ke liye)
        if not new_words or abs(len(new_words) - len(line)) > max(2, len(line) // 2):
            out.extend(line)
            continue
        changed += sum(1 for a, b in zip(new_words, line) if a != b["w"])
        out.extend(_retime(line, new_words))
    print(f"[fix] {changed} shabd sudhaare")
    return out


# ---------------------------------------------------------------- character jaanch
MEASURE_JS = """(svgText) => {
  const box = document.createElement('div');
  box.style.cssText = 'width:200px;height:300px;position:absolute;left:0;top:0';
  box.innerHTML = svgText;
  document.body.appendChild(box);
  const svg = box.querySelector('svg');
  if (!svg) { box.remove(); return null; }
  let bb = null;
  try { const b = svg.getBBox(); bb = {x: b.x, y: b.y, w: b.width, h: b.height}; } catch (e) {}
  const shapes = svg.querySelectorAll('path,rect,circle,ellipse,polygon,polyline,line').length;
  box.remove();
  return {bb, shapes};
}"""


def _fit_svg(svg, bb):
    """viewBox ko asli drawing ke hisaab se set karo, taaki character box mein poora bhare aur pair neeche hon."""
    pad = max(bb["w"], bb["h"]) * 0.04
    vb = f'{bb["x"] - pad:.1f} {bb["y"] - pad:.1f} {bb["w"] + 2 * pad:.1f} {bb["h"] + 2 * pad:.1f}'
    head_end = svg.index(">")
    head = svg[:head_end]
    head = re.sub(r'\s(viewBox|width|height|preserveAspectRatio)\s*=\s*("[^"]*"|\'[^\']*\')', "", head)
    head += f' viewBox="{vb}" preserveAspectRatio="xMidYMax meet"'
    return head + svg[head_end:]


def _measure_all(svgs):
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch()
        page = b.new_page()
        page.set_content("<html><body></body></html>")
        res = [page.evaluate(MEASURE_JS, s) for s in svgs]
        b.close()
    return res


def _is_bad(m):
    """Khaali, bahut kam shapes, ya box (200x300) ke chauthai se bhi chhota tukda = toota."""
    if not m or not m.get("bb") or m.get("shapes", 0) < 6:
        return True
    w, h = m["bb"]["w"], m["bb"]["h"]
    return (w < 50 and h < 75) or w < 10 or h < 10


def check_characters(characters):
    """Toote/chhote/khaali SVG dobara banwao, aur sabko box mein fit karo."""
    for round_no in range(2):
        ms = _measure_all([c["svg"] for c in characters])
        bad = [c for c, m in zip(characters, ms) if _is_bad(m)]
        if not bad or round_no == 1:
            break
        print(f"[svg] toote characters dobara: {[c['id'] for c in bad]}")
        for c in bad:
            c.pop("svg", None)
        make_character_svgs(bad)
    ms = _measure_all([c["svg"] for c in characters])
    for i, (c, m) in enumerate(zip(characters, ms)):
        if _is_bad(m):
            print(f"[svg] {c['id']} ab bhi toota -> simple character")
            c["svg"] = FALLBACK_SVG.format(skin="#c68a5a", cloth=_FALLBACK_COLORS[i % len(_FALLBACK_COLORS)])
            continue
        c["svg"] = _fit_svg(c["svg"], m["bb"])
        print(f"[svg] {c['id']} ok ({m['shapes']} shapes, size {m['bb']['w']:.0f}x{m['bb']['h']:.0f})")
    return characters
