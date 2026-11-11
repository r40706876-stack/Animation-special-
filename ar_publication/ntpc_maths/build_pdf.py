"""AR Publication - RRB NTPC Maths PYQ (with solutions) PDF builder. Design: khula + rang-biranga (final).

Reads every data/*.json (chapter-wise jod kar) and writes out/RRB_NTPC_Maths_PYQ_Solutions_AR_Publication.pdf
Usage:  python ar_publication/ntpc_maths/build_pdf.py
Needs:  playwright (chromium ya runner ka Google Chrome). Hindi font repo ke fonts/ folder mein hai.
"""
import glob, html, json, os, re, sys
from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
FONT_DIR = os.path.join(HERE, "fonts")
BRAND = "AR Publication"
TITLE = "RRB NTPC 2025-26 · Maths PYQ (GL + UG) · हल सहित"

TOPICS = [
    ("Number System", "संख्या पद्धति", 87, "🔢"), ("LCM & HCF", "लघुत्तम एवं महत्तम समापवर्तक", 50, "➗"),
    ("Simplification", "सरलीकरण", 130, "🧮"), ("Algebra", "बीजगणित", 112, "🔣"),
    ("Quadratic Equations", "द्विघात समीकरण", 7, "📐"), ("Percentage", "प्रतिशत", 100, "💯"),
    ("Profit & Loss", "लाभ एवं हानि", 102, "💰"), ("Discount", "बट्टा / छूट", 101, "🏷️"),
    ("Simple Interest", "साधारण ब्याज", 59, "🏦"), ("Compound Interest", "चक्रवृद्धि ब्याज", 52, "📈"),
    ("Ratio & Proportion", "अनुपात एवं समानुपात", 140, "⚖️"), ("Partnership", "साझेदारी", 32, "🤝"),
    ("Mixture & Alligation", "मिश्रण", 3, "🧪"), ("Average", "औसत", 93, "📊"),
    ("Problems on Age", "आयु संबंधी प्रश्न", 43, "🎂"), ("Time & Work", "समय एवं कार्य", 88, "🛠️"),
    ("Pipe & Cistern", "पाइप एवं टंकी", 31, "🚰"), ("Time, Speed & Distance", "समय, चाल एवं दूरी", 89, "🚆"),
    ("Boat & Stream", "नाव एवं धारा", 12, "⛵"), ("Race", "दौड़", 7, "🏃"),
    ("Mensuration", "क्षेत्रमिति", 89, "📏"), ("Geometry", "ज्यामिति", 103, "📐"),
    ("Trigonometry", "त्रिकोणमिति", 35, "📐"), ("Height & Distance", "ऊँचाई एवं दूरी", 16, "🗼"),
    ("Statistics", "सांख्यिकी", 73, "📉"), ("Venn Diagram", "वेन आरेख", 5, "⭕"),
    ("Statement Based Questions", "कथन आधारित प्रश्न", 20, "📝"),
]

QCOL = [("#e91e63", "#fde4ee"), ("#7c3aed", "#efe7ff"), ("#0284c7", "#e0f2fe"), ("#f97316", "#ffedd5")]
OPTC = ["#e91e63", "#7c3aed", "#0284c7", "#f97316"]
LETTERS = "ABCD"

