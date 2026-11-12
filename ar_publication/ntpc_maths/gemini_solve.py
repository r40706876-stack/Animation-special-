"""Gemini (free tier) se book ke pages ke sawaal + short Hindi hal banana.

Usage: python gemini_solve.py START_PAGE END_PAGE
Env:   GEMINI_API_KEY  (alag Google project wali key - katha reels ka quota na kate)
Output: data/cNN_pPPP.json (ek page = ek file). Jo page pehle se bana hai use skip karta hai.
Answer hamesha book ki answer key se lagta hai; Gemini ka jawab alag aaye to review.txt mein likh deta hai.
"""
import base64, glob, json, os, re, sys, time
import requests
import pypdfium2 as pdfium

HERE = os.path.dirname(os.path.abspath(__file__))
BOOK_DIR = os.path.abspath(os.environ.get("BOOK_DIR", HERE))  # kaun si book: ntpc_maths / ntpc_reasoning ...
CFG = json.load(open(os.path.join(BOOK_DIR, "book.json"), encoding="utf-8"))
BOOK = os.path.join(BOOK_DIR, "source", "book.pdf")
DATA = os.path.join(BOOK_DIR, "data")
FIGS = os.path.join(BOOK_DIR, "figs")
REVIEW = os.path.join(BOOK_DIR, "review.txt")
# Kai keys (alag Google projects = alag free quota). Comma/space se alag.
KEYS = [k for k in re.split(r"[,\s]+", os.environ.get("GEMINI_API_KEYS", "") + "," + os.environ.get("GEMINI_API_KEY", "")) if k]
KEYS = list(dict.fromkeys(KEYS))
KEY = KEYS[0] if KEYS else ""
MODELS = [m for m in os.environ.get("GEMINI_MODELS",
          "gemini-3.5-flash,gemini-3-flash-preview,gemini-2.5-flash,gemini-2.5-pro,gemini-3.1-flash-lite,gemini-2.5-flash-lite").split(",") if m]
BATCH = int(os.environ.get("PAGES_PER_CALL", "3"))  # ek request mein itne page -> 3 guna kam requests
DEAD = set()  # (key, model) jinki aaj ki limit khatam

# (no, en, hi, start_page, total, gl, ug) - book.json se
CHAPTERS = [tuple(c[:7]) for c in CFG["chapters"]]
LAST_PAGE = CFG["last_page"]
SUBJECT = CFG.get("subject_en", "Maths")
HINT = ("\n  " + CFG["sol_hint"].replace("{", "(").replace("}", ")")) if CFG.get("sol_hint") else ""


_PDF = None


def pdf():
    global _PDF
    if _PDF is None:
        _PDF = pdfium.PdfDocument(BOOK)
    return _PDF


def page_text(p):  # apt/poppler ki zaroorat nahi
    return pdf()[p - 1].get_textpage().get_text_range() + "\n"


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
    if k < 0:  # kuch books (GK) mein har sawaal ke saath hi "Q.12 GL Ans: (B)"
        return {int(n): a for n, a in re.findall(r"Q\.(\d+)\s+(?:GL|UG)\s+Ans:\s*\(([ABCD])\)", txt)}
    return {int(n): a for n, a in re.findall(r"(?<![\d.])(\d{1,3})\s+([ABCD])\b", txt[k:])}


def page_png_b64(p):
    out = os.path.join("/tmp", f"pg{p}.png")
    pdf()[p - 1].render(scale=110 / 72).to_pil().save(out)
    return base64.b64encode(open(out, "rb").read()).decode()


EXAMPLE = {"n": 16, "lvl": "GL",
           "en": "The HCF of two numbers is 6 and their LCM is 72. If one of the numbers is 18, find the other number.",
           "hi": "दो संख्याओं का HCF 6 और LCM 72 है। यदि एक संख्या 18 है, तो दूसरी संख्या ज्ञात कीजिए।",
           "opts": ["48", "12", "24", "36"], "my_ans": "C",
           "sol": "पहली × दूसरी = HCF × LCM → 18 × दूसरी = 6 × 72 = 432<br>दूसरी = 432 ÷ 18 = 24.",
           "trick": "दो संख्याओं का गुणनफल = HCF × LCM"}

