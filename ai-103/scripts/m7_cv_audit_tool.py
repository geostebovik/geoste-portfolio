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


def build_audit_messages(image_b64: str, mime_type: str = "image/png") -> list[dict]:
    """Build the chat.completions messages list for the audit call.

      - text_legible: is any text rendered IN THE IMAGE actually readable
      - brand_consistent: is the dominant palette orange (#FD5A1E family) /
        cream (#EFE4B0 family) -- flag anything materially different
        (the fact sheet's own example: blue/gray)
      - info_accurate: do the visible assertions (hours, services) in
        the image match the fact sheet content below, evaluated
        independently per assertion -- a headline/title naming a topic
        does NOT count as a checkable assertion (fixed 2026-09-01 after
        item2's clean-control headline, "Seasonal Home Maintenance
        Checklist", kept reading as an implied service claim -- 43% false
        positive rate across 7 manual runs, all under pinned
        temperature=0/seed=42, so not sampling noise). See
        content-items-plan.md's "Design constraint for future items" --
        this exemption means a future flawed item's info-accuracy violation
        MUST live in a separate visible element, not the item's own
        headline. This is why the fact sheet text is interpolated into the
        prompt, same principle as evaluate_draft() passing `context` to the
        text evaluators
      - notes: brief reasoning for whatever it flagged (or "no issues
        found" if everything passed)

    Structure mirrors m7_vision_test.py's build_vision_messages(): a text
    part plus an image part inside the user message's content list.
    """
    system_prompt = f"""You are auditing an image from Riverside Hardware against the actual business details and the checks below. Evaluate exactly three things and always explain your findings, regardless of pass or fail.

        Grounded truth:
        {fact_sheet}

        Checks:
        - text_legible: are distinct text elements legible on their own — one legible element, such as the business name, does not make other, separate text elements legible. Do not weight any single text element more heavily than another, regardless of legibility. Font variations that do not negatively impact human readability are not an issue
        - brand_consistent: is the dominant palette orange (#FD5A1E family) / cream (#EFE4B0 family) -- flag anything materially different. Small color variations that do not impact brand consistency are not an issue
        - info_accurate: do the visible assertions (hours, services) in the image match the fact sheet content and if not, identify the discrepancy. Do not allow any single assertion's accuracy, or lack thereof, to affect another. Evaluations are to be independently made and reported. A headline or title describing the content's topic is not itself a checkable assertion. Do not make assumptions about the business details beyond what is in the fact sheet
        - notes: brief reasoning for whatever it flagged (or "no issues found" if everything passed)

        Explain your findings, regardless of pass or fail, and write your explanations for your findings into 'notes'. Do not leave it empty."""

    user_prompt = "Audit the thumbnail image below against the Riverside Hardware & Supply brand guide and fact sheet and return your findings."

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


def audit_thumbnail(image_path: str) -> str:
    """
    Audit a marketing thumbnail image against Riverside Hardware & Supply's
    brand guide and posted hours (fact-sheet.md): checks whether any text
    rendered in the image is legible, whether the dominant color palette
    matches the brand's orange/cream family, and whether any factual claim
    visible in the image (hours, services, etc.) matches the fact sheet.

    :param image_path (str): Path to the thumbnail image file to audit.
    :return: JSON string with keys text_legible (bool), brand_consistent
        (bool), info_accurate (bool), and notes (str) explaining any flag
        raised (or confirming a clean pass).
    :rtype: str
    """
    client = build_audit_client()
    image_b64 = encode_image(Path(image_path))
    messages = build_audit_messages(image_b64)

    model = os.environ["CHAT_DEPLOYMENT_GPT_5_4_MINI"]

    # TODO -- run this for real against item1 (a CLEAN fixture) first. If
    # response_format isn't accepted on this deployment/api_version combo,
    # that raises here -- don't silently swallow it. Fallback plan if it
    # doesn't work: plain chat.completions.create() + json.loads() on the
    # response text, with a try/except around the parse (the model can
    # still occasionally return near-miss JSON without structured outputs
    # enforcing the shape).
    # temperature/seed pinned 2026-09-01 -- see the backlog's temperature-
    # pinning item in m7-orientation.md. Decided ahead of the brand_consistent
    # regression reruns rather than after, specifically so those reruns can
    # tell apart "real ripple effect from the text_legible wording change"
    # from ordinary run-to-run sampling noise, instead of conflating both
    # under one unpinned signal. Neither param guarantees bit-exact
    # determinism on Azure OpenAI, but both substantially reduce variance.
    response = client.beta.chat.completions.parse(
        model=model,
        messages=messages,
        response_format=ThumbnailAudit,
        temperature=0,
        seed=42,
    )

    result: ThumbnailAudit = response.choices[0].message.parsed
    return result.model_dump_json()


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
