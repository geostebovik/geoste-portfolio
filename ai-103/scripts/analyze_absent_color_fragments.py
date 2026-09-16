"""
Count an absent colour in EACH labelled fragment of the audit notes, not just
[observed]. Offline: reads a results file, makes no Azure call.

WHY (added 2026-09-16, Claude wrote it). probe_fixture_stability.py's
ABSENT_COLOR_CHECKS only searches the [observed] fragment. The [content]
fragment -- the brand verdict's own explanation, and the channel the Sep 11
defect was first found in ("orange/cream palette" on 15 runs of 15) -- was not
counted by anything. On Run 2 (0dffc01, the shipped audit wording with no
docstring) [observed] names "cream" 0/45 and [content] names it 40/45.

TWO COUNTS, AND ONLY THE FIRST IS THE MEASURE:

1. SUBSTRING, per fragment. Same test ABSENT_COLOR_CHECKS uses, so it compares
   with every earlier figure. It is a regression detector, not a quality
   measure (m7-orientation.md Backlog): it scores a bare brand-guide
   recitation the same as a wrong description of the image.

2. IMAGE-ATTRIBUTION, [content] only, secondary and for information. A
   [content] sentence counts as attributing the colour TO THE IMAGE when a
   colour noun (tones, accents, highlights, hues, shades, tints, colours)
   follows the colour's token within three words, without crossing
   punctuation:
       "dominated by orange and cream/peach tones"        -> image
       "orange with cream-like light orange/peach accents" -> image
       "orange/cream-family hues"                          -> image
       "consistent with the orange/cream family"           -> palette only
       "Brand colors are within the orange/cream family"   -> palette only
   The rule was written on Sep 16 AFTER reading Run 2's sentences, so Run 2's
   split is calibration, not a blind result. It is fixed as of this commit
   and applies unchanged to any later run. Every matched sentence is printed
   so a person can audit the call.

Usage:
    python analyze_absent_color_fragments.py results/<file>_fixture_stability.json [...] [--sentences]
One file prints its [content] sentences; several print counts only unless
--sentences is given.
"""

import json
import re
import sys
from pathlib import Path

# Same pairs as probe_fixture_stability.ABSENT_COLOR_CHECKS. Copied, not
# imported. That module has had a __main__ guard since 2026-09-16, but it
# imports the audit tool (pydantic, openai, dotenv), and this script is meant
# to run offline on any Python with nothing installed. The dependency runs the
# other way: the probe imports fragment() from here.
ABSENT_COLOR_CHECKS = {
    "item3-tool-rental-FLAW-legibility.png": "cream",
}

FRAGMENTS = ("legibility", "observed", "content")
COLOUR_NOUNS = r"(?:tones?|accents?|highlights?|hues?|shades?|tints?|colou?rs?)"


def fragment(notes: str, tag: str) -> str:
    """Every line of `notes` that belongs to the [tag] fragment, joined.

    A fragment can run past one line (the model sometimes writes a second
    paragraph), so a line with no label belongs to the last label seen.
    """
    current, out = None, []
    for line in notes.splitlines():
        m = re.match(r"^\[(\w+)\]", line)
        if m:
            current = m.group(1)
        if current == tag:
            out.append(line)
    return "\n".join(out)


def sentences_naming(text: str, colour: str) -> list[str]:
    parts = re.split(r"(?<=[.;])\s+|\n", text)
    return [p.strip() for p in parts if colour in p.lower()]


def attributes_to_image(sentence: str, colour: str) -> bool:
    pattern = (rf"{colour}[\w/-]*"          # the token: cream, cream-like, peach/cream-family
               rf"(?:[ \t]+[\w/-]+){{0,3}}?"  # up to three more words, no punctuation
               rf"[ \t]+{COLOUR_NOUNS}\b")
    return re.search(pattern, sentence, re.IGNORECASE) is not None


def analyze(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    fixtures = data.get("fixtures", data)
    run = data.get("run", {})
    report = {"file": path.name, "git_head": run.get("git_head", "")[:7],
              "git_dirty": run.get("git_dirty"), "checks": {}}
    for fixture, colour in ABSENT_COLOR_CHECKS.items():
        runs = fixtures.get(fixture, [])
        counts = {tag: 0 for tag in FRAGMENTS}
        image_runs, palette_only_runs, lines = 0, 0, []
        for r in runs:
            notes = r.get("notes", "")
            for tag in FRAGMENTS:
                if colour in fragment(notes, tag).lower():
                    counts[tag] += 1
            hits = sentences_naming(fragment(notes, "content"), colour)
            if hits:
                is_image = any(attributes_to_image(s, colour) for s in hits)
                image_runs += is_image
                palette_only_runs += not is_image
                for s in hits:
                    tag = "IMAGE  " if attributes_to_image(s, colour) else "PALETTE"
                    lines.append(f"  run {r.get('run')}: {tag} {s[:200]}")
        report["checks"][fixture] = {
            "colour": colour, "runs": len(runs),
            "substring_by_fragment": counts,
            "content_image_attribution_runs": image_runs,
            "content_palette_only_runs": palette_only_runs,
            "content_sentences": lines,
        }
    return report


def main() -> None:
    files = [a for a in sys.argv[1:] if not a.startswith("--")]
    show_sentences = "--sentences" in sys.argv[1:] or len(files) == 1
    if not files:
        sys.exit(__doc__)
    for arg in files:
        rep = analyze(Path(arg))
        print(f"\n{rep['file']}  head {rep['git_head']}  dirty={rep['git_dirty']}")
        for fixture, c in rep["checks"].items():
            n = c["runs"]
            f = c["substring_by_fragment"]
            print(f"  {fixture}: '{c['colour']}' by fragment (substring), of {n} runs: "
                  + ", ".join(f"[{k}] {v}/{n}" for k, v in f.items()))
            print(f"  [content] image-attribution {c['content_image_attribution_runs']}/{n}, "
                  f"palette-only {c['content_palette_only_runs']}/{n}  (secondary, rule fixed Sep 16)")
            if show_sentences:
                print("\n".join(c["content_sentences"]))


if __name__ == "__main__":
    main()
