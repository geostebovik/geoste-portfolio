"""
M7 -- deterministic text-legibility check (replaces the model-judged one).

WHY THIS EXISTS. Four controlled probe runs (Sep 2-3) established that a
vision model cannot reliably judge whether text is hard for a HUMAN to read:
it decodes pixel values and has no notion that recovery was effortful. The
same fixture returned 0/7, 6/7, 5/7 and 3/7 across runs. See
content-items-plan.md item 3 for the full finding.

The fix is architectural, not a better prompt: move the JUDGMENT out of the
model and leave the PERCEPTION in it.
  - Azure AI Vision Read (OCR) locates text  -> it is good at this
  - This module measures contrast and rules  -> arithmetic, same answer every run

Read is only the LOCATOR. It is not the judge, and it must not be: on the
Sep 3 smoke test Read recovered item3's headline at 1.19:1 contrast, which
is exactly the low-contrast recovery that makes models unreliable here.

Written by Claude 2026-09-03 at Gerard's direction.

Usage (from scripts/, venv active):
    python m7_legibility_check.py --selftest    # pure math, NO Azure calls
    python m7_legibility_check.py              # measures all 5 fixtures via Read
    python m7_legibility_check.py item3-tool-rental-FLAW-legibility.png
"""

import os
import sys
from pathlib import Path

import numpy as np
from dotenv import load_dotenv
from azure.core.credentials import AzureKeyCredential
from azure.ai.vision.imageanalysis import ImageAnalysisClient
from azure.ai.vision.imageanalysis.models import VisualFeatures

from m3_analyze import get_endpoint, get_subscription_key  # reuse, don't rewrite

# NOTE: Pillow is imported lazily inside measure_contrast(), not here. The
# --selftest path exercises only the WCAG arithmetic and must run with numpy
# alone -- a module-level `from PIL import Image` made the zero-cost check
# depend on an image library it never uses (caught 2026-09-03).

FIXTURES_DIR = (Path(__file__).parent / ".." / "iip-docs" / "m7-riverside-hardware").resolve()

# WCAG 2.x minimum contrast for LARGE text (>=24px, or >=18.66px bold).
# Every text element in these fixtures is large text: titles are 44-48px at
# weight 800, the business name is 26px at weight 700. Normal text would be
# 4.5:1. Named here because it is a policy choice, not a fact -- change it in
# one place and the whole check moves with it.
LARGE_TEXT_THRESHOLD = 3.0

# When separating text pixels from background pixels, use the 10th/90th
# percentile of each class rather than its mean. Antialiased glyph edges are
# blends of the two colors; including them in a mean pulls the two measured
# colors toward each other and UNDERSTATES contrast. Verified 2026-09-03
# against build.py's declared colors on item3: class-mean gave 2.629:1 where
# the true value is 2.949:1 (off by 0.32); p10/p90 gave 2.967:1 (off by 0.02).
EDGE_PERCENTILE = 10


# --------------------------------------------------------------------------
# WCAG relative luminance and contrast. Pure arithmetic -- no Azure, no image.
# --------------------------------------------------------------------------

def _linearize(channel_0_255):
    """Undo sRGB gamma encoding. Stored RGB values are perceptual, not physical."""
    c = np.asarray(channel_0_255, dtype=float) / 255.0
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def relative_luminance(rgb):
    """WCAG relative luminance, 0.0 (black) to 1.0 (white).

    Green is weighted ~10x blue because the retina is built that way.
    Accepts a single (r,g,b) or an (N,3) array.
    """
    lin = _linearize(np.asarray(rgb, dtype=float))
    r, g, b = lin[..., 0], lin[..., 1], lin[..., 2]
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast_ratio(rgb_a, rgb_b):
    """WCAG contrast ratio, 1.0 (identical) to 21.0 (black on white).

    The 0.05 terms model ambient light reflecting off a real screen, which
    never emits true black in a lit room. They also stop division by zero.
    """
    la, lb = float(relative_luminance(rgb_a)), float(relative_luminance(rgb_b))
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


# --------------------------------------------------------------------------
# Pixel measurement
# --------------------------------------------------------------------------

