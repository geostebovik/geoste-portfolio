"""
M7 -- diagnostic thumbnail generator, NOT part of the official fixture set.

Builds three controlled variants of item3-tool-rental-FLAW-legibility.png,
each changing exactly one thing from item3's actual baseline (bg_color=
"#FD5A1E", title_color="#F2803D", clutter_pattern(...) at opacity=0.55) to
isolate whether the CV-audit's text_legible miss (confirmed stable, 5/5,
via tester2.py, Aug 31) is caused by contrast, clutter, or both together.

Deliberately separate from build.py's official ITEMS / content-items-plan.md
answer key -- these are throwaway diagnostic images, never meant to become
graded fixtures. Renders to its own /tmp output dir (same pattern as
build.py's OUT_DIR), reuses build.py's shared HTML template and helper
functions rather than duplicating them.

Variant A -- clutter kept, contrast fixed (title_color swapped to
  "#fffaf0", the same cream item2 already passes with, on this same
  orange background). If this passes, clutter alone isn't the problem.
Variant B -- contrast kept exactly as item3, clutter removed entirely.
  If this still misses, the model doesn't need visual clutter to miss
  this level of contrast -- a bigger finding than item3 alone suggested.
Variant C -- contrast pushed to the extreme (title_color set identical
  to bg_color -- zero contrast, true invisibility), clutter removed.
  Decided with Gerard (Aug 31): push as close as possible and see what
  comes back, then evaluate -- not picking a "reasonable" middle value
  in advance.

Variant D -- added after A/B/C all came back text_legible=True at 5/5,
  including C's genuinely zero-contrast, nothing-there-to-read control.
  Different question from A/B/C: not "where's the contrast threshold,"
  but "can this check ever return false at all." Uses the proven-legible
  color combo (cream title on the orange bg, no clutter -- same pairing
  diag-a already passed with) so color and clutter are ruled out as
  factors, and shrinks title_size from 48 down to 3 -- unmistakably too
  small to read at normal viewing size, a completely different failure
  mode than color contrast. Deliberately not "remove the title text
  entirely": RIVERSIDE HARDWARE & SUPPLY still renders at the bottom in
  every variant, so a title-less image would still contain genuinely
  legible text and text_legible=true would be the correct answer, not
  evidence of anything -- this needed to keep text-shaped content
  present while making it unmistakably unreadable through an unrelated
  mechanism (size, not color).
"""

import tempfile
from pathlib import Path

from playwright.sync_api import sync_playwright

from build import toolbox_icon, clutter_pattern, build_html

# tempfile.gettempdir() instead of a hardcoded "/tmp" -- resolves to the
# right OS temp dir wherever this actually runs (Cloud Shell vs. Windows
# PowerShell), unlike build.py's own hardcoded OUT_DIR, which only "works"
# because it's always been run from a Unix-like shell so far.
OUT_DIR = Path(tempfile.gettempdir()) / "m7-legibility-diagnostics"

_BASELINE = dict(
    accent_color="#FD5A1E",
    brand_color="#7a3010",
    title_size=48,
    icon_svg=toolbox_icon("#e05a2a", "#c44415", "#7a3010", "#7a3010"),
    title="Tool Rental 101: What We Offer",
    badge_html="",
    badge_bg="#FD5A1E",
    badge_color="#fffaf0",
    extra_style="",
)

DIAGNOSTIC_ITEMS = [
    dict(
        _BASELINE,
        name="diag-a-clutter-normal-contrast",
        bg_color="#FD5A1E",
        title_color="#fffaf0",  # proven-readable cream -- item2 already passes with this
        clutter=clutter_pattern("#e8703a", "#f28a4f", opacity=0.55),  # item3's clutter, unchanged
    ),
    dict(
        _BASELINE,
        name="diag-b-lowcontrast-noclutter",
        bg_color="#FD5A1E",
        title_color="#F2803D",  # item3's exact low-contrast color, unchanged
        clutter="",
    ),
    dict(
        _BASELINE,
        name="diag-c-extreme-lowcontrast-noclutter",
        bg_color="#FD5A1E",
        title_color="#FD5A1E",  # identical to bg -- zero contrast, true invisibility
        clutter="",
    ),
    dict(
        _BASELINE,
        name="diag-d-tiny-font-proven-contrast",
        bg_color="#FD5A1E",
        title_color="#fffaf0",  # proven-legible cream -- diag-a already passed with this
        clutter="",
        title_size=3,  # unmistakably unreadable at this size, nothing to do with color
    ),
]


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    html_paths = []
    for item in DIAGNOSTIC_ITEMS:
        html_path = OUT_DIR / (item["name"] + ".html")
        html_path.write_text(build_html(item), encoding="utf-8")
        html_paths.append((item["name"], html_path))

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1280, "height": 720})
        for name, html_path in html_paths:
            page.goto(html_path.as_uri())  # correct cross-platform file:// URL
            png_path = OUT_DIR / (name + ".png")
            page.screenshot(path=str(png_path))
            print(f"Rendered: {png_path}")
        browser.close()


if __name__ == "__main__":
    main()
