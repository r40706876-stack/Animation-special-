"""AR Publication - RRB NTPC Maths PYQ (with solutions) PDF builder.

Reads every data/*.json file (in name order) and writes out/RRB_NTPC_Maths_PYQ_Solutions_AR_Publication.pdf
Usage:  python ar_publication/ntpc_maths/build_pdf.py
Needs:  playwright (chromium) + a Devanagari font (fonts-noto-core on Ubuntu)
"""
import glob, html, json, os, re, sys
from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
BRAND = "AR Publication"
TITLE = "RRB NTPC 2025-26 | Maths PYQ (GL + UG) | With Solutions"

TOPICS = [
    ("Number System", "संख्या पद्धति", 87), ("LCM & HCF", "लघुत्तम एवं महत्तम समापवर्तक", 50),
    ("Simplification", "सरलीकरण", 130), ("Algebra", "बीजगणित", 112),
    ("Quadratic Equations", "द्विघात समीकरण", 7), ("Percentage", "प्रतिशत", 100),
    ("Profit & Loss", "लाभ एवं हानि", 102), ("Discount", "बट्टा / छूट", 101),
    ("Simple Interest", "साधारण ब्याज", 59), ("Compound Interest", "चक्रवृद्धि ब्याज", 52),
    ("Ratio & Proportion", "अनुपात एवं समानुपात", 140), ("Partnership", "साझेदारी", 32),
    ("Mixture & Alligation", "मिश्रण", 3), ("Average", "औसत", 93),
    ("Problems on Age", "आयु संबंधी प्रश्न", 43), ("Time & Work", "समय एवं कार्य", 88),
    ("Pipe & Cistern", "पाइप एवं टंकी", 31), ("Time, Speed & Distance", "समय, चाल एवं दूरी", 89),
    ("Boat & Stream", "नाव एवं धारा", 12), ("Race", "दौड़", 7),
    ("Mensuration", "क्षेत्रमिति", 89), ("Geometry", "ज्यामिति", 103),
    ("Trigonometry", "त्रिकोणमिति", 35), ("Height & Distance", "ऊँचाई एवं दूरी", 16),
    ("Statistics", "सांख्यिकी", 73), ("Venn Diagram", "वेन आरेख", 5),
    ("Statement Based Questions", "कथन आधारित प्रश्न", 20),
]