def _otsu_threshold(luminances):
    """Split luminances into two classes by maximizing between-class variance.

    Deterministic and dependency-light -- no k-means, no random seeding.
    """
    hist, edges = np.histogram(luminances, bins=64, range=(0.0, 1.0))
    centers = (edges[:-1] + edges[1:]) / 2
    total = hist.sum()
    if total == 0:
        return None
    w0 = np.cumsum(hist)
    w1 = total - w0
    m0 = np.cumsum(hist * centers)
    m_total = m0[-1]
    with np.errstate(invalid="ignore", divide="ignore"):
        between = (m_total * w0 / total - m0) ** 2 / (w0 * w1 / total ** 2 + 1e-12) / total ** 2
    between = np.nan_to_num(between)
    return float(centers[int(np.argmax(between[:-1]))])


def measure_contrast(image_array, polygons):
    """Contrast between the two dominant color populations inside `polygons`.

    `polygons` is a list of 4-point bounding polygons as Read returns them:
    [{"x": int, "y": int}, ...] in top-left, top-right, bottom-right,
    bottom-left order. Read's polygons are near-axis-aligned but not exactly
    (y varies 1-3px across a line), so each is reduced to its bounding box.

    IMPORTANT: pass WORD polygons, not the LINE polygon. On item3 the line box
    spans x=56..873 while the words only occupy x=60..777 -- the line box
    carries ~96px of empty background that dilutes the measurement.
    """
    patches = []
    h, w = image_array.shape[:2]
    for poly in polygons:
        xs = [p["x"] for p in poly]
        ys = [p["y"] for p in poly]
        x0, x1 = max(0, min(xs)), min(w, max(xs))
        y0, y1 = max(0, min(ys)), min(h, max(ys))
        if x1 > x0 and y1 > y0:
            patches.append(image_array[y0:y1, x0:x1].reshape(-1, 3))
    if not patches:
        return None

    pixels = np.concatenate(patches)
    lums = relative_luminance(pixels)
    threshold = _otsu_threshold(lums)
    if threshold is None:
        return None

    dark, light = pixels[lums <= threshold], pixels[lums > threshold]
    if len(dark) == 0 or len(light) == 0:
        # One population only: nothing distinguishable from its background.
        return {"contrast": 1.0, "dark": None, "light": None, "pixels": len(pixels)}

    dark_l, light_l = relative_luminance(dark), relative_luminance(light)
    core_dark = dark[dark_l <= np.percentile(dark_l, EDGE_PERCENTILE)].mean(axis=0)
    core_light = light[light_l >= np.percentile(light_l, 100 - EDGE_PERCENTILE)].mean(axis=0)

    to_hex = lambda c: "#%02x%02x%02x" % tuple(int(round(v)) for v in c)
    return {
        "contrast": contrast_ratio(core_dark, core_light),
        "dark": to_hex(core_dark),
        "light": to_hex(core_light),
        "pixels": len(pixels),
    }


# --------------------------------------------------------------------------
# The check
# --------------------------------------------------------------------------

def check_text_legibility(image_path, read_result):
    """Return (text_legible: bool, notes: str) for one thumbnail.

    `read_result` is the object from ImageAnalysisClient.analyze(...).read --
    passed in rather than fetched here so this function stays testable without
    an Azure call, and so a caller auditing several images reuses one client.

    A thumbnail is legible when EVERY text line Read found meets
    LARGE_TEXT_THRESHOLD. One legible element does not cover for another --
    that rule survives from the model-judged version, where it was the fix for
    the original existential-vs-universal quantifier bug.
    """
    from PIL import Image  # lazy -- see note at the imports

    image_array = np.array(Image.open(image_path).convert("RGB"))

    if read_result is None or not read_result.blocks:
        return False, "No text elements detected in the image at all."

    measured, failures = [], []
    for block in read_result.blocks:
        for line in block.lines:
            polys = [[{"x": p.x, "y": p.y} for p in word.bounding_polygon] for word in line.words]
            result = measure_contrast(image_array, polys)
            if result is None:
                continue
            ratio = result["contrast"]
            confidences = [w.confidence for w in line.words]
            measured.append((line.text, ratio, min(confidences) if confidences else None))
            if ratio < LARGE_TEXT_THRESHOLD:
                failures.append((line.text, ratio))

    if not measured:
        return False, "Text was detected but no element could be measured."

    detail = "; ".join(
        f"{text!r} {ratio:.2f}:1" + (f" (min OCR confidence {conf:.2f})" if conf is not None else "")
        for text, ratio, conf in measured
    )
    if failures:
        worst = min(failures, key=lambda f: f[1])
        return False, (
            f"Below the {LARGE_TEXT_THRESHOLD}:1 WCAG large-text minimum: "
            f"{len(failures)} of {len(measured)} element(s). "
            f"Worst: {worst[0]!r} at {worst[1]:.2f}:1. Measured: {detail}"
        )
    return True, f"All {len(measured)} text element(s) meet {LARGE_TEXT_THRESHOLD}:1. Measured: {detail}"