CSS = """
@font-face { font-family: ARSans; src: url("FONTDIR/FreeSans.ttf"); }
@font-face { font-family: ARSans; font-weight: bold; src: url("FONTDIR/FreeSansBold.ttf"); }
@font-face { font-family: ARSerif; src: url("FONTDIR/FreeSerif.ttf"); }
@font-face { font-family: ARSerif; font-style: italic; src: url("FONTDIR/FreeSerifItalic.ttf"); }
* { box-sizing: border-box; }
body { margin:0; font-family: ARSans, sans-serif; font-size:13pt; line-height:1.42; color:#262a35; }
i { font-family: ARSerif, serif; }
.page { page-break-after: always; }
.grad { background: linear-gradient(115deg,#e91e63 0%,#7c3aed 50%,#0284c7 100%); color:#fff; }
/* cover */
.cover { height:262mm; border-radius:22px; padding:22mm 18mm; display:flex; flex-direction:column; justify-content:center; text-align:center; }
.cover .brand { align-self:center; background:#ffd23f; color:#3b1d6e; font-weight:bold; letter-spacing:4px; padding:7px 22px; border-radius:30px; font-size:14pt; }
.cover h1 { font-size:42pt; line-height:1.1; margin:16mm 0 5mm; }
.cover .sub { font-size:17pt; } .cover .hi { font-size:16pt; margin-top:3mm; opacity:.95; }
.cover .chips { margin-top:12mm; display:flex; gap:10px; justify-content:center; flex-wrap:wrap; }
.cover .chip { background:#ffffff26; border:1.5px solid #ffffff99; border-radius:20px; padding:5px 14px; font-size:11pt; }
.cover .big { margin-top:14mm; font-size:34pt; font-weight:bold; color:#ffd23f; }
/* index + about */
.sec { font-size:20pt; font-weight:bold; color:#1b1f2b; margin:0 0 4px; } .bar { width:50px; height:5px; border-radius:4px; margin-bottom:16px; }
.idx { display:grid; grid-template-columns:1fr 1fr; gap:8px 14px; }
.ix { display:flex; align-items:center; gap:10px; padding:7px 10px; border-radius:12px; background:var(--s); }
.ix .no { width:30px; height:30px; border-radius:9px; background:var(--c); color:#fff; font-weight:bold; display:flex; align-items:center; justify-content:center; font-size:10pt; flex:0 0 30px; }
.ix .t { flex:1; font-size:10pt; line-height:1.3; } .ix .t b { display:block; font-size:10.5pt; } .ix .c { font-weight:bold; color:var(--c); font-size:10pt; }
.box { border-radius:14px; padding:12px 16px; margin-bottom:12px; background:var(--s); border-left:5px solid var(--c); }
.box h3 { margin:0 0 4px; color:var(--c); font-size:12.5pt; }
/* chapter */
.chap { height:250mm; display:flex; flex-direction:column; justify-content:center; align-items:center; text-align:center; }
.chap .card { border-radius:26px; padding:20mm 16mm; width:100%; }
.chap .tno { letter-spacing:5px; font-weight:bold; font-size:10pt; opacity:.9; } .chap .ico { font-size:44pt; margin-top:6mm; }
.chap h1 { font-size:38pt; margin:2mm 0 1mm; } .chap .hi { font-size:22pt; }
.chap .cnt { margin-top:12mm; display:flex; gap:12px; justify-content:center; }
.chap .cnt div { background:#ffd23f; color:#3b1d6e; border-radius:14px; padding:8px 18px; font-weight:bold; }
.lvl { border-radius:14px; padding:9px 16px; margin:0; font-weight:bold; display:flex; justify-content:space-between; align-items:center; }
.lvl span:last-child { background:#ffd23f; color:#3b1d6e; border-radius:10px; padding:1px 10px; }
/* question */
.q { break-inside:avoid; border:2px solid var(--s); border-radius:16px; padding:9px 12px; display:flex; flex-direction:column; gap:6px; }
.sheet { height:262mm; display:flex; flex-direction:column; gap:4mm; page-break-after:always; }
.sheet.long { height:auto; }
.q.fill { flex:1; justify-content:space-around; }
.sheet .lvl { margin:0; }
#measure { width:180mm; } #measure .q { margin-bottom:4mm; }
.qt { display:flex; gap:14px; }
.n { flex:0 0 40px; height:40px; border-radius:12px; background:var(--c); color:#fff; font-weight:bold; display:flex; align-items:center; justify-content:center; font-size:12.5pt; box-shadow:0 3px 0 var(--d); }
.tag { display:inline-block; background:var(--s); color:var(--c); font-weight:bold; font-size:10.5pt; border-radius:20px; padding:0 10px; margin-bottom:3px; }
.en { font-weight:bold; color:#1b1f2b; } .hi2 { color:#5a5f6b; margin-top:3px; }
.os { display:grid; grid-template-columns:1fr 1fr; gap:6px 14px; margin:0 0 0 54px; }
.o { display:flex; gap:10px; align-items:center; padding:4px 12px; border:2px solid #eceef3; border-radius:12px; background:#fff; }
.l { width:26px; height:26px; border-radius:50%; color:#fff; font-weight:bold; font-size:11.5pt; display:flex; align-items:center; justify-content:center; flex:0 0 26px; }
.ans { margin:0 0 0 54px; font-weight:bold; color:#1b1f2b; }
.ans span { display:inline-block; background:var(--s); color:var(--c); border:2px solid var(--c); border-radius:10px; padding:1px 12px; }
.s { margin-left:54px; padding:8px 14px; background:var(--s); border-left:5px solid var(--c); border-radius:12px; }
.s .tl { font-size:11pt; letter-spacing:2px; font-weight:bold; color:var(--c); margin-bottom:3px; }
.tr { margin:0 0 0 54px; padding:6px 12px; background:#fff7cc; border-radius:10px; font-size:12.5pt; display:inline-block; }
.tr b { color:#c2410c; }
"""

DARK = {"#e91e63": "#a3134a", "#7c3aed": "#5523b0", "#0284c7": "#015e8c", "#f97316": "#b8520c"}


def strip_tags(s):
    return re.sub(r"<[^>]+>", "", s)


