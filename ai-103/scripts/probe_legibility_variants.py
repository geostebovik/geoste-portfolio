"""
M7 -- legibility root-cause: 5 runs each against the three
build_legibility_diagnostics.py variants (diag-a/b/c), same reliability
discipline as tester2.py's item3 check (Aug 31, 5/5 stable, not noise).

Requires build_legibility_diagnostics.py to have been run first -- reads
its rendered PNGs from /tmp/m7-legibility-diagnostics/, doesn't render
anything itself.

Isolates what's actually driving the item3 miss:
  diag-a: item3's clutter kept, contrast fixed      -> tests clutter alone
  diag-b: item3's exact low contrast, no clutter     -> tests contrast alone
  diag-c: contrast pushed to zero, no clutter        -> tests any-contrast
                                                         sensitivity at all

Gerard's call (Aug 31): all three get the full 5-run / 80%-agreement
treatment up front, not a cheap single-run screen first -- Cost
Management showed budget isn't a real constraint this billing cycle.
"""

import json
import tempfile
from pathlib import Path

from m7_cv_audit_tool import audit_thumbnail

# Must match build_legibility_diagnostics.py's OUT_DIR exactly.
DIAG_DIR = Path(tempfile.gettempdir()) / "m7-legibility-diagnostics"

VARIANTS = {
    "diag-a-clutter-normal-contrast":
        "clutter kept, contrast fixed -- tests clutter alone",
    "diag-b-lowcontrast-noclutter":
        "item3's exact contrast, clutter removed -- tests contrast alone",
    "diag-c-extreme-lowcontrast-noclutter":
        "contrast pushed to zero, clutter removed -- tests any-contrast sensitivity",
    "diag-d-tiny-font-proven-contrast":
        "proven-legible color, no clutter, title_size=3 -- tests whether "
        "text_legible can ever return false at all, via a non-color failure mode",
}

RUNS = 5
STABLE_THRESHOLD = 0.8

for name, purpose in VARIANTS.items():
    image_path = DIAG_DIR / f"{name}.png"
    print(f"=== {name} ===\n    {purpose}")

    results = []
    for i in range(RUNS):
        actual = json.loads(audit_thumbnail(str(image_path)))
        print(f"  Run {i + 1}: text_legible={actual['text_legible']}")
        results.append(actual["text_legible"])

    true_count = sum(results)
    agreement = true_count / RUNS

    print(f"  {true_count}/{RUNS} runs returned text_legible=True "
          f"({agreement:.0%} agreement)")

    if agreement >= STABLE_THRESHOLD or (1 - agreement) >= STABLE_THRESHOLD:
        majority_verdict = true_count >= RUNS / 2
        print(f"  STABLE -- text_legible={majority_verdict}\n")
    else:
        print(f"  NOT STABLE (< {STABLE_THRESHOLD:.0%} agreement either way) "
              f"-- noisy result, don't trust either verdict yet\n")
