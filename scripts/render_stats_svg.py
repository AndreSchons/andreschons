#!/usr/bin/env python3
import json
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
g = json.loads((ROOT / "data" / "github.json").read_text(encoding="utf-8"))
p = json.loads((ROOT / "data" / "profile_info.json").read_text(encoding="utf-8"))

u = g["user"]
c = g["contributions"]
calendar = c["contributionCalendar"]

metrics = [
    ("repos", u["repositories"]),
    ("followers", u["followers"]),
    ("contribs", calendar["totalContributions"]),
    ("commits", c["totalCommitContributions"]),
    ("pull reqs", c["totalPullRequestContributions"]),
    ("reviews", c["totalPullRequestReviewContributions"]),
]

W, H = 670, 430
cols = 2
card_w, card_h = 290, 72
sx, sy = 32, 168
gap_x, gap_y = 22, 16

svg = [f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" role="img" aria-label="GitHub stats">\n<style>\n  .bg {{ fill:#0d1117; }}\n  .h1 {{ fill:#f0f6fc; font:700 24px ui-monospace,SFMono-Regular,Menlo,Consolas,monospace; }}\n  .sub {{ fill:#8b949e; font:13px ui-monospace,SFMono-Regular,Menlo,Consolas,monospace; }}\n  .num {{ fill:#39d353; font:700 22px ui-monospace,SFMono-Regular,Menlo,Consolas,monospace; }}\n  .lab {{ fill:#c9d1d9; font:12px ui-monospace,SFMono-Regular,Menlo,Consolas,monospace; }}\n  .card {{ fill:#161b22; stroke:#30363d; stroke-width:1; }}\n  .line {{ opacity:0; animation:in .45s ease forwards; }}\n  @keyframes in {{ from {{ opacity:0; transform:translateY(8px); }} to {{ opacity:1; transform:translateY(0); }} }}\n</style>\n<rect class="bg" width="100%" height="100%" rx="14"/>\n<text x="32" y="46" class="h1">{escape(p["display_name"])}</text>\n<text x="32" y="72" class="sub">{escape(p["role"])} · {escape(p["company"])}</text>\n<text x="32" y="96" class="sub">{escape(p["location"])}</text>\n<text x="32" y="122" class="sub">{escape(p["focus"])}</text>\n''']

for i, (label, value) in enumerate(metrics):
    col = i % cols
    row = i // cols
    x = sx + col * (card_w + gap_x)
    y = sy + row * (card_h + gap_y)
    svg.append(f'<g class="line" style="animation-delay:{i*0.08:.2f}s">')
    svg.append(f'<rect class="card" x="{x}" y="{y}" width="{card_w}" height="{card_h}" rx="10"/>')
    svg.append(f'<text x="{x+18}" y="{y+30}" class="num">{value:,}</text>')
    svg.append(f'<text x="{x+18}" y="{y+53}" class="lab">{escape(label)}</text>')
    svg.append('</g>')

svg += [
    '<text x="32" y="414" class="sub">Java · Spring Boot · TypeScript · NestJS · PostgreSQL · Docker</text>',
    '</svg>'
]
(ROOT / "stats.svg").write_text("\n".join(svg), encoding="utf-8")
print("Wrote stats.svg")