def q_html(q, k):
    c, s = QCOL[k % 4]
    long_opt = any(len(strip_tags(o)) > 55 for o in q["opts"])
    opts = "".join(f'<div class="o"><span class="l" style="background:{OPTC[i]}">{LETTERS[i]}</span><span>{o}</span></div>'
                   for i, o in enumerate(q["opts"]))
    a = q["ans"]
    ans_txt = strip_tags(q["opts"][LETTERS.index(a)].split("<br>")[0]) if a in LETTERS else ""
    trick = f'<div class="tr"><b>⚡ याद रखो —</b> {q["trick"]}</div>' if q.get("trick") else ""
    return f"""<div class="q" style="--c:{c};--s:{s};--d:{DARK[c]}"><div class="qt"><div class="n">{q['n']}</div><div>
<span class="tag">RRB NTPC 2025-26 · {q['lvl']}</span><div class="en">{q['en']}</div><div class="hi2">{q['hi']}</div></div></div>
<div class="os"{' style="grid-template-columns:1fr"' if long_opt else ''}>{opts}</div>
<div class="ans">उत्तर: <span>विकल्प ({a}) {html.escape(ans_txt)}</span></div>
<div class="s"><div class="tl">💡 हल · SOLUTION</div>{q['sol']}</div>{trick}</div>"""


def front_pages():
    total = sum(t[2] for t in TOPICS)
    cover = f"""<div class="page"><div class="cover grad"><div class="brand">{BRAND.upper()}</div>
<h1>RRB NTPC<br>Maths PYQ</h1><div class="sub">2025-26 · CBT-1 · Graduate + Under Graduate</div>
<div class="hi">गणित · विषयवार पूर्व वर्ष प्रश्न · हर प्रश्न का आसान हल</div>
<div class="chips"><span class="chip">English + हिन्दी</span><span class="chip">{len(TOPICS)} Topics</span><span class="chip">💡 Step हल</span><span class="chip">⚡ याद रखो ट्रिक</span></div>
<div class="big">{total:,} प्रश्न</div></div></div>"""
    items = "".join(
        f'<div class="ix" style="--c:{QCOL[i % 4][0]};--s:{QCOL[i % 4][1]}"><div class="no">{i + 1:02d}</div>'
        f'<div class="t"><b>{ic} {en}</b>{hi}</div><div class="c">{c}</div></div>'
        for i, (en, hi, c, ic) in enumerate(TOPICS))
    index = f"""<div class="page"><div class="sec">Index · विषय-सूची</div><div class="bar grad"></div><div class="idx">{items}</div></div>"""
    about = f"""<div class="page"><div class="sec">पुस्तक परिचय · About</div><div class="bar grad"></div>
<div class="box" style="--c:#e91e63;--s:#fde4ee"><h3>📘 पुस्तक में क्या है</h3>RRB NTPC 2025-26 CBT-1 में पूछे गए {total:,} गणित प्रश्न — स्नातक (GL) और स्नातक-पूर्व (UG) दोनों स्तर, {len(TOPICS)} टॉपिक में टॉपिकवार।</div>
<div class="box" style="--c:#7c3aed;--s:#efe7ff"><h3>🧭 उपयोग कैसे करें</h3>• हर प्रश्न: ऊपर English, नीचे हिन्दी<br>• पहले खुद हल करें, फिर नीचे "उत्तर" और "💡 हल" से मिलाएँ<br>• "⚡ याद रखो" वाली लाइन परीक्षा से पहले दोहराएँ<br>• GL / UG टैग परीक्षा का स्तर बताता है</div>
<div class="box" style="--c:#0284c7;--s:#e0f2fe"><h3>✍️ {BRAND}</h3>प्रतियोगी परीक्षाओं के लिए नोट्स, PYQ और प्रैक्टिस सामग्री।</div></div>"""
    return cover + index + about


def chapter_pages(d):
    c = d["chapter"]
    ic = TOPICS[c["no"] - 1][3] if c["no"] <= len(TOPICS) else "📘"
    cnt = f"<div>{c['total']} PYQs</div>" + (f"<div>GL · {c['gl']}</div>" if c["gl"] else "") + (f"<div>UG · {c['ug']}</div>" if c["ug"] else "")
    out = f"""<div class="page"><div class="chap"><div class="card grad"><div class="tno">TOPIC {c['no']:02d} / {len(TOPICS)}</div><div class="ico">{ic}</div>
<h1>{c['en']}</h1><div class="hi">{c['hi']}</div><div class="cnt">{cnt}</div></div></div></div>"""
    items, lvl = [], None  # ("lvl", html) ya ("q", html)
    for k, q in enumerate(d["questions"]):
        if q["lvl"] != lvl:
            lvl = q["lvl"]
            name = "Graduate Level · स्नातक स्तर" if lvl == "GL" else "Under Graduate Level · स्नातक-पूर्व स्तर"
            items.append(("lvl", f'<div class="lvl grad"><span>{ic} {c["en"]} · {lvl} · {name}</span><span>{c["gl"] if lvl == "GL" else c["ug"]} Qs</span></div>'))
        items.append(("q", q_html(q, k)))
    return out, items


