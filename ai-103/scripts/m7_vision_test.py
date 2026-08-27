#!/usr/bin/env python3
"""
M7 -- IIP: confirm the gpt-5-4-mini Foundry deployment accepts image input
via the OpenAI-compatible vision content-array format.

Why this script exists: two signals (MS docs' "GPT-5 series" vision claim,
and the Foundry Toolkit catalog tagging gpt-5.4/gpt-5.4-mini with Image
Attachment support) both point the same way, but neither is a live call
against YOUR deployment. This is that live call -- expected to just work;
if it doesn't, that's a real finding worth digging into, not a bug in this
script to quietly work around.

Reuses m3_analyze.py's get_endpoint()/get_subscription_key() -- same
live-fetch-the-key-via-az-cli pattern, nothing secret written to disk --
and mirrors m6_generate.py's build_client() shape, so this stays consistent
with the existing scripts instead of inventing a second way to authenticate.

"""

import base64, json, os
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from openai import AzureOpenAI

from m3_analyze import get_endpoint, get_subscription_key  # reuse, don't rewrite


# One of the five M7 thumbnails -- start with the clean one, per the
# handoff doc. Built on Path(__file__).parent so this works regardless of
# the terminal's cwd -- m6_generate.py/m6_assemble.py both use a bare
# relative string instead ("../iip-docs/...") and that's a known, already-
# flagged gotcha (STATUS.md) when launched from the wrong folder. Don't
# repeat it here.
IMAGE_PATH = (
    Path(__file__).parent
    / ".."
    / "iip-docs"
    / "m7-riverside-hardware"
    / "item1-paint-mixing-CLEAN.png"
).resolve()


def build_client() -> AzureOpenAI:
    # Build and return an AzureOpenAI client
    load_dotenv()

    account, rg = os.environ["AIF_ACCOUNT"], os.environ["AIF_RESOURCE_GROUP"]
    endpoint = get_endpoint(account, rg)
    key = get_subscription_key(account, rg)

    client = AzureOpenAI(
        azure_endpoint=endpoint,
        api_key=key,
        api_version=os.environ["CHAT_API_VERSION"],  # "2024-06-01" 
    )
    
    return client


def encode_image(path: Path) -> str:
    """Read the image file in binary mode and return it as a base64 string
     -- IMAGE_PATH is a known PNG.
    """
    return base64.b64encode(path.read_bytes()).decode("ascii")


def build_vision_messages(image_b64: str, mime_type: str = "image/png") -> list[dict]:
    """Build the chat.completions messages list using the vision
    content-array format.

    mime_type is a parameter, not hardcoded -- decided Aug 25 (see STATUS.md
    "Next action"): M7's orchestrator is meant to eventually accept
    visitor-submitted images on the live site, which won't all be PNGs. The
    default keeps today's call against the PNG thumbnail working unchanged.

    The "user" message's content is a LIST, not a plain string -- a list of typed
    parts instead of one string, so a single message can carry text and an
    image (or several) together instead of being limited to one or the
    other. Two parts here: a text instruction, then the image itself as a
    data: URL (embedding the base64 bytes directly, since this is a local
    file with nothing to host it at a real URL).
    """
    system_prompt = (
        "You are reviewing a rendered marketing thumbnail for Riverside "
        "Hardware & Supply, a fictional small-town hardware store. Describe "
        "what you see factually and specifically -- the text present, "
        "whether it's legible, the layout, and the colors used -- rather "
        "than a generic scene description."
    )
    user_prompt = "Describe this marketing thumbnail in detail."

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


def main():
    client = build_client()
    image_b64 = encode_image(IMAGE_PATH)
    messages = build_vision_messages(image_b64)

    model = os.environ["CHAT_DEPLOYMENT_GPT_5_4_MINI"]  # deployment name from .env,
    # not a hardcoded model string -- same discipline as m6_generate.py
    response = client.chat.completions.create(
        model=model,
        messages=messages,
    )

    description = response.choices[0].message.content
    print(description)

    # Save a record either way (works or breaks), matching m6_generate.py's
    # Path("results") + timestamp pattern -- don't rely on terminal
    # scrollback alone.
    results_dir = Path(__file__).parent / "results"
    results_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    out_path = results_dir / f"{timestamp}_vision_test.json"
    out_path.write_text(json.dumps({
        "image_path": str(IMAGE_PATH),
        "model": model,
        "description": description,
    }, indent=2))
    print(f"Saved: {out_path}")


if __name__ == "__main__":
    main()