CSS = """
@page { size: A4; margin: 14mm 12mm 16mm; }
* { box-sizing: border-box; }
body { font-family: "Noto Sans", "Noto Sans Devanagari", "FreeSans", sans-serif; color:#1b1f2a; font-size:11.2pt; line-height:1.42; margin:0; }
i { font-family: "Noto Serif", "FreeSerif", serif; }
.page { page-break-after: always; }
.cover { height: 265mm; display:flex; flex-direction:column; justify-content:center; align-items:center; text-align:center;
  background: linear-gradient(160deg,#0f2d6b 0%,#1f4fb5 60%,#2e6be6 100%); color:#fff; border-radius:14px; padding:20mm; }
.cover .brand { font-size:16pt; letter-spacing:4px; font-weight:bold; background:#ffc83d; color:#0f2d6b; padding:6px 22px; border-radius:30px; }
.cover h1 { font-size:40pt; margin:16mm 0 4mm; line-height:1.1; }
.cover h2 { font-size:20pt; margin:0 0 4mm; font-weight:normal; }
.cover .hi { font-size:17pt; margin-bottom:12mm; }
.cover .chips { display:flex; gap:10px; flex-wrap:wrap; justify-content:center; }
.cover .chip { border:1.5px solid #ffffffaa; border-radius:20px; padding:5px 14px; font-size:11.5pt; }
.cover .big { font-size:30pt; font-weight:bold; color:#ffc83d; margin-top:14mm; }
h2.sec { color:#0f2d6b; border-bottom:3px solid #ffc83d; padding-bottom:4px; margin:0 0 8px; font-size:17pt; }
table.idx { width:100%; border-collapse:collapse; font-size:10.5pt; }
table.idx td { padding:4px 6px; border-bottom:1px solid #e3e8f4; }
table.idx td.n { color:#1f4fb5; font-weight:bold; width:28px; }
table.idx td.c { text-align:right; color:#555; white-space:nowrap; }
.box { border:1px solid #c9d3ea; border-radius:10px; padding:10px 14px; margin-bottom:10px; }
.box h3 { margin:0 0 6px; color:#1f4fb5; font-size:12.5pt; }
.chap { height:250mm; display:flex; flex-direction:column; justify-content:center; align-items:center; text-align:center; }
.chap .tno { color:#1f4fb5; letter-spacing:5px; font-weight:bold; }
.chap h1 { font-size:36pt; color:#0f2d6b; margin:6mm 0 2mm; }
.chap .hi { font-size:22pt; color:#333; }
.chap .cnt { margin-top:10mm; display:flex; gap:12px; }
.chap .cnt div { border:2px solid #1f4fb5; border-radius:10px; padding:8px 16px; font-weight:bold; color:#0f2d6b; }
.lvl { background:#0f2d6b; color:#fff; border-radius:8px; padding:6px 12px; margin:4px 0 10px; font-weight:bold; display:flex; justify-content:space-between; }
.q { border:1px solid #c9d3ea; border-radius:9px; padding:8px 11px; margin-bottom:9px; page-break-inside: avoid; }
.qn { display:inline-block; background:#1f4fb5; color:#fff; font-weight:bold; border-radius:4px; padding:1px 8px; font-size:10pt; }
.tag { display:inline-block; background:#e8edf8; color:#1f4fb5; font-weight:bold; border-radius:4px; padding:1px 6px; font-size:9pt; margin-left:4px; }
.en { font-weight:bold; margin-top:4px; }
.hi2 { margin-top:2px; }
.opts { display:grid; grid-template-columns: repeat(4, 1fr); gap:5px; margin:6px 0; }
.opts.two { grid-template-columns: repeat(2, 1fr); }
.opt { border:1px solid #dde3f0; border-radius:5px; padding:3px 7px; display:flex; gap:7px; align-items:baseline; }
.opt b { color:#1f4fb5; }
.opt.ok { background:#e6f6ea; border-color:#43a047; }
.sol { background:#fff8e6; border-left:4px solid #f0a500; padding:5px 9px; border-radius:4px; font-size:10.7pt; }
.sol .ans { color:#1b7f3a; font-weight:bold; white-space:nowrap; }
"""

LETTERS = "ABCD"


def strip_tags(s):
    return re.sub(r"<[^>]+>", "", s)


def q_html(q):
    long_opt = any(len(strip_tags(o)) > 14 or "<br>" in o for o in q["opts"])
    opts = "".join(
        f'<div class="opt{" ok" if LETTERS[i] == q["ans"] else ""}"><b>{LETTERS[i]}</b><span>{o}</span></div>'
        for i, o in enumerate(q["opts"]))
    ans_txt = strip_tags(q["opts"][LETTERS.index(q["ans"])].split("<br>")[0])
    return f"""<div class="q"><span class="qn">Q.{q['n']}</span><span class="tag">{q['lvl']}</span>
<div class="en">{q['en']}</div><div class="hi2">{q['hi']}</div>
<div class="opts{' two' if long_opt else ''}">{opts}</div>
<div class="sol"><b>हल:</b> {q['sol']} &nbsp;<span class="ans">उत्तर: ({q['ans']}) {html.escape(ans_txt)}</span></div></div>"""