# --------------------------------------------------------------------------

def build_vision_client() -> ImageAnalysisClient:
    """Build an Image Analysis client against the shared AIServices account.

    `aif-dev-wus-01` is kind=AIServices, so Vision rides the same endpoint and
    key as the chat deployments -- no second Azure resource. Deliberately NOT
    m7_cv_audit_tool.py's client: that one is AzureOpenAI on a bumped
    api_version for structured outputs. Same account, different data plane,
    different SDK.

    load_dotenv() is called here rather than at module level so importing this
    module has no side effects -- matching every other script in this folder.
    """
    load_dotenv()
    account, resource_group = os.environ["AIF_ACCOUNT"], os.environ["AIF_RESOURCE_GROUP"]
    endpoint = get_endpoint(account, resource_group)
    key = get_subscription_key(account, resource_group)
    return ImageAnalysisClient(endpoint=endpoint, credential=AzureKeyCredential(key))


def audit_legibility(image_path, client: ImageAnalysisClient = None):
    """Locate text with Read, then measure contrast. Returns (bool, notes).

    This is the entry point m7_cv_audit_tool.py calls -- it hides Vision
    entirely from the audit tool, which only needs a verdict and a reason.

    Pass `client` to reuse one across several images; omit it and one is built
    per call. Building it costs two `az` invocations, which is the same
    per-call cost build_audit_client() already pays, so the default matches
    existing behaviour rather than quietly changing it.
    """
    client = client or build_vision_client()
    image_path = Path(image_path)
    result = client.analyze(
        image_data=image_path.read_bytes(),
        visual_features=[VisualFeatures.READ],
    )
    return check_text_legibility(image_path, result.read)


def _selftest():
    """Verify the math against build.py's declared colors. No Azure, no image."""
    hexr = lambda s: tuple(int(s.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4))
    cases = [
        ("item3 title  #F2803D on #FD5A1E", "#F2803D", "#FD5A1E", 1.191),
        ("item3 brand  #7a3010 on #FD5A1E", "#7a3010", "#FD5A1E", 2.949),
        ("item1 title  #1a1208 on #EFE4B0", "#1a1208", "#EFE4B0", 14.458),
        ("item2 title  #fffaf0 on #FD5A1E", "#fffaf0", "#FD5A1E", 3.032),
        ("white on black (max possible)   ", "#ffffff", "#000000", 21.000),
    ]
    print(f"{'case':<36}{'computed':>10}{'expected':>10}   ok?")
    ok = True
    for label, fg, bg, expected in cases:
        got = contrast_ratio(hexr(fg), hexr(bg))
        passed = abs(got - expected) < 0.01
        ok &= passed
        print(f"{label:<36}{got:>9.3f}:1{expected:>9.3f}:1   {'yes' if passed else 'NO'}")
    print("\nselftest:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main():
    if "--selftest" in sys.argv:
        raise SystemExit(_selftest())

    names = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not names:
        names = sorted(p.name for p in FIXTURES_DIR.glob("item*.png"))

    client = build_vision_client()
    print(f"Threshold: {LARGE_TEXT_THRESHOLD}:1 (WCAG large text)\n")
    for name in names:
        path = FIXTURES_DIR / name
        result = client.analyze(image_data=path.read_bytes(), visual_features=[VisualFeatures.READ])
        legible, notes = check_text_legibility(path, result.read)
        print(f"{name}\n  text_legible = {legible}\n  {notes}\n")


if __name__ == "__main__":
    main()
