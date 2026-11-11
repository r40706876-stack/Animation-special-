"""Gemini (free tier) se book ke pages ke sawaal + short Hindi hal banana.

Usage: python gemini_solve.py START_PAGE END_PAGE
Env:   GEMINI_API_KEY  (alag Google project wali key - katha reels ka quota na kate)
Output: data/cNN_pPPP.json (ek page = ek file). Jo page pehle se bana hai use skip karta hai.
Answer hamesha book ki answer key se lagta hai; Gemini ka jawab alag aaye to review.txt mein likh deta hai.
"""
import base64, glob, json, os, re, subprocess, sys, time
import requests

HERE = os.path.dirname(os.path.abspath(__file__))
BOOK = os.path.join(HERE, "source", "book.pdf")
DATA = os.path.join(HERE, "data")
REVIEW = os.path.join(HERE, "review.txt")
KEY = os.environ.get("GEMINI_API_KEY", "").strip()
MODELS = [m for m in os.environ.get("GEMINI_MODELS", "gemini-3.5-flash,gemini-2.5-flash,gemini-3-flash-preview").split(",") if m]

# (no, en, hi, start_page, total, gl, ug) - book ke index se
CHAPTERS = [
    (1, "Number System", "संख्या पद्धति", 4, 87, 38, 49), (2, "LCM & HCF", "लघुत्तम एवं महत्तम समापवर्तक", 18, 50, 0, 50),
    (3, "Simplification", "सरलीकरण", 26, 130, 38, 92), (4, "Algebra", "बीजगणित", 47, 112, 75, 37),
    (5, "Quadratic Equations", "द्विघात समीकरण", 66, 7, 7, 0), (6, "Percentage", "प्रतिशत", 69, 100, 43, 57),
    (7, "Profit & Loss", "लाभ एवं हानि", 87, 102, 49, 53), (8, "Discount", "बट्टा / छूट", 105, 101, 23, 78),
    (9, "Simple Interest", "साधारण ब्याज", 126, 59, 24, 35), (10, "Compound Interest", "चक्रवृद्धि ब्याज", 136, 52, 23, 29),
    (11, "Ratio & Proportion", "अनुपात एवं समानुपात", 147, 140, 59, 81), (12, "Partnership", "साझेदारी", 169, 32, 15, 17),
    (13, "Mixture & Alligation", "मिश्रण", 176, 3, 0, 3), (14, "Average", "औसत", 178, 93, 53, 40),
    (15, "Problems on Age", "आयु संबंधी प्रश्न", 194, 43, 8, 35), (16, "Time & Work", "समय एवं कार्य", 203, 88, 49, 39),
    (17, "Pipe & Cistern", "पाइप एवं टंकी", 219, 31, 0, 31), (18, "Time, Speed & Distance", "समय, चाल एवं दूरी", 226, 89, 24, 65),
    (19, "Boat & Stream", "नाव एवं धारा", 243, 12, 12, 0), (20, "Race", "दौड़", 247, 7, 7, 0),
    (21, "Mensuration", "क्षेत्रमिति", 250, 89, 47, 42), (22, "Geometry", "ज्यामिति", 267, 103, 50, 53),
    (23, "Trigonometry", "त्रिकोणमिति", 288, 35, 23, 12), (24, "Height & Distance", "ऊँचाई एवं दूरी", 296, 16, 0, 16),
    (25, "Statistics", "सांख्यिकी", 301, 73, 47, 26), (26, "Venn Diagram", "वेन आरेख", 319, 5, 0, 5),
    (27, "Statement Based Questions", "कथन आधारित प्रश्न", 325, 20, 0, 20),
]
LAST_PAGE = 330


def page_text(p):
    return subprocess.run(["pdftotext", "-f", str(p), "-l", str(p), "-layout", BOOK, "-"],
                          capture_output=True, text=True).stdout


def chapter_of(p):
    ch = None
    for c in CHAPTERS:
        if c[3] <= p:
            ch = c
    return ch


def answer_key(ch):
    i = CHAPTERS.index(ch)
    end = CHAPTERS[i + 1][3] - 1 if i + 1 < len(CHAPTERS) else LAST_PAGE
    txt = "".join(page_text(p) for p in range(ch[3], end + 1))
    k = txt.find("Answer Key")
    if k < 0:
        return {}
    return {int(n): a for n, a in re.findall(r"(?<![\d.])(\d{1,3})\s+([ABCD])\b", txt[k:])}


def page_png_b64(p):
    out = os.path.join("/tmp", f"pg{p}")
    subprocess.run(["pdftoppm", "-f", str(p), "-l", str(p), "-r", "110", "-png", "-singlefile", BOOK, out], check=True)
    return base64.b64encode(open(out + ".png", "rb").read()).decode()


EXAMPLE = {"n": 16, "lvl": "GL",
           "en": "The HCF of two numbers is 6 and their LCM is 72. If one of the numbers is 18, find the other number.",
           "hi": "दो संख्याओं का HCF 6 और LCM 72 है। यदि एक संख्या 18 है, तो दूसरी संख्या ज्ञात कीजिए।",
           "opts": ["48", "12", "24", "36"], "my_ans": "C",
           "sol": "पहली × दूसरी = HCF × LCM → 18 × दूसरी = 6 × 72 = 432<br>दूसरी = 432 ÷ 18 = 24."}

