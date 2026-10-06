#!/usr/bin/env python3
import io
import json
import urllib.request
from html import escape
from pathlib import Path
from PIL import Image, ImageEnhance, ImageOps

ROOT = Path(__file__).resolve().parents[1]
data = json.loads((ROOT / "data" / "github.json").read_text(encoding="utf-8"))
avatar = data["user"]["avatar_url"]

req = urllib.request.Request(avatar, headers={"User-Agent": "AndreSchons-profile-readme"})
with urllib.request.urlopen(req, timeout=30) as r:
    img = Image.open(io.BytesIO(r.read())).convert("L")

img = ImageOps.autocontrast(img)
img = ImageEnhance.Contrast(img).enhance(1.45)

cols = 52
aspect = img.height / img.width
rows = max(28, int(cols * aspect * 0.48))
img = img.resize((cols, rows))

chars = "@%#*+=-:. "
pix = list(img.getdata())
lines = []
for y in range(rows):
    line = []
    for x in range(cols):
        v = pix[y*cols+x]
        idx = min(len(chars)-1, int(v / 256 * len(chars)))
        line.append(chars[idx])
    lines.append("".join(line).rstrip())

font = 8
line_h = 9
pad = 18
W = cols * 5 + pad*2
H = rows * line_h + pad*2 + 30

svg = [f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" role="img" aria-label="ASCII portrait">\n<style>\n  .bg {{ fill:#0d1117; }}\n  .art {{ fill:#c9d1d9; font:{font}px ui-monospace,SFMono-Regular,Menlo,Consolas,monospace; white-space:pre; }}\n  .prompt {{ fill:#39d353; font:11px ui-monospace,SFMono-Regular,Menlo,Consolas,monospace; }}\n  .row {{ opacity:0; animation:type .08s linear forwards; }}\n  @keyframes type {{ to {{ opacity:1; }} }}\n</style>\n<rect class="bg" width="100%" height="100%" rx="14"/>\n<text x="{pad}" y="22" class="prompt">andre@github:~$ cat avatar.ascii</text>\n''']

start_y = 42
for i, line in enumerate(lines):
    svg.append(f'<text class="art row" style="animation-delay:{i*0.025:.3f}s" x="{pad}" y="{start_y+i*line_h}">{escape(line)}</text>')

svg.append('</svg>')
(ROOT / "andre-ascii.svg").write_text("\n".join(svg), encoding="utf-8")
print("Wrote andre-ascii.svg")