def front_pages():
    total = sum(t[2] for t in TOPICS)
    cover = f"""<div class="page"><div class="cover"><div class="brand">{BRAND.upper()}</div>
<h1>RRB NTPC<br>Maths PYQ</h1><h2>2025-26 · CBT-1 · Graduate + Under Graduate</h2>
<div class="hi">गणित · विषयवार पूर्व वर्ष प्रश्न · हल सहित</div>
<div class="chips"><span class="chip">Bilingual · English + हिन्दी</span><span class="chip">{len(TOPICS)} Topics</span><span class="chip">हर प्रश्न का आसान हल</span></div>
<div class="big">{total:,} प्रश्न</div></div></div>"""
    rows = "".join(f'<tr><td class="n">{i+1:02d}</td><td>{en} / {hi}</td><td class="c">{c} Qs</td></tr>'
                   for i, (en, hi, c) in enumerate(TOPICS))
    index = f"""<div class="page"><h2 class="sec">Index / विषय-सूची</h2><table class="idx">{rows}</table></div>"""
    about = f"""<div class="page"><h2 class="sec">About this Book / पुस्तक परिचय</h2>
<div class="box"><h3>📘 पुस्तक में क्या है</h3>RRB NTPC 2025-26 CBT-1 में पूछे गए {total:,} गणित प्रश्न, स्नातक (GL) और स्नातक-पूर्व (UG) दोनों स्तर, {len(TOPICS)} टॉपिक में टॉपिकवार।<br>
{total:,} Maths questions asked in RRB NTPC 2025-26 CBT-1 (GL + UG), arranged topic-wise.</div>
<div class="box"><h3>🧭 उपयोग कैसे करें</h3>• हर प्रश्न: ऊपर अंग्रेज़ी, नीचे हिन्दी<br>• सही विकल्प <b style="color:#1b7f3a">हरे रंग</b> में है<br>
• हर प्रश्न के नीचे छोटा और आसान हल दिया गया है — पहले खुद हल करें, फिर मिलाएँ<br>• GL / UG टैग परीक्षा का स्तर बताता है</div>
<div class="box"><h3>✍️ {BRAND}</h3>प्रतियोगी परीक्षाओं के लिए नोट्स, PYQ और प्रैक्टिस सामग्री।</div></div>"""
    return cover + index + about


def chapter_pages(d):
    c = d["chapter"]
    out = f"""<div class="page"><div class="chap"><div class="tno">TOPIC {c['no']:02d} / {len(TOPICS)}</div>
<h1>{c['en']}</h1><div class="hi">{c['hi']}</div>
<div class="cnt"><div>{c['total']} PYQs</div><div>GL · {c['gl']}</div><div>UG · {c['ug']}</div></div></div></div>"""
    lvl = None
    for q in d["questions"]:
        if q["lvl"] != lvl:
            lvl = q["lvl"]
            name = "Graduate Level · स्नातक स्तर" if lvl == "GL" else "Under Graduate Level · स्नातक-पूर्व स्तर"
            n = c["gl"] if lvl == "GL" else c["ug"]
            out += f'<div class="lvl"><span>{lvl} · {name}</span><span>{n} Qs</span></div>'
        out += q_html(q)
    return out


def main():
    files = sorted(glob.glob(os.path.join(HERE, "data", "*.json")))
    if not files:
        sys.exit("data/*.json nahi mila")
    body = front_pages()
    seen = set()
    for f in files:
        d = json.load(open(f, encoding="utf-8"))
        if d["chapter"]["no"] in seen:  # same chapter split in many files: no new title page
            d = dict(d); body += "".join(q_html(q) for q in d["questions"]); continue
        seen.add(d["chapter"]["no"])
        body += chapter_pages(d)
    doc = f'<!doctype html><html lang="hi"><head><meta charset="utf-8"><style>{CSS}</style></head><body>{body}</body></html>'
    os.makedirs(OUT, exist_ok=True)
    html_path = os.path.join(OUT, "book.html")
    open(html_path, "w", encoding="utf-8").write(doc)
    pdf_path = os.path.join(OUT, "RRB_NTPC_Maths_PYQ_Solutions_AR_Publication.pdf")
    head = f'<div style="font-size:8px;width:100%;padding:0 12mm;display:flex;justify-content:space-between;color:#0f2d6b;font-family:sans-serif"><b>{TITLE}</b><b>{BRAND}</b></div>'
    foot = f'<div style="font-size:8px;width:100%;padding:0 12mm;display:flex;justify-content:space-between;color:#555;font-family:sans-serif"><span>© {BRAND}</span><span>Page <span class="pageNumber"></span> / <span class="totalPages"></span></span></div>'
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page()
        pg.goto("file://" + html_path)
        pg.pdf(path=pdf_path, format="A4", print_background=True, display_header_footer=True,
               header_template=head, footer_template=foot,
               margin={"top": "14mm", "bottom": "16mm", "left": "12mm", "right": "12mm"})
        b.close()
    print("PDF:", pdf_path)


if __name__ == "__main__":
    main()
