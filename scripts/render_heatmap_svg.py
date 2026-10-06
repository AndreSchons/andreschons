#!/usr/bin/env python3
import json
from datetime import date
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
data = json.loads((ROOT / "data" / "github.json").read_text(encoding="utf-8"))
weeks = data["contributions"]["contributionCalendar"]["weeks"][-53:]
total = data["contributions"]["contributionCalendar"]["totalContributions"]

W, H = 1000, 190
LEFT, TOP = 58, 46
CELL, GAP = 12, 4
STEP = CELL + GAP

colors = {
    "NONE": "#161b22",
    "FIRST_QUARTILE": "#0e4429",
    "SECOND_QUARTILE": "#006d32",
    "THIRD_QUARTILE": "#26a641",
    "FOURTH_QUARTILE": "#39d353",
}

def month_label(week):
    days = week["contributionDays"]
    if not days:
        return ""
    d = date.fromisoformat(days[0]["date"])
    return d.strftime("%b")

parts = [f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" role="img" aria-label="GitHub contribution calendar">\n<style>\n  .bg {{ fill:#0d1117; }}\n  .title {{ fill:#f0f6fc; font:600 16px ui-monospace,SFMono-Regular,Menlo,Consolas,monospace; }}\n  .muted {{ fill:#8b949e; font:12px ui-monospace,SFMono-Regular,Menlo,Consolas,monospace; }}\n  .cell {{ transform-box:fill-box; transform-origin:center; animation:pop .42s ease both; }}\n  @keyframes pop {{ from {{ opacity:0; transform:scale(.25); }} to {{ opacity:1; transform:scale(1); }} }}\n</style>\n<rect class="bg" width="100%" height="100%" rx="14"/>\n<text x="28" y="28" class="title">{total:,} contributions in the last year</text>\n''']

last_month = None
for x, week in enumerate(weeks):
    label = month_label(week)
    if label and label != last_month:
        parts.append(f'<text x="{LEFT + x*STEP}" y="43" class="muted">{escape(label)}</text>')
        last_month = label

for x, week in enumerate(weeks):
    for d in week["contributionDays"]:
        y = int(d["weekday"])
        level = d["contributionLevel"]
        count = d["contributionCount"]
        delay = (x + y) * 0.012
        parts.append(
            f'<rect class="cell" x="{LEFT + x*STEP}" y="{TOP + y*STEP}" '
            f'width="{CELL}" height="{CELL}" rx="2" fill="{colors.get(level, colors["NONE"])}" '
            f'style="animation-delay:{delay:.3f}s"><title>{count} contributions on {d["date"]}</title></rect>'
        )

for y, label in [(1,"Mon"),(3,"Wed"),(5,"Fri")]:
    parts.append(f'<text x="18" y="{TOP + y*STEP + 10}" class="muted">{label}</text>')

legend_x = 800
parts += [
    f'<text x="{legend_x}" y="171" class="muted">Less</text>',
    *[
        f'<rect x="{legend_x+34+i*17}" y="160" width="11" height="11" rx="2" fill="{c}"/>'
        for i,c in enumerate(colors.values())
    ],
    f'<text x="{legend_x+124}" y="171" class="muted">More</text>',
    '</svg>'
]
(ROOT / "contrib-heatmap.svg").write_text("\n".join(parts), encoding="utf-8")
print("Wrote contrib-heatmap.svg")
