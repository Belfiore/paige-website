"""Extract text, links, images, forms from saved Squarespace pages.
Usage: python3 -I extract.py <raw_dir> <out_dir>
"""
import sys, os, re, json
from html.parser import HTMLParser

BLOCK = {"p","h1","h2","h3","h4","h5","h6","li","blockquote","div","section","button","figcaption","label","legend","td","th","tr","ul","ol","header","footer","main","nav","form","article","summary","details"}
SKIP = {"script","style","noscript","template"}
VOID = {"img","br","input","meta","link","hr","source","area","base","col","embed","param","track","wbr"}

class P(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []          # tag names
        self.skip = 0
        self.svg = 0
        self.region = None       # header / main / footer
        self.lines = []          # (region, tag, text)
        self.cur = []
        self.cur_tag = None
        self.links = []          # (region, href, text, classes)
        self.images = []         # dicts
        self.forms = []
        self.inputs = []
        self.iframes = []
        self.cur_link = None
        self.cur_heading = None

    def flush(self):
        t = re.sub(r"\s+", " ", "".join(self.cur)).strip()
        if t:
            self.lines.append({"region": self.region, "tag": self.cur_tag or "", "text": t})
        self.cur = []
        self.cur_tag = None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag in SKIP:
            self.skip += 1
            return
        if tag == "svg":
            self.svg += 1
        if tag in ("header","main","footer") and self.region is None:
            self.region = tag
        if tag == "br":
            self.cur.append("\n")
        if tag in BLOCK:
            self.flush()
            self.cur_tag = tag
        if tag == "a":
            self.cur_link = {"region": self.region, "href": a.get("href",""), "text": [], "class": a.get("class",""), "target": a.get("target","")}
        if tag == "img":
            self.images.append({"region": self.region, "src": a.get("src",""), "data_src": a.get("data-src",""), "data_image": a.get("data-image",""), "alt": a.get("alt",""), "class": a.get("class",""), "w": a.get("data-image-dimensions",""), "focal": a.get("data-image-focal-point","")})
        st = a.get("style","")
        m = re.search(r"url\(['\"]?([^)'\"]+)['\"]?\)", st)
        if m and "background" in st:
            self.images.append({"region": self.region, "src": m.group(1), "data_src":"", "data_image":"", "alt":"(css background)", "class": a.get("class",""), "w":"", "focal":""})
        if tag == "form":
            self.forms.append({"region": self.region, "action": a.get("action",""), "method": a.get("method",""), "id": a.get("id",""), "class": a.get("class","")})
        if tag in ("input","textarea","select"):
            self.inputs.append({k: a.get(k,"") for k in ("type","name","placeholder","aria-label","id","required","autocomplete")} | {"tag": tag})
        if tag == "iframe":
            self.iframes.append({"src": a.get("src",""), "data_src": a.get("data-src",""), "title": a.get("title","")})
        if tag not in VOID:
            self.stack.append(tag)

    def handle_endtag(self, tag):
        if tag in SKIP:
            self.skip = max(0, self.skip-1)
            return
        if tag == "svg":
            self.svg = max(0, self.svg-1)
        if tag in BLOCK:
            self.flush()
        if tag == "a" and self.cur_link is not None:
            self.cur_link["text"] = re.sub(r"\s+"," "," ".join(self.cur_link["text"])).strip()
            self.links.append(self.cur_link)
            self.cur_link = None
        if tag in ("header","main","footer") and self.region == tag:
            self.region = None
        while self.stack:
            t = self.stack.pop()
            if t == tag:
                break

    def handle_data(self, data):
        if self.skip or self.svg:
            return
        self.cur.append(data)
        if self.cur_link is not None:
            self.cur_link["text"].append(data)

def run(raw, out):
    os.makedirs(out, exist_ok=True)
    summary = {}
    for f in sorted(os.listdir(raw)):
        if not f.endswith(".html"):
            continue
        html = open(os.path.join(raw,f), encoding="utf-8").read()
        p = P(); p.feed(html); p.flush()
        name = f[:-5]
        json.dump({"lines": p.lines, "links": p.links, "images": p.images, "forms": p.forms, "inputs": p.inputs, "iframes": p.iframes}, open(os.path.join(out, name+".json"),"w"), indent=1)
        with open(os.path.join(out, name+".txt"),"w") as fh:
            for l in p.lines:
                fh.write(f"[{l['region'] or '-'}|{l['tag']}] {l['text']}\n")
        summary[name] = {"lines": len(p.lines), "images": len(p.images), "forms": len(p.forms), "inputs": len(p.inputs), "iframes": len(p.iframes)}
    print(json.dumps(summary, indent=1))

if __name__ == "__main__":
    run(sys.argv[1], sys.argv[2])
