"""Background images: Pollinations.ai (free, no key). Fail ho to apna gradient background."""
import hashlib
import io
import random
import time
import urllib.parse

import requests
from PIL import Image, ImageDraw, ImageFilter

STYLE = (", flat 2D vector cartoon illustration, Indian devotional storybook art, warm soft colours, "
         "clean shapes, vertical 9:16 composition, empty foreground ground area at the bottom, "
         "no people, no animals, no text, no watermark")

URL = "https://image.pollinations.ai/prompt/{p}?width=1080&height=1920&nologo=true&seed={seed}&model=flux"


def _pollinations(prompt, seed):
    url = URL.format(p=urllib.parse.quote(prompt + STYLE), seed=seed)
    for attempt in range(3):
        try:
            r = requests.get(url, timeout=180)
            if r.ok and r.headers.get("content-type", "").startswith("image"):
                img = Image.open(io.BytesIO(r.content)).convert("RGB")
                if img.width >= 400:
                    return img
            print(f"[bg] pollinations HTTP {r.status_code}")
        except requests.RequestException as e:
            print(f"[bg] pollinations error: {e}")
        time.sleep(15 * (attempt + 1))
    return None


PALETTES = [
    ("#ff9a3c", "#ffe29a", "#8bc34a", "#5a8f2a"),  # din, gaon
    ("#1a237e", "#5c6bc0", "#2e3b2e", "#1b261b"),  # raat
    ("#ff7043", "#ffcc80", "#c8a165", "#8d6e3f"),  # sham, registan
    ("#4fc3f7", "#e1f5fe", "#66bb6a", "#2e7d32"),  # subah, jungle
]


def _fallback(prompt, seed):
    rnd = random.Random(seed)
    night = any(k in prompt.lower() for k in ("night", "dark", "moon"))
    sky1, sky2, g1, g2 = PALETTES[1] if night else rnd.choice([PALETTES[0], PALETTES[2], PALETTES[3]])
    W, H = 1080, 1920
    img = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(img)

    def mix(a, b, t):
        a = [int(a[i:i + 2], 16) for i in (1, 3, 5)]
        b = [int(b[i:i + 2], 16) for i in (1, 3, 5)]
        return tuple(int(a[k] + (b[k] - a[k]) * t) for k in range(3))

    hz = int(H * 0.6)
    for y in range(hz):
        d.line([(0, y), (W, y)], fill=mix(sky1, sky2, y / hz))
    for y in range(hz, H):
        d.line([(0, y), (W, y)], fill=mix(g1, g2, (y - hz) / (H - hz)))
    # door ki pahadiyan
    for k in range(2):
        base = hz - 40 + k * 30
        pts = [(0, base)] + [(x, base - rnd.randint(40, 160)) for x in range(0, W + 200, 200)] + [(W, base + 80), (0, base + 80)]
        d.polygon(pts, fill=mix(sky2, g2, 0.45 + k * 0.2))
    if night:
        for _ in range(120):
            x, y = rnd.randint(0, W), rnd.randint(0, hz - 200)
            d.ellipse([x, y, x + 4, y + 4], fill="#ffffff")
        d.ellipse([760, 260, 900, 400], fill="#fff8e1")
    else:
        d.ellipse([720, 300, 900, 480], fill="#fff3c4")
    return img.filter(ImageFilter.GaussianBlur(1))


def get_backgrounds(plan, workdir):
    workdir.mkdir(parents=True, exist_ok=True)
    out = {}
    pollinations_ok = True
    for bg in plan["backgrounds"]:
        seed = int(hashlib.md5(bg["prompt"].encode()).hexdigest()[:6], 16)
        img = _pollinations(bg["prompt"], seed) if pollinations_ok else None
        if img is None:
            pollinations_ok = False  # ek baar fail = baaki ke liye seedha backup
        if img is None:
            print(f"[bg] {bg['id']} -> fallback gradient")
            img = _fallback(bg["prompt"], seed)
        # 9:16 crop
        tw, th = 1080, 1920
        scale = max(tw / img.width, th / img.height)
        img = img.resize((int(img.width * scale) + 1, int(img.height * scale) + 1), Image.LANCZOS)
        left, top = (img.width - tw) // 2, (img.height - th) // 2
        img = img.crop((left, top, left + tw, top + th))
        path = workdir / f"{bg['id']}.jpg"
        img.save(path, quality=88)
        out[bg["id"]] = path
        time.sleep(3)
    return out
