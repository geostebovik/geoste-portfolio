"""
M7 -- Azure AI Vision Read (OCR) smoke test.

WHY THIS FILE EXISTS -- it proves three things before any code is built on
top of them:

  1. Read is reachable on `aif-dev-wus-01`. That account is
     `kind=AIServices` (verified 2026-09-03), so Vision rides on the same
     endpoint and key as the chat deployments -- no new Azure resource.
  2. West US actually serves Image Analysis 4.0's `read` visual feature.
     Region support in Azure AI is PER-FEATURE, not per-service: 4.0 is in
     West US but 4.0's *captioning* feature is not. "The service is in my
     region" is a different claim from "the feature I need is in my region."
  3. What the response ACTUALLY looks like -- field names, geometry format,
     where confidence lives.

Point 3 is the real reason. The contrast check that follows consumes Read's
bounding polygons, and it should be written against an OBSERVED response,
not a described one. So this script prints the raw payload as well as a
structured view: if the structured view below is wrong about a field name,
the raw dump still shows the truth.

Reuses `m3_analyze.py`'s run_az-based credential fetch -- no cached secrets
in files, same as every other script here. Requires `az login` to already be
done in whatever shell runs this.

Written by Claude 2026-09-03 at Gerard's direction; not yet run at time of
writing.

Usage (from scripts/, venv active):
    python probe_read_ocr.py
    python probe_read_ocr.py item1-paint-mixing-CLEAN.png
"""

import json
import sys

from azure.ai.vision.imageanalysis.models import VisualFeatures

# The client lives in m7_legibility_check.py, not here. A probe script is a
# diagnostic; the production module should not depend on it. Dependency
# direction corrected 2026-09-03.
from m7_legibility_check import build_vision_client, FIXTURES_DIR

DEFAULT_FIXTURE = "item3-tool-rental-FLAW-legibility.png"


def main():
    fixture_name = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_FIXTURE
    image_path = FIXTURES_DIR / fixture_name

    if not image_path.exists():
        raise SystemExit(f"Fixture not found: {image_path}")

    print(f"Image:  {image_path.name}")
    print(f"Path:   {image_path}\n")

    client = build_vision_client()
    result = client.analyze(
        image_data=image_path.read_bytes(),
        visual_features=[VisualFeatures.READ],
    )

    # ---- structured view (best-effort; the raw dump below is authoritative)
    print("=" * 70)
    print("STRUCTURED VIEW")
    print("=" * 70)
    meta = getattr(result, "metadata", None)
    if meta is not None:
        print(f"image size: {meta.width} x {meta.height} px\n")

    if result.read is None:
        print("result.read is None -- Read returned nothing at all for this image.")
    else:
        for b_i, block in enumerate(result.read.blocks):
            print(f"block {b_i}: {len(block.lines)} line(s)")
            for l_i, line in enumerate(block.lines):
                poly = ", ".join(f"({p.x},{p.y})" for p in line.bounding_polygon)
                print(f"  line {l_i}: {line.text!r}")
                print(f"    polygon: {poly}")
                for word in line.words:
                    print(f"    word {word.text!r:<28} confidence={word.confidence:.4f}")
            print()

    # ---- raw payload. This is the part to trust.
    print("=" * 70)
    print("RAW RESPONSE (authoritative -- compare against the view above)")
    print("=" * 70)
    try:
        print(json.dumps(result.as_dict(), indent=2))
    except AttributeError:
        # Older/newer SDK shapes may not expose as_dict(); fall back to repr.
        print(repr(result))


if __name__ == "__main__":
    main()
