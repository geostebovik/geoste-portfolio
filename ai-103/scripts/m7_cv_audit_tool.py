"""
M7 -- IIP: CV-audit tool wrapper for the orchestrator agent.

FRAMEWORK ONLY, written 2026-08-28 -- the prompt text and a couple of real
judgment calls are left as TODOs below. Fill those in, then this becomes
the second tool the orchestrator agent gets handed alongside evaluate_draft().

Wraps m7_vision_test.py's proven vision-call plumbing (build_client(),
encode_image()) but does NOT reuse build_client() unchanged -- see the
api_version note below. Checks a thumbnail image against fact-sheet.md's
brand/hours ground truth and returns a JSON string with the 3-field
rubric + notes, same dict-shaped family as m7_evaluator_tool.py's
evaluate_draft(), serialized per the FunctionTool return convention
documented in agent-service-primer.md ("How FunctionTool actually reads
your function", added 2026-08-28).

Real version note, checked against .env directly (2026-08-28): the shared
CHAT_API_VERSION env var is pinned at "2024-06-01". Azure OpenAI's
structured-outputs feature (response_format=<pydantic model>) requires
"2024-08-01-preview" or later. Bumping CHAT_API_VERSION itself would touch
every other M5/M6/M7 script that reads it -- not worth the blast radius for
one new tool. This file builds its own client with its own bumped version
instead, rather than reusing m7_vision_test.py's build_client() as-is.
"""

import json
import os
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel
from openai import AzureOpenAI

from m3_analyze import get_endpoint, get_subscription_key  # reuse, don't rewrite
from m7_vision_test import encode_image  # reuse, don't rewrite -- no api_version dependency

# Answer key for the fixtures in iip-docs/m7-riverside-hardware/ -- mirrors
# content-items-plan.md's expected-results table. A PNG in that folder only
# gets audited if it's a key here; anything else is skipped and reported,
# not silently processed. Add new fixtures here, not by relying on a
# filename pattern.
EXPECTED_RESULTS = {
    "item1-paint-mixing-CLEAN.png": {
        "text_legible": True, "brand_consistent": True, "info_accurate": True,
    },
    "item2-seasonal-checklist-CLEAN.png": {
        "text_legible": True, "brand_consistent": True, "info_accurate": True,
    },
    "item3-tool-rental-FLAW-legibility.png": {
        "text_legible": False, "brand_consistent": True, "info_accurate": True,
    },
    "item4-key-cutting-FLAW-brand.png": {
        "text_legible": True, "brand_consistent": False, "info_accurate": True,
    },
    "item5-propane-refill-FLAW-info-accuracy.png": {
        "text_legible": True, "brand_consistent": True, "info_accurate": False,
    },
}

# Bumped independently of the shared CHAT_API_VERSION -- see module docstring.
# TODO: confirm this is still the right version once you've read the current
# structured-outputs doc yourself; verify by running this file, not by
# trusting this comment.
STRUCTURED_OUTPUT_API_VERSION = "2024-08-01-preview"

FACT_SHEET_PATH = (
    Path(__file__).parent
    / ".."
    / "iip-docs"
    / "m7-riverside-hardware"
    / "fact-sheet.md"
).resolve()

with open(FACT_SHEET_PATH, "r", encoding="utf-8") as f:
    fact_sheet = f.read()


class ThumbnailAudit(BaseModel):
    """Structured-output schema for the CV audit. Passed as response_format
    so the model's reply is GUARANTEED to match this shape -- not just
    asked for nicely in the prompt text.
    """
    text_legible: bool
    brand_consistent: bool
    info_accurate: bool
    notes: str


class LegibilityAudit(BaseModel):
    """Structured-output schema for call 1 of the split audit (legibility
    only). Added 2026-09-02 -- see build_legibility_messages() for why the
    audit is two calls now.
    """
    text_legible: bool
    notes: str


class ContentAudit(BaseModel):
    """Structured-output schema for call 2 of the split audit (brand +
    info accuracy). These two stay together deliberately: neither was ever
    implicated in the cross-check contamination that forced the split, and
    both need the fact sheet in context.
    """
    brand_consistent: bool
    info_accurate: bool
    notes: str


def build_audit_client() -> AzureOpenAI:
    """Build the AzureOpenAI client for the audit call, using the bumped
    STRUCTURED_OUTPUT_API_VERSION rather than the shared CHAT_API_VERSION.
    Mirrors m7_vision_test.py's build_client() shape otherwise.
    """
    load_dotenv()

    account, rg = os.environ["AIF_ACCOUNT"], os.environ["AIF_RESOURCE_GROUP"]
    endpoint = get_endpoint(account, rg)
    key = get_subscription_key(account, rg)

    return AzureOpenAI(
        azure_endpoint=endpoint,
        api_key=key,
        api_version=STRUCTURED_OUTPUT_API_VERSION,
    )


