"""
M7 -- legibility root-cause, next step: (1) print the FULL audit result
(notes included, not just text_legible) for diag-c and diag-d, to see
what the model actually claims to observe when it calls genuinely
invisible or unmistakably-tiny text "legible"; (2) re-run both with
"detail": "high" explicitly set on the image content, to test whether
Azure OpenAI's default image-processing detail level is throwing away
fine-grained detail (small text, subtle contrast) before the model ever
evaluates it.

Motivating pattern (Aug 31): text_legible has never once returned false
across item3 + diag-a/b/c/d -- 20 runs total, every one individually
stable at 5/5. Meanwhile brand_consistent correctly caught item4's
off-brand blue/gray palette, and info_accuracy correctly caught item5's
"OPEN 24/7" claim -- both large, coarse, whole-image-scale signals. That
split (coarse: reliable, fine detail: never, not even at zero contrast
or 3px text) is the signature you'd expect if the image is being
processed at reduced resolution before the model evaluates it, not a
gradual contrast-sensitivity gap.

Deliberately bypasses audit_thumbnail() rather than editing it -- this
is still root-causing, not the fix. Reuses build_audit_client() and
build_audit_messages() from m7_cv_audit_tool.py unchanged, then patches
"detail" onto the returned messages' image_url dict afterward, so the
real system/user prompt text is never duplicated here. If "detail":
"high" turns out to matter, that change belongs in
build_audit_messages() itself, deliberately, not left living only here.

RUNS is small (2) on purpose -- this is still exploratory. If either
condition shows something other than a flat true, bump RUNS up and
rerun for the same 5-run/80%-agreement confirmation used everywhere
else before trusting it.
"""

import json
import os
import tempfile
from pathlib import Path

from m7_cv_audit_tool import build_audit_client, build_audit_messages, ThumbnailAudit
from m7_vision_test import encode_image

DIAG_DIR = Path(tempfile.gettempdir()) / "m7-legibility-diagnostics"

TARGETS = [
    "diag-c-extreme-lowcontrast-noclutter",
    "diag-d-tiny-font-proven-contrast",
]

RUNS = 2


def run_audit(image_path, detail=None):
    client = build_audit_client()
    image_b64 = encode_image(Path(image_path))
    messages = build_audit_messages(image_b64)

    if detail:
        messages[1]["content"][1]["image_url"]["detail"] = detail

    model = os.environ["CHAT_DEPLOYMENT_GPT_5_4_MINI"]
    response = client.beta.chat.completions.parse(
        model=model,
        messages=messages,
        response_format=ThumbnailAudit,
    )
    result: ThumbnailAudit = response.choices[0].message.parsed
    return json.loads(result.model_dump_json())


for name in TARGETS:
    image_path = DIAG_DIR / f"{name}.png"

    for detail_label, detail_value in [("default detail", None), ("detail=high", "high")]:
        print(f"=== {name} ({detail_label}) ===")
        for i in range(RUNS):
            actual = run_audit(image_path, detail=detail_value)
            print(f"  Run {i + 1}: text_legible={actual['text_legible']}")
            print(f"    notes: {actual['notes']}")
        print()
