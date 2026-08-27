"""
M7 synthetic thumbnail generator — Riverside Hardware & Supply.

Deterministic HTML/CSS -> PNG rendering (Playwright + headless Chromium),
not a generative image model. Each thumbnail is built to hit an exact,
known spec per content-items-plan.md — precise colors, precise text,
precise contrast — not an approximation from a prompt.

Canvas: 1280x720 (standard thumbnail aspect).
"""

import os
from playwright.sync_api import sync_playwright

OUT_DIR = "/tmp/m7-thumbnails"

TOOLBOX_SVG = """
<svg viewBox="0 0 200 140" xmlns="http://www.w3.org/2000/svg">
  <rect x="20" y="50" width="160" height="80" rx="8" fill="{box}" />
  <rect x="20" y="50" width="160" height="20" rx="8" fill="{lid}" />
  <path d="M 70 50 L 70 25 Q 70 15 80 15 L 120 15 Q 130 15 130 25 L 130 50"
        fill="none" stroke="{handle}" stroke-width="10" stroke-linecap="round" />
  <circle cx="55" cy="95" r="7" fill="{latch}" />
  <circle cx="145" cy="95" r="7" fill="{latch}" />
</svg>
"""

BASE_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{
    width: 1280px;
    height: 720px;
    font-family: 'Arial', 'Helvetica', sans-serif;
    position: relative;
    overflow: hidden;
    background: {bg_color};
  }}
  {extra_style}
  .accent-band {{
    position: absolute;
    top: 0; right: 0;
    width: 420px; height: 100%;
    background: {accent_color};
    clip-path: polygon(35% 0, 100% 0, 100% 100%, 0% 100%);
  }}
  .icon {{
    position: absolute;
    top: 60px; left: 60px;
    width: 130px; height: 91px;
  }}
  .brand {{
    position: absolute;
    bottom: 40px; left: 60px;
    font-size: 26px;
    font-weight: 700;
    letter-spacing: 0.04em;
    color: {brand_color};
  }}
  .title {{
    position: absolute;
    top: 220px; left: 60px;
    width: 760px;
    font-size: {title_size}px;
    font-weight: 800;
    line-height: 1.15;
    color: {title_color};
  }}
  .badge {{
    position: absolute;
    top: 50px; right: 50px;
    background: {badge_bg};
    color: {badge_color};
    font-size: 30px;
    font-weight: 800;
    padding: 14px 26px;
    border-radius: 6px;
    letter-spacing: 0.03em;
  }}
</style>
</head>
<body>
  <div class="accent-band"></div>
  {clutter}
  <div class="icon">{icon_svg}</div>
  <div class="title">{title}</div>
  <div class="brand">RIVERSIDE HARDWARE &amp; SUPPLY</div>
  {badge_html}
</body>
</html>
"""

def toolbox_icon(box, lid, handle, latch):
    return TOOLBOX_SVG.format(box=box, lid=lid, handle=handle, latch=latch)

def clutter_pattern(icon_color, tile_color, opacity=0.35):
    """Busy repeating-icon background used only for the legibility-flaw item."""
    tiles = ""
    for row in range(5):
        for col in range(7):
            x = col * 190 - 40
            y = row * 160 - 30
            tiles += (
                f'<g transform="translate({x},{y}) scale(0.55)" opacity="{opacity}">'
                + toolbox_icon(icon_color, tile_color, icon_color, tile_color)
                + "</g>"
            )
    return f'<svg style="position:absolute;top:0;left:0;width:1280px;height:720px;" ' \
           f'viewBox="0 0 1280 1280" xmlns="http://www.w3.org/2000/svg">{tiles}</svg>'

ITEMS = [
    dict(
        name="item1-paint-mixing-CLEAN",
        bg_color="#EFE4B0",
        accent_color="#FD5A1E",
        brand_color="#7a5a1e",
        title_color="#1a1208",
        title_size=48,
        icon_svg=toolbox_icon("#FD5A1E", "#c44415", "#7a5a1e", "#7a5a1e"),
        title="Mix Any Exterior Paint Color &mdash; In Store",
        clutter="",
        badge_html="",
        badge_bg="#FD5A1E",
        badge_color="#fffaf0",
        extra_style="",
    ),
    dict(
        name="item2-seasonal-checklist-CLEAN",
        bg_color="#FD5A1E",
        accent_color="#EFE4B0",
        brand_color="#3a2408",
        title_color="#fffaf0",
        title_size=48,
        icon_svg=toolbox_icon("#EFE4B0", "#cbb96a", "#3a2408", "#3a2408"),
        title="Seasonal Home Maintenance Checklist",
        clutter="",
        badge_html="",
        badge_bg="#EFE4B0",
        badge_color="#3a2408",
        extra_style="",
    ),
    dict(
        name="item3-tool-rental-FLAW-legibility",
        bg_color="#FD5A1E",
        accent_color="#FD5A1E",
        brand_color="#7a3010",
        # Text color deliberately very close to the background color/lightness --
        # near-unreadable on purpose, plus a cluttered tiled-icon background.
        title_color="#F2803D",
        title_size=48,
        icon_svg=toolbox_icon("#e05a2a", "#c44415", "#7a3010", "#7a3010"),
        title="Tool Rental 101: What We Offer",
        clutter=clutter_pattern("#e8703a", "#f28a4f", opacity=0.55),
        badge_html="",
        badge_bg="#FD5A1E",
        badge_color="#fffaf0",
        extra_style="",
    ),
    dict(
        name="item4-key-cutting-FLAW-brand",
        # Off-brand palette on purpose: blue/gray, nowhere near orange/cream.
        bg_color="#2A5C8A",
        accent_color="#7A7A7A",
        brand_color="#dfe6ec",
        title_color="#ffffff",
        title_size=48,
        icon_svg=toolbox_icon("#7A7A7A", "#5c5c5c", "#dfe6ec", "#dfe6ec"),
        title="Key Cutting While You Wait",
        clutter="",
        badge_html="",
        badge_bg="#7A7A7A",
        badge_color="#ffffff",
        extra_style="",
    ),
    dict(
        name="item5-propane-refill-FLAW-info-accuracy",
        bg_color="#EFE4B0",
        accent_color="#FD5A1E",
        brand_color="#7a5a1e",
        title_color="#1a1208",
        title_size=44,
        icon_svg=toolbox_icon("#FD5A1E", "#c44415", "#7a5a1e", "#7a5a1e"),
        title="Propane Tank Refill Safety Tips",
        clutter="",
        # Factually wrong claim relative to fact-sheet.md (Mon-Sat 8am-6pm, closed Sunday).
        badge_html='<div class="badge">OPEN 24/7</div>',
        badge_bg="#FD5A1E",
        badge_color="#fffaf0",
        extra_style="",
    ),
]

def build_html(item):
    return BASE_TEMPLATE.format(**item)

def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    html_paths = []
    for item in ITEMS:
        html_path = os.path.join(OUT_DIR, item["name"] + ".html")
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(build_html(item))
        html_paths.append((item["name"], html_path))

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1280, "height": 720})
        for name, html_path in html_paths:
            page.goto("file://" + html_path)
            png_path = os.path.join(OUT_DIR, name + ".png")
            page.screenshot(path=png_path)
            print(f"Rendered: {png_path}")
        browser.close()

if __name__ == "__main__":
    main()