def _build_messages(system_prompt: str, user_prompt: str, image_b64: str,
                    mime_type: str) -> list[dict]:
    """Assemble the system + user message envelope shared by both audit
    calls. Structure mirrors m7_vision_test.py's build_vision_messages():
    a text part plus an image part inside the user message's content list.
    Factored out 2026-09-02 when the audit became two calls -- the envelope
    is identical for both, only the prompts differ.
    """
    return [
        {"role": "system", "content": system_prompt},
        {
            "role": "user",
            "content": [
                {"type": "text", "text": user_prompt},
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:{mime_type};base64,{image_b64}"},
                },
            ],
        },
    ]


def build_legibility_messages(image_b64: str, mime_type: str = "image/png") -> list[dict]:
    """Build the messages for call 1 of the split audit: legibility only.

    WHY THIS IS A SEPARATE CALL (decided 2026-09-02, full reasoning in
    STATUS.md's Sep 2 entries): two consecutive wording edits each fixed
    their target check and broke a different one. Tightening text_legible
    broke info_accurate on items 2 and 3; fixing info_accurate broke
    text_legible on item3 while text_legible's clause sat byte-for-byte
    unchanged on disk, with the original bug's reasoning returning verbatim.
    That is cross-check contamination in a shared system prompt,
    demonstrated in both directions under pinned temperature/seed --
    salience competition between instructions, not any one sentence being
    wrong. brand_consistent was never implicated (7/7 correct on every
    fixture in every run), so the split follows the collision the data
    actually shows: text_legible alone here, brand_consistent +
    info_accurate together in build_content_messages().

    NOTE: this call deliberately does NOT interpolate fact-sheet.md.
    Judging whether text is readable needs no ground truth about the
    business -- only info_accurate does. Splitting therefore SHRINKS this
    call's prompt rather than duplicating the old one, which is why the
    added cost is one extra image upload rather than a doubling.

      - text_legible: are distinct text elements legible on their own
      - notes: reasoning, required whether it passed or failed

    The text_legible clause below is FROZEN exactly as verified on
    2026-09-02 (7/7 correct on all five fixtures, before the info_accurate
    edit disturbed it). Do not tune wording and split in the same step --
    removing that confound is the entire point of the split.
    """
    system_prompt = """You are auditing an image from Riverside Hardware against the check below. Evaluate exactly one thing and always explain your findings, regardless of pass or fail.

        Check:
        - text_legible: are distinct text elements legible on their own — one legible element, such as the business name, does not make other, separate text elements legible or vice versa. Legible should be defined as readable by a typical human without undue effort or assistance. Do not weight any single text element more heavily than another, regardless of legibility. Font variations that do not negatively impact human readability are not an issue
        - notes: brief reasoning for whatever it flagged (or "no issues found" if it passed)

        Explain your findings, regardless of pass or fail, and write your explanations for your findings into 'notes'. Do not leave it empty."""

    user_prompt = ("Audit the thumbnail image below for text legibility and "
                   "return your findings.")

    return _build_messages(system_prompt, user_prompt, image_b64, mime_type)


def build_content_messages(image_b64: str, mime_type: str = "image/png") -> list[dict]:
    """Build the messages for call 2 of the split audit: brand consistency
    and info accuracy, checked together against fact-sheet.md.

    These two stay in one call on purpose. brand_consistent has never once
    been implicated in a contamination event -- 7/7 correct on every fixture
    across every run, including item4's intended failure -- and both checks
    need the fact sheet in context, so separating them would pay a third
    image upload to solve a problem that has never appeared. If a future
    regression run ever shows these two interfering, the same evidence
    standard applies and they split too.

      - brand_consistent: is the dominant palette orange/cream
      - info_accurate: do the visible assertions match the fact sheet
      - notes: reasoning, required whether it passed or failed

    Both clauses are FROZEN as verified 2026-09-02: info_accurate at 7/7 on
    every fixture in the afternoon run (the wording that finally worked
    defines the passing condition by absence -- "when nothing legible
    contradicts the fact sheet, record it as True" -- so unreadable text
    drops out of the comparison instead of counting as a failed match),
    and brand_consistent unchanged since it has never needed a fix.
    """
    system_prompt = f"""You are auditing an image from Riverside Hardware against the actual business details and the checks below. Evaluate exactly two things and always explain your findings, regardless of pass or fail.

        Grounded truth:
        {fact_sheet}

        Checks:
        - brand_consistent: is the dominant palette orange (#FD5A1E family) / cream (#EFE4B0 family) -- flag anything materially different. Small color variations that do not impact brand consistency are not an issue
        - info_accurate: do the visible assertions (hours, services) in the image match the fact sheet content and if not, identify the discrepancy. When nothing legible contradicts the fact sheet, record it as True. Do not allow any single assertion's accuracy, or lack thereof, to affect another. Evaluations are to be independently made and reported. Accuracy is not dependent on legibility and vice versa. When accuracy cannot be determined due to legibility issues, note this explicitly. A headline or title describing the content's topic is not itself a checkable assertion. Do not make assumptions about the business details beyond what is in the fact sheet
        - notes: brief reasoning for whatever it flagged (or "no issues found" if everything passed)

        Explain your findings, regardless of pass or fail, and write your explanations for your findings into 'notes'. Do not leave it empty."""

    user_prompt = ("Audit the thumbnail image below against the Riverside "
                   "Hardware & Supply brand guide and fact sheet and return "
                   "your findings.")

    return _build_messages(system_prompt, user_prompt, image_b64, mime_type)