PROMPT = """You are preparing an exam-prep book page. The image is one page of an RRB NTPC Maths PYQ book.
The pdftotext output below may have broken Hindi spacing and missing formulas (fractions, recurring bars, roots, images) - ALWAYS trust the IMAGE.

For EVERY question on this page return a JSON list. Each item:
- "n": question number (int), "lvl": "GL" or "UG"
- "en": clean English question text, "hi": clean Hindi question text (fix spacing like "कु ल"→"कुल", "दू सरी"→"दूसरी")
- "opts": exactly 4 option strings in order A,B,C,D (if an option has Hindi too, write "English<br>हिन्दी")
- "my_ans": your own answer letter
- "sol": a SHORT solution in simple Hindi (Devanagari), 1-3 lines joined with <br>, show only key steps and numbers, easy for a weak student. Do NOT write the final "उत्तर" line.
Math formatting: use plain text/HTML only: x², 2³, √, ÷, ×, fractions as a/b, <sup>..</sup>, recurring as 0.<span style='text-decoration:overline'>5</span>, variables in <i>x</i>. No LaTeX, no markdown, no double quotes inside strings (use single quotes).
Never write any coaching / channel / telegram name. Skip anything that is not a question (headers, answer-key tables).
Official answers from the book key (use them; your solution must reach this answer): {keys}
Return ONLY the JSON list. Example item: {example}

pdftotext of this page:
<<<
{text}
>>>"""


def ask_gemini(p, text, keys):
    body = {
        "contents": [{"parts": [
            {"inline_data": {"mime_type": "image/png", "data": page_png_b64(p)}},
            {"text": PROMPT.format(keys=json.dumps(keys), example=json.dumps(EXAMPLE, ensure_ascii=False), text=text)}]}],
        "generationConfig": {"responseMimeType": "application/json", "temperature": 0.2},
    }
    last = ""
    for m in MODELS:
        for attempt in range(2):
            r = requests.post(f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent",
                              params={"key": KEY}, json=body, timeout=300)
            if r.status_code == 200:
                try:
                    out = r.json()["candidates"][0]["content"]["parts"]
                    raw = "".join(x.get("text", "") for x in out)
                    return json.loads(raw), m
                except Exception as e:  # bad JSON - ek baar aur
                    last = f"{m}: parse error {e}"
                    continue
            last = f"{m}: HTTP {r.status_code} {r.text[:200]}"
            if r.status_code in (429, 404, 403):
                break  # is model ki limit/available nahi - agla model
            time.sleep(10)
    raise RuntimeError(last)


def main():
    if not KEY:
        sys.exit("GEMINI_API_KEY secret nahi mila")
    a, b = int(sys.argv[1]), int(sys.argv[2])
    os.makedirs(DATA, exist_ok=True)
    done_pages = set()
    for f in glob.glob(os.path.join(DATA, "c*_p*.json")):
        m = re.search(r"_p(\d+)(?:-(\d+))?\.json$", f)
        s, e = int(m.group(1)), int(m.group(2) or m.group(1))
        done_pages.update(range(s, e + 1))
    keys_cache, review = {}, []
    for p in range(a, b + 1):
        if p in done_pages:
            print(f"page {p}: pehle se bana hai, skip"); continue
        text = page_text(p)
        qnums = [int(x) for x in re.findall(r"Q\.(\d+)", text)]
        if not qnums:
            print(f"page {p}: koi sawaal nahi, skip"); continue
        ch = chapter_of(p)
        if ch[0] not in keys_cache:
            keys_cache[ch[0]] = answer_key(ch)
        key = keys_cache[ch[0]]
        keys = {n: key.get(n, "?") for n in qnums}
        try:
            qs, model = ask_gemini(p, text, keys)
        except RuntimeError as e:
            print(f"page {p}: Gemini fail -> {e}\nAaj ki limit khatam lagti hai. Kal isi range ko dobara chalao, bane hue page skip honge.")
            break
        for q in qs:
            q["ans"] = key.get(q["n"], q.get("my_ans", "?"))
            if q.get("my_ans") != q["ans"]:
                review.append(f"page {p} chapter {ch[0]} Q.{q['n']}: Gemini={q.get('my_ans')} key={q['ans']} - hal check karo")
            if len(q.get("opts", [])) != 4:
                review.append(f"page {p} chapter {ch[0]} Q.{q['n']}: options 4 nahi aaye")
        missing = set(qnums) - {q["n"] for q in qs}
        if missing:
            review.append(f"page {p}: ye sawaal chhoot gaye {sorted(missing)}")
        d = {"chapter": {"no": ch[0], "en": ch[1], "hi": ch[2], "total": ch[4], "gl": ch[5], "ug": ch[6]},
             "source_pages": str(p), "model": model, "questions": sorted(qs, key=lambda q: q["n"])}
        json.dump(d, open(os.path.join(DATA, f"c{ch[0]:02d}_p{p:03d}.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print(f"page {p}: {len(qs)} sawaal ({model})")
        time.sleep(6)  # free tier per-minute limit
    if review:
        open(REVIEW, "a", encoding="utf-8").write("\n".join(review) + "\n")
        print("REVIEW:\n" + "\n".join(review))


if __name__ == "__main__":
    main()