PROMPT = """You are preparing an exam-prep book page. The image is one page of an RRB NTPC {subject} PYQ book.
The pdftotext output below may have broken Hindi spacing and missing formulas (fractions, recurring bars, roots, images) - ALWAYS trust the IMAGE.

For EVERY question on this page return a JSON list. Each item:
- "n": question number (int), "lvl": "GL" or "UG"
- "en": clean English question text, "hi": clean Hindi question text (fix spacing like "कु ल"→"कुल", "दू सरी"→"दूसरी")
- "opts": exactly 4 option strings in order A,B,C,D (if an option has Hindi too, write "English<br>हिन्दी")
- "my_ans": your own answer letter
- "sol": a SHORT solution in simple Hindi (Devanagari), 1-3 lines joined with <br>, show only key steps and numbers, easy for a weak student. Do NOT write the final "उत्तर" line.{hint}
- "fig": ONLY if the question/options contain a diagram, figure or table that cannot be written as plain text: {{"page": <page number>, "box": [ymin, xmin, ymax, xmax]}} with coordinates 0-1000 on THAT page image, tightly around the figure only. Otherwise omit "fig".
- "trick": ONE short Hindi line (max ~15 words) - a memory rule / shortcut / formula behind this question that the student should remember for the exam.
Math formatting: use plain text/HTML only: x², 2³, √, ÷, ×, fractions as a/b, <sup>..</sup>, recurring as 0.<span style='text-decoration:overline'>5</span>, variables in <i>x</i>. No LaTeX, no markdown, no double quotes inside strings (use single quotes).
Never write any coaching / channel / telegram name. Write the solution in your OWN words - never copy any explanation printed on the page. Skip anything that is not a question (headers, answer-key tables).
Official answers from the book key (use them; your solution must reach this answer): {keys}
Return ONLY the JSON list. Example item: {example}

pdftotext of this page:
<<<
{text}
>>>"""


def call(body):
    """Har key x har model try karo. Return (json, model). Sab ki limit khatam -> RuntimeError('HTTP 429 ...')."""
    last, any_alive = "", False
    for k in KEYS:
        for m in MODELS:
            if (k, m) in DEAD:
                continue
            any_alive = True
            for attempt in range(2):
                try:
                    r = requests.post(f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent",
                                      params={"key": k}, json=body, timeout=300)
                except requests.RequestException as e:
                    last = f"{m}: network {e}"; time.sleep(10); continue
                if r.status_code == 200:
                    try:
                        out = r.json()["candidates"][0]["content"]["parts"]
                        return json.loads("".join(x.get("text", "") for x in out)), m
                    except Exception as e:  # bad JSON - ek baar aur
                        last = f"{m}: parse error {e}"; continue
                last = f"{m}: HTTP {r.status_code} {r.text[:160]}"
                if r.status_code == 429 and "PerMinute" in r.text and attempt == 0:
                    time.sleep(40); continue  # sirf minute wali limit - thoda ruko
                if r.status_code in (429, 404, 403, 400):
                    DEAD.add((k, m)); break  # is key+model ka aaj ka quota / model nahi - agla
                time.sleep(10)
    if not any_alive or all((k, m) in DEAD for k in KEYS for m in MODELS):
        raise RuntimeError("HTTP 429 sab keys/models ki aaj ki limit khatam. " + last)
    raise RuntimeError(last)


def save_fig(q, pages, ch):
    f = q.pop("fig", None)
    if not isinstance(f, dict) or not isinstance(f.get("box"), list) or len(f["box"]) != 4:
        return  # chitra nahi hai - kuch nahi karna
    try:
        pg = int(f["page"]) if isinstance(f, dict) and f.get("page") else pages[0]
        y0, x0, y1, x1 = [max(0, min(1000, float(v))) for v in f["box"]]
        if pg not in pages or y1 - y0 < 15 or x1 - x0 < 15:
            return
        im = pdf()[pg - 1].render(scale=200 / 72).to_pil()
        W, H = im.size
        pad = 8
        crop = im.crop((max(0, x0 * W / 1000 - pad), max(0, y0 * H / 1000 - pad), min(W, x1 * W / 1000 + pad), min(H, y1 * H / 1000 + pad)))
        os.makedirs(FIGS, exist_ok=True)
        name = f"c{ch[0]:02d}_q{q['n']:03d}.png"
        crop.save(os.path.join(FIGS, name))
        q["img"] = "figs/" + name
    except Exception as e:
        print("fig crop fail", q.get("n"), e)


def ask_gemini(pages, text, keys):
    parts = [{"inline_data": {"mime_type": "image/png", "data": page_png_b64(p)}} for p in pages]
    note = f"There are {len(pages)} consecutive page images (pages {pages}). Cover EVERY question on ALL of them.\n" if len(pages) > 1 else ""
    parts.append({"text": note + PROMPT.format(subject=SUBJECT, hint=HINT, keys=json.dumps(keys), example=json.dumps(EXAMPLE, ensure_ascii=False), text=text)})
    return call({"contents": [{"parts": parts}],
                 "generationConfig": {"responseMimeType": "application/json", "temperature": 0.2}})