PAGE_MM, GAP_MM, PX_MM = 262, 4, 96 / 25.4
MIN_ZOOM = 0.93  # isse chhota nahi (13pt x 0.93 = ~12pt)


def pack(items, h):
    """Har page par 2 sawaal; dono na samayein to 1. h = har item ki naap (mm)."""
    pages, i = [], 0
    while i < len(items):
        top = []
        while i < len(items) and items[i][0] == "lvl":
            top.append(items[i][1]); i += 1
        used = sum(h[x] for x in top) + GAP_MM * len(top)
        qs, zoom = [], 1.0
        while i < len(items) and items[i][0] == "q" and len(qs) < 2:
            need = h[items[i][1]] + (GAP_MM if qs else 0)
            if qs and used + need > PAGE_MM:
                if (used + need) * MIN_ZOOM <= PAGE_MM:  # thoda chhota karke dono sawaal ek page par
                    zoom = max(MIN_ZOOM, PAGE_MM / (used + need) - 0.005)
                else:
                    break
            qs.append(items[i][1]); used += need; i += 1
        cls = "sheet" if used * zoom <= PAGE_MM else "sheet long"
        cards = [x.replace('class="q"', 'class="q fill"', 1) for x in qs] if len(qs) == 2 else qs
        st = f' style="zoom:{zoom:.3f};height:{PAGE_MM / zoom:.1f}mm"' if zoom < 1 else ""
        pages.append(f'<div class="{cls}"{st}>{"".join(top)}{"".join(cards)}</div>')
    return "".join(pages)


def main():
    files = sorted(glob.glob(os.path.join(HERE, "data", "*.json")))
    if not files:
        sys.exit("data/*.json nahi mila")
    body = front_pages()
    chapters = {}  # ek chapter kai files mein ho sakta hai -> jod kar ek saath
    for f in files:
        d = json.load(open(f, encoding="utf-8"))
        c = chapters.setdefault(d["chapter"]["no"], {"chapter": d["chapter"], "questions": {}})
        for q in d["questions"]:
            c["questions"][q["n"]] = q
    parts = []
    for no in sorted(chapters):
        c = chapters[no]
        parts.append(chapter_pages({"chapter": c["chapter"], "questions": [c["questions"][n] for n in sorted(c["questions"])]}))
    css = CSS.replace("FONTDIR", "file://" + FONT_DIR)
    wrap = lambda b: f'<!doctype html><html lang="hi"><head><meta charset="utf-8"><style>{css}</style></head><body>{b}</body></html>'
    os.makedirs(OUT, exist_ok=True)
    html_path = os.path.join(OUT, "book.html")
    allitems = [x for _, its in parts for x in its]
    open(html_path, "w", encoding="utf-8").write(wrap('<div id="measure">' + "".join(x[1] for x in allitems) + "</div>"))
    pdf_path = os.path.join(OUT, "RRB_NTPC_Maths_PYQ_Solutions_AR_Publication.pdf")
    head = f'<div style="font-size:8px;width:100%;padding:0 15mm;display:flex;justify-content:space-between;color:#7c3aed;font-family:sans-serif"><b>{TITLE}</b><b>{BRAND}</b></div>'
    foot = f'<div style="font-size:8px;width:100%;padding:0 15mm;display:flex;justify-content:space-between;color:#777;font-family:sans-serif"><span>© {BRAND}</span><span><span class="pageNumber"></span> / <span class="totalPages"></span></span></div>'
    with sync_playwright() as p:
        try:
            b = p.chromium.launch()
        except Exception:  # runner par pehle se laga Google Chrome
            b = p.chromium.launch(channel="chrome")
        pg = b.new_page()
        pg.emulate_media(media="print")
        pg.goto("file://" + html_path)
        pg.wait_for_timeout(300)
        hs = pg.evaluate("Array.from(document.querySelectorAll('#measure > div')).map(e => e.getBoundingClientRect().height)")
        h = {x[1]: px / PX_MM for x, px in zip(allitems, hs)}
        for cp, its in parts:
            body += cp + pack(its, h)
        open(html_path, "w", encoding="utf-8").write(wrap(body))
        pg.goto("file://" + html_path)
        pg.pdf(path=pdf_path, format="A4", print_background=True, display_header_footer=True,
               header_template=head, footer_template=foot,
               margin={"top": "16mm", "bottom": "16mm", "left": "15mm", "right": "15mm"})
        b.close()
    print("PDF:", pdf_path)


if __name__ == "__main__":
    main()
