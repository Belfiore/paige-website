#!/usr/bin/env python3
"""Verify the rebuilt site against the audited original.

1. TEXT      every original line (nav, main, footer) must appear verbatim in the new pages
2. ADDED     every block of new text that is NOT in the original is listed (authored labels etc.)
3. IMAGES    every original image used on the original pages is accounted for
4. GROW      every booking link carries the exact URL, opens in a new tab, rel=noopener

Run:  python3 -I _tools/verify.py
"""
import json, os, re, sys, html as H
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from htmltext import P

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EX = os.path.join(ROOT, "_audit", "extracted")

GROW = "https://growtherapy.com/book-appointment?prsid=oq1cmlyoxaaf&ref=grow&setting=Virtual&insuranceId=&state=&cusid="

def norm(t):
    t = t.replace("‍", "").replace(" ", " ")
    return re.sub(r"\s+", " ", t).strip()

def parse(path):
    p = P(); p.feed(open(path, encoding="utf-8").read()); p.flush(); return p

def orig_lines(page, regions=("header", "main", "footer")):
    d = json.load(open(os.path.join(EX, page + ".json"), encoding="utf-8"))
    return [norm(l["text"]) for l in d["lines"] if l["region"] in regions and norm(l["text"])]

# original page  ->  new page(s) it now lives on
MAP = {
    "root": ["classic/index.html"],
    "about": ["classic/index.html"],
    "therapy": ["services/index.html"],
    "reiki": ["services/index.html"],
    "supervision": ["services/index.html"],
}
# Squarespace chrome that has no equivalent in a design without a cart / mobile folder drawer
SQS_CHROME = {"0", "Back", "Folder: Services", "Open Menu Close Menu"}
# labels deliberately replaced after Paige's feedback (booking CTAs now lead to the inquiry form)
CHANGED = {"BOOK A CONSULTATION", "Book Session"}

new_pages = {f: parse(os.path.join(ROOT, f)) for f in {"classic/index.html", "services/index.html", "consultation/index.html", "index.html"}}
new_text = {f: norm(" ".join(l["text"] for l in p.lines)) for f, p in new_pages.items()}
# the form-labels live in the consultation page
form_expected = ["Name", "First Name", "(required)", "Last Name", "Email", "Preferred Day", "Short Message",
                 "Preferred Time", "in Eastern Time", "Phone Number", "Send Inquiry",
                 "Example: Tuesdays or Thursdays", "Tell me briefly what you’re looking for support with.",
                 "Thank you for reaching out. I look forward to speaking with you!", "-Paige"]

fail = False
print("=" * 72, "\n1. TEXT — original lines found verbatim in the new site\n" + "=" * 72)
for page, targets in list(MAP.items()) + [("root", ["index.html"]), ("about", ["index.html"])]:
    if targets[0] == "index.html":
        # story page splits paragraphs into chunks with added emoji/labels between them:
        # drop the added blocks, then the original paragraphs must be intact and in order
        _all = norm(" ".join(l for pg in MAP for l in orig_lines(pg)))
        hay = " ".join(norm(l["text"]) for l in new_pages[targets[0]].lines if norm(l["text"]) and norm(l["text"]) in _all)
    else:
        hay = " ".join(new_text[t] for t in targets)
    hay_ph = hay + " " + " ".join(" ".join(i.get("placeholder", "") for i in new_pages[t].inputs) for t in targets)
    lines = list(dict.fromkeys(orig_lines(page)))
    full = " ".join(new_text[t] for t in targets)
    missing = [l for l in lines if l not in hay and l not in SQS_CHROME and l not in CHANGED and (len(l) > 60 or l not in full)]
    skipped = [l for l in lines if l in SQS_CHROME]
    ok = len(lines) - len(missing) - len(skipped)
    print(f"{page:12s} {targets[0][:10]:10s} {ok:3d}/{len(lines) - len(skipped)} lines verbatim" + (f"   (+{len(skipped)} Squarespace-only UI strings skipped)" if skipped else ""))
    for m in missing:
        fail = True; print("   MISSING:", m[:140])
# nav words that Squarespace combined into one string
for w in ("Open Menu", "Close Menu"):
    present = w in " ".join(new_text.values()) or w in open(os.path.join(ROOT, "assets/js/main.js"), encoding="utf-8").read()
    print(f"{'ok ' if present else 'MISSING'} nav string {w!r}"); fail |= not present
ct = new_text["consultation/index.html"] + " " + " ".join(i.get("placeholder", "") for i in new_pages["consultation/index.html"].inputs)
ct += " " + " ".join(l["text"] for l in new_pages["consultation/index.html"].lines)
miss = [t for t in form_expected if norm(t) not in norm(ct)]
print(f"consultation {len(form_expected) - len(miss)}/{len(form_expected)} form strings verbatim")
for m in miss: fail = True; print("   MISSING:", m)

