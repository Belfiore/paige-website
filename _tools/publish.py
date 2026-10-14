#!/usr/bin/env python3
"""Copy the deployable site into docs/ with root-relative URLs prefixed for GitHub Pages.
Usage: python3 -I _tools/publish.py /repo-name"""
import os, re, shutil, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = sys.argv[1].rstrip("/")
OUT = os.path.join(ROOT, "docs")
shutil.rmtree(OUT, ignore_errors=True)
for item in ["assets", "index.html", "services", "consultation", "about", "therapy", "reiki", "supervision", "home", "favicon.ico"]:
    src = os.path.join(ROOT, item)
    (shutil.copytree if os.path.isdir(src) else shutil.copy)(src, os.path.join(OUT, item))
open(os.path.join(OUT, ".nojekyll"), "w").close()
for dp, _, fs in os.walk(OUT):
    for f in fs:
        if not f.endswith(".html"): continue
        p = os.path.join(dp, f); s = open(p, encoding="utf-8").read()
        s = re.sub(r'(href|src)="/(?!/)', lambda m: f'{m.group(1)}="{BASE}/', s)
        s = s.replace('content="0; url=/', f'content="0; url={BASE}/').replace('location.replace("/', f'location.replace("{BASE}/')
        open(p, "w", encoding="utf-8").write(s)
print("published to docs/ with base", BASE)