TRICK_PROMPT = """For each exam question below write ONE short Hindi line (max ~15 words): the memory rule / shortcut / formula
behind it that a student should remember for the exam. Plain text/HTML only (x², √, a/b), no LaTeX, no double quotes, no coaching names.
Return ONLY a JSON object mapping question number (string) to the Hindi line.
Questions:
{qs}"""


def add_tricks():
    """Jin files mein 'trick' nahi hai unme sirf trick line jodna (image nahi, bahut kam quota)."""
    for f in sorted(glob.glob(os.path.join(DATA, "c*_p*.json"))):
        d = json.load(open(f, encoding="utf-8"))
        need = [q for q in d["questions"] if not q.get("trick")]
        if not need:
            continue
        qs = "\n".join(f"{q['n']}. {re.sub('<[^>]+>', ' ', q['en'])} | solution: {re.sub('<[^>]+>', ' ', q['sol'])}" for q in need)
        body = {"contents": [{"parts": [{"text": TRICK_PROMPT.format(qs=qs)}]}],
                "generationConfig": {"responseMimeType": "application/json", "temperature": 0.3}}
        try:
            got, _ = call(body)
        except RuntimeError:
            got = None
        if not isinstance(got, dict):
            print(f"{os.path.basename(f)}: trick nahi bani (limit?) - agli baar"); return
        for q in need:
            if got.get(str(q["n"])):
                q["trick"] = got[str(q["n"])]
        json.dump(d, open(f, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print(f"{os.path.basename(f)}: {len(need)} trick jodi")
        time.sleep(6)


BAD = re.compile(r"विकल्प के अनुसार|लेकिन विकल्प|उत्तर कुंजी|answer key|key के अनुसार|दिए गए उत्तर|विकल्पों में नहीं|कोई विकल्प नहीं|त्रुटि|not match|मेल नहीं|शायद|संभवतः|पुन: जाँच|पुनः जाँच|प्रश्न के अनुसार सही|निकटतम है", re.I)
GOOD_MODELS = [m for m in MODELS if "lite" not in m]

FIX_PROMPT = """The image is a page of an RRB NTPC {subject} PYQ book. Solve question Q.{n} on it ({lvl}) properly.
The OFFICIAL correct answer is option ({ans}) = {opt}. Write a correct, clean, SHORT solution in simple Hindi (1-3 steps joined with <br>)
that logically reaches exactly this answer. Re-read the question carefully from the IMAGE (the earlier solution misread it).
NEVER mention errors, answer key, options, doubt or words like शायद/संभवतः/त्रुटि. If the printed question really has a typo,
silently use the most likely intended reading. Also give "trick": one short Hindi memory line.
Plain text/HTML only (x², a/b, <br>), no LaTeX, no double quotes.
Return ONLY JSON: {{"sol": "...", "trick": "..."}}
Question text: {q}"""


def fix_bad():
    """Gol-mol hal (त्रुटि/विकल्प के अनुसार...) ko achhe model se dobara likhwana. Har sawaal max 2 koshish."""
    global MODELS
    keep, MODELS = MODELS, GOOD_MODELS or MODELS
    try:
        for f in sorted(glob.glob(os.path.join(DATA, "c*_p*.json"))):
            d = json.load(open(f, encoding="utf-8"))
            changed = False
            for q in d["questions"]:
                if not BAD.search(q.get("sol", "")) or q.get("fix_tries", 0) >= 2:
                    continue
                pages = [int(x) for x in re.findall(r"\d+", d.get("source_pages", ""))]
                pages = list(range(pages[0], pages[-1] + 1)) if pages else []
                ans = q["ans"]
                opt = re.sub("<[^>]+>", " ", q["opts"]["ABCD".index(ans)]) if ans in "ABCD" and len(q["opts"]) == 4 else ans
                parts = [{"inline_data": {"mime_type": "image/png", "data": page_png_b64(p)}} for p in pages[:3]]
                parts.append({"text": FIX_PROMPT.format(subject=SUBJECT, n=q["n"], lvl=q.get("lvl", ""), ans=ans, opt=opt,
                                                        q=re.sub("<[^>]+>", " ", q["en"]))})
                q["fix_tries"] = q.get("fix_tries", 0) + 1; changed = True
                try:
                    got, m = call({"contents": [{"parts": parts}], "generationConfig": {"responseMimeType": "application/json", "temperature": 0.2}})
                except RuntimeError as e:
                    if "HTTP 429" in str(e):
                        print("fix: aaj ki achhe model ki limit khatam, agle run mein"); q["fix_tries"] -= 1
                        json.dump(d, open(f, "w", encoding="utf-8"), ensure_ascii=False, indent=1); return
                    continue
                if isinstance(got, dict) and got.get("sol") and not BAD.search(got["sol"]):
                    q["sol"] = got["sol"]
                    if got.get("trick"):
                        q["trick"] = got["trick"]
                    print(f"fix: {os.path.basename(f)} Q.{q['n']} hal sudhara ({m})")
                time.sleep(4)
            if changed:
                json.dump(d, open(f, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    finally:
        MODELS = keep


def main():
    if not KEYS:
        sys.exit("GEMINI_API_KEY secret nahi mila")
    a, b = int(sys.argv[1]), min(int(sys.argv[2]), LAST_PAGE)
    os.makedirs(DATA, exist_ok=True)
    done_pages = set()
    for f in glob.glob(os.path.join(DATA, "c*_p*.json")):
        m = re.search(r"_p(\d+)(?:-(\d+))?\.json$", f)
        s, e = int(m.group(1)), int(m.group(2) or m.group(1))
        done_pages.update(range(s, e + 1))
    keys_cache, review, todo = {}, [], []
    for p in range(a, b + 1):
        if p in done_pages:
            continue
        text = page_text(p)
        qnums = [int(x) for x in re.findall(r"Q\.(\d+)\s+(?:GL|UG)", text.split("Answer Key")[0])]
        if qnums:
            todo.append((p, chapter_of(p), text, qnums))
    print(f"baaki pages: {len(todo)} ({len(KEYS)} key, {BATCH} page/request)")
    batches = []  # ek hi chapter ke lagaatar pages, max BATCH
    for item in todo:
        if batches and len(batches[-1]) < BATCH and batches[-1][-1][1] == item[1] and item[0] - batches[-1][-1][0] <= 2:
            batches[-1].append(item)
        else:
            batches.append([item])
    for bt in batches:
        pages = [x[0] for x in bt]
        ch = bt[0][1]
        if ch[0] not in keys_cache:
            keys_cache[ch[0]] = answer_key(ch)
        key = keys_cache[ch[0]]
        qnums = [n for x in bt for n in x[3]]
        keys = {n: key.get(n, "?") for n in qnums}
        text = "\n".join(f"----- page {x[0]} -----\n{x[2]}" for x in bt)
        try:
            qs, model = ask_gemini(pages, text, keys)
        except RuntimeError as e:
            if "HTTP 429" in str(e):
                print(f"pages {pages}: {e}\nAgla run (2 ghante baad) yahin se aage banayega.")
                break
            print(f"pages {pages}: Gemini fail -> {e} (agle run mein dobara)")
            continue
        if isinstance(qs, dict):
            qs = qs.get("questions", [])
        qs = [q for q in qs if isinstance(q, dict) and q.get("n") in qnums]
        qs = list({q["n"]: q for q in qs}.values())
        missing = set(qnums) - {q["n"] for q in qs}
        if len(missing) > len(qnums) // 2:  # aadhe se zyada chhoote -> save mat karo, dobara banega
            print(f"pages {pages}: bahut sawaal chhoote {sorted(missing)}, agle run mein dobara"); continue
        if missing:
            review.append(f"pages {pages} chapter {ch[0]}: ye sawaal chhoot gaye {sorted(missing)}")
        for q in qs:
            save_fig(q, pages, ch)
            if q.get("img"):
                review.append(f"pages {pages} chapter {ch[0]} Q.{q['n']}: chitra (figure) wala sawaal - image ek baar dekh lena ({q['img']})")
            q["ans"] = key.get(q["n"], q.get("my_ans", "?"))
            if q.get("my_ans") != q["ans"]:
                review.append(f"pages {pages} chapter {ch[0]} Q.{q['n']}: Gemini={q.get('my_ans')} key={q['ans']} - hal check karo")
            if len(q.get("opts", [])) != 4:
                review.append(f"pages {pages} chapter {ch[0]} Q.{q['n']}: options 4 nahi aaye")
        rng = f"p{pages[0]:03d}" + (f"-{pages[-1]:03d}" if len(pages) > 1 else "")
        d = {"chapter": {"no": ch[0], "en": ch[1], "hi": ch[2], "total": ch[4], "gl": ch[5], "ug": ch[6]},
             "source_pages": f"{pages[0]}-{pages[-1]}", "model": model, "questions": sorted(qs, key=lambda q: q["n"])}
        json.dump(d, open(os.path.join(DATA, f"c{ch[0]:02d}_{rng}.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print(f"pages {pages}: {len(qs)} sawaal ({model})")
        time.sleep(5)
    add_tricks()
    fix_bad()
    if review:
        open(REVIEW, "a", encoding="utf-8").write("\n".join(review) + "\n")
        print("REVIEW:\n" + "\n".join(review))


if __name__ == "__main__":
    main()