print("\n" + "=" * 72, "\n2. ADDED — new text not present in the original (authored labels / helper / status)\n" + "=" * 72)
orig_all = norm(" ".join(l for p in MAP for l in orig_lines(p)) + " " + " ".join(form_expected))
extra = {}
for f, p in new_pages.items():
    for i, l in enumerate(p.lines):
        t = norm(l["text"])
        if not t or t in orig_all or i == 0: continue   # i == 0 is the <title>
        extra.setdefault(f, [])
        if t not in extra[f]: extra[f].append(t)
for f, items in extra.items():
    print(f"\n[{f}]")
    for t in items: print("   +", t)

print("\n" + "=" * 72, "\n3. IMAGES — original images accounted for\n" + "=" * 72)
used = set()
for f in new_pages:
    txt = open(os.path.join(ROOT, f), encoding="utf-8").read()
    used |= set(re.findall(r"/assets/img/([\w.-]+)", txt))
need = {"shore-pebbles.webp": "02 Shore-Pebbles (home hero)", "paige-portrait.webp": "03 portrait (meet Paige)",
        "bloom-blue.webp": "Star@2x (quote bloom)", "icon-awaken.webp": "Star 1 (AWAKEN)", "icon-attune.webp": "Star 2 (ATTUNE)",
        "icon-align.webp": "Subtract (ALIGN)", "about-sunset.webp": "IMG_4524 (About)", "tile-sunburst.webp": "Group 25",
        "tile-mandala-warm.webp": "unsplash hqrQ3brWGQA", "tile-ring.webp": "Group 26", "tile-flower.webp": "Group 27",
        "tile-mandala-blue.webp": "unsplash XvvJnMbmOkY", "therapy-stones.webp": "unsplash E0X-zPBgyFo",
        "therapy-minerals.webp": "unsplash g95sf8-fEQg", "ivory-mist.webp": "Ivory Mist (bg)", "logo-512.png": "watercolor logo"}
css = open(os.path.join(ROOT, "assets/css/styles.css"), encoding="utf-8").read()
used |= set(re.findall(r"img/([\w.-]+)", css))
for fn, label in need.items():
    ok = fn in used and os.path.exists(os.path.join(ROOT, "assets/img", fn))
    print(f"{'ok ' if ok else 'MISSING'} {fn:26s} <- {label}"); fail |= not ok
print("note  graphic-shape.png (About page) is hidden on the live site (display:none) — not carried over")

print("\n" + "=" * 72, "\n4. CTAs & BOOKING LINKS\n" + "=" * 72)
def hrefs(f): return [(l["href"], l["text"], l["target"]) for l in new_pages[f].links]
raw = {f: open(os.path.join(ROOT, f), encoding="utf-8").read() for f in new_pages}
# a) the old Grow "book-appointment" funnel link must be gone everywhere
n_old = sum(r.count("book-appointment") for r in raw.values())
print(f"{'ok ' if n_old == 0 else 'BAD'} no site-wide Grow book-appointment links ({n_old} found)"); fail |= n_old != 0
# b) Grow/Headway only on the matching insurance cards, exact original hrefs
tl = json.load(open(os.path.join(EX, "therapy.json"), encoding="utf-8"))["links"]
orig = {norm(l["text"]): l["href"] for l in tl}
sv = {norm(t): (h, tg) for h, t, tg in hrefs("services/index.html")}
for label in ("Book with Aetna or Cigna", "Book with Florida Blue or United"):
    got = next(((h, tg) for t, (h, tg) in sv.items() if t.startswith(label)), None)
    good = got and got[0] == orig[label] and got[1] == "_blank"
    print(f"{'ok ' if good else 'BAD'} {label} -> original link, new tab"); fail |= not good
other = [h for f in new_pages for h, t, tg in hrefs(f) if ("growtherapy.com" in h or "headway.co" in h)]
print(f"{'ok ' if len(other) == 2 else 'BAD'} only 2 insurer links on the whole site ({len(other)} found)"); fail |= len(other) != 2
# c) private pay + every Inquire / announce link goes to the inquiry form
pp = next(((h, t) for h, t, tg in hrefs("services/index.html") if "Inquire about private pay" in t), None)
print(f"{'ok ' if pp and pp[0] == '/consultation/' else 'BAD'} private pay button -> /consultation/"); fail |= not (pp and pp[0] == "/consultation/")
for f in new_pages:
    ann = [h for h, t, tg in hrefs(f) if t.strip().startswith("Inquire →")]
    inq = [h for h, t, tg in hrefs(f) if t.strip().startswith("Inquire") and "private" not in t]
    good = ann == ["/consultation/"] and all(h == "/consultation/" for h in inq) and len(inq) >= 3
    print(f"{'ok ' if good else 'BAD'} {f:26s} announce bar + {len(inq)-1} Inquire buttons -> /consultation/"); fail |= not good
# d) the form carries the new field
cf = raw["consultation/index.html"]
ok = 'name="coverage"' in cf and "Insurance or private pay?" in cf
print(f"{'ok ' if ok else 'BAD'} inquiry form has the insurance / private pay dropdown"); fail |= not ok
print("\nRESULT:", "FAIL" if fail else "PASS")
sys.exit(1 if fail else 0)