def audit_thumbnail(image_path: str) -> str:
    """
    Audit a marketing thumbnail image against Riverside Hardware & Supply's
    brand guide and posted hours (fact-sheet.md): checks whether the text
    rendered in the image is legible, whether the dominant color palette
    matches the brand's orange/cream family, and whether the factual
    assertions visible in the image (hours, services, etc.) match the fact
    sheet.

    Runs as TWO model calls as of 2026-09-02 (legibility, then brand +
    info accuracy) and merges them, so that a wording change to one check
    cannot disturb another -- see build_legibility_messages() for the
    evidence behind that. The merge is deliberate: the return shape is
    unchanged, so the orchestrator agent's tool contract does not change
    just because the implementation did.

    :param image_path (str): Path to the thumbnail image file to audit.
    :return: JSON string with keys text_legible (bool), brand_consistent
        (bool), info_accurate (bool), and notes (str) explaining any flag
        raised (or confirming a clean pass). Notes from the two calls are
        concatenated with [legibility] / [content] labels so each verdict's
        reasoning stays attributable to the call that produced it.
    :rtype: str
    """
    client = build_audit_client()
    # Encode once, reuse for both calls -- the image is identical, only the
    # prompts differ. Re-encoding per call would re-read the file for no gain.
    image_b64 = encode_image(Path(image_path))
    model = os.environ["CHAT_DEPLOYMENT_GPT_5_4_MINI"]

    # temperature/seed pinned 2026-09-01 -- see the temperature-pinning item
    # in m7-orientation.md's backlog. Neither param guarantees bit-exact
    # determinism on Azure OpenAI, but both substantially reduce variance,
    # which is what makes a 7-run stability probe interpretable at all.
    # Both calls pin identically: an unpinned call in a split pair would
    # reintroduce exactly the noise the split is meant to eliminate.
    legibility: LegibilityAudit = client.beta.chat.completions.parse(
        model=model,
        messages=build_legibility_messages(image_b64),
        response_format=LegibilityAudit,
        temperature=0,
        seed=42,
    ).choices[0].message.parsed

    content: ContentAudit = client.beta.chat.completions.parse(
        model=model,
        messages=build_content_messages(image_b64),
        response_format=ContentAudit,
        temperature=0,
        seed=42,
    ).choices[0].message.parsed

    # Merge back into the original three-boolean shape. Callers
    # (probe_fixture_stability.py, main(), and eventually the orchestrator's
    # FunctionTool) see no difference from the single-call version.
    merged = ThumbnailAudit(
        text_legible=legibility.text_legible,
        brand_consistent=content.brand_consistent,
        info_accurate=content.info_accurate,
        notes=f"[legibility] {legibility.notes}\n[content] {content.notes}",
    )
    return merged.model_dump_json()


def main():

    folder = Path(__file__).parent / ".." / "iip-docs" / "m7-riverside-hardware"

    all_pngs = sorted(folder.glob("*.png"))
    fixtures = [f for f in all_pngs if f.name in EXPECTED_RESULTS]
    skipped = [f for f in all_pngs if f.name not in EXPECTED_RESULTS]

    if skipped:
        print(f"Skipping {len(skipped)} PNG(s) not in EXPECTED_RESULTS: "
              f"{[f.name for f in skipped]}\n")

    pass_count = 0

    for image_file in fixtures:
        print(f"Auditing {image_file.name}...")
        actual = json.loads(audit_thumbnail(str(image_file)))
        expected = EXPECTED_RESULTS[image_file.name]

        mismatches = [
            field for field in ("text_legible", "brand_consistent", "info_accurate")
            if actual[field] != expected[field]
        ]

        if mismatches:
            print(f" MISMATCH on {mismatches} -- expected {expected}, "
                f"got { {k: actual[k] for k in expected} }")
        else:
            print(" PASS -- all three dimensions matched expected")
            pass_count += 1

        print(f" notes: {actual['notes']}\n")

    print(f"{pass_count}/{len(fixtures)} fixtures matched expected results.")


if __name__ == "__main__":
    main()
