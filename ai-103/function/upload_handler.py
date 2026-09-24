"""
upload_handler.py -- the M11 Function's work for one upload.

Written by Claude, 2026-09-24, to the design Gerard approved the same day:
the Event Grid -> storage queue -> queue trigger shape (D-M11-1 (b)), the topic
carried as blob metadata, and one agent created and deleted per upload
(D-M11-3).

WHY THIS IS NOT IN function_app.py. This module never imports azure.functions,
so it runs on the laptop without the Functions host: local_run.py calls
process() with a hand-built event against a real blob. That tests everything
except the trigger itself before any Azure Function exists. function_app.py is
a thin adapter over it.

WHAT ONE CALL DOES
  1. Parse the queue message into an Event Grid event (see parse_event() on the
     encoding question).
  2. Ignore anything that isn't a BlobCreated in the `uploads` container, or
     isn't an image. Ignored events return normally, so they're never retried.
  3. Read the blob's `topic` metadata. If it's missing, write an ERROR result
     and return normally: a missing topic is the uploader's mistake, and
     retrying can't fix it.
  4. Download the image to a temp file. audit_thumbnail() reads a local path,
     exactly as it does for the fixtures.
  5. Import the orchestrator HERE, not at the top of the module (probe 2's
     insurance against the 30 s Flex host start), create one agent, run
     run_item() once, and delete the agent in `finally`.
  6. Write {upload, provenance, record} as JSON to
     results/<upload-stem>/<UTC timestamp>.json.

RELIES ON, and says so rather than hiding it: run_item() builds the thumbnail
path as FIXTURE_DIR / item["thumbnail"]. pathlib discards the left side when the
right side is absolute, so passing an ABSOLUTE temp path gives run_item the temp
file with no change to the certified orchestrator. A relative path here would
silently point into the fixtures folder instead.

NOT SAFE FOR CONCURRENT CALLS IN ONE PROCESS. The orchestrator keeps TOOL_CALLS
and _item_deadline at module level, so two uploads processed at once would
record each other's tool calls. host.json sets queues.batchSize = 1 and
newBatchThreshold = 0 for exactly this reason. Don't raise either value without
refactoring those globals first.
"""

from __future__ import annotations

import base64
import json
import os
import shutil
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from urllib.parse import unquote, urlparse

UPLOADS_CONTAINER = "uploads"
RESULTS_CONTAINER = "results"
TOPIC_METADATA_KEY = "topic"
IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg"}
BLOB_CREATED = "Microsoft.Storage.BlobCreated"


def _add_scripts_to_path() -> None:
    """Make the M7 modules importable by their bare names, as they import each other.

    Deployed package: <root>/function_app.py next to <root>/scripts/.
    Repo checkout (local_run.py): ai-103/function/ next to ai-103/scripts/.
    Either way the tools' own `../iip-docs/...` fact-sheet paths resolve,
    because build_package.py mirrors the repo layout. No certified module
    had to change for this.
    """
    here = Path(__file__).resolve().parent
    for candidate in (here / "scripts", here.parent / "scripts"):
        if (candidate / "m7_orchestrator.py").exists():
            if str(candidate) not in sys.path:
                sys.path.insert(0, str(candidate))
            return
    raise RuntimeError(f"m7_orchestrator.py not found beside {here}")


class Skipped(Exception):
    """An event this Function deliberately doesn't process. Not an error."""


def parse_event(body: str) -> dict:
    """Decode one queue message into one Event Grid event.

    VERIFY AT FIRST LIGHT: whether Event Grid writes the event to the queue as
    plain JSON or base64-encoded JSON. host.json sets messageEncoding = "none"
    so the host never rejects either form, and this function accepts both.
    The first real message settles it. Record which one in m11-prep.md, then
    this fallback can stay as harmless tolerance.
    """
    text = body.strip()
    try:
        event = json.loads(text)
    except json.JSONDecodeError:
        event = json.loads(base64.b64decode(text).decode("utf-8"))
    if isinstance(event, list):
        if len(event) != 1:
            raise ValueError(f"expected one event per message, got {len(event)}")
        event = event[0]
    return event


def blob_from_event(event: dict) -> tuple[str, str, str]:
    """Return (account_url, container, blob_name) for a BlobCreated in `uploads`.

    Accepts both the Event Grid schema (`eventType`) and the CloudEvents
    schema (`type`), since the subscription's schema is a Bicep choice.
    """
    event_type = event.get("eventType") or event.get("type")
    if event_type != BLOB_CREATED:
        raise Skipped(f"event type {event_type!r}")
    url = urlparse(event["data"]["url"])
    container, _, blob_name = url.path.lstrip("/").partition("/")
    blob_name = unquote(blob_name)
    if container != UPLOADS_CONTAINER:
        raise Skipped(f"container {container!r}")
    if PurePosixPath(blob_name).suffix.lower() not in IMAGE_SUFFIXES:
        raise Skipped(f"not an image: {blob_name!r}")
    return f"{url.scheme}://{url.netloc}", container, blob_name


def _write_result(service, blob_name: str, payload: dict) -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    result_name = f"{PurePosixPath(blob_name).stem}/{stamp}.json"
    service.get_blob_client(RESULTS_CONTAINER, result_name).upload_blob(
        json.dumps(payload, indent=2, default=str).encode("utf-8"),
        overwrite=False,
    )
    return f"{RESULTS_CONTAINER}/{result_name}"


def process(body: str, dequeue_count: int | None = None) -> dict:
    """Handle one queue message. Returns a short summary for the log."""
    from azure.identity import DefaultAzureCredential
    from azure.storage.blob import BlobServiceClient

    try:
        event = parse_event(body)
        account_url, container, blob_name = blob_from_event(event)
    except Skipped as why:
        return {"status": "skipped", "reason": str(why)}

    # With two user-assigned identities on the app (-01 runs the work, -03 is
    # the sign-in credential), AZURE_CLIENT_ID must name -01's client ID, or
    # DefaultAzureCredential can't tell which one to use. On the laptop it's
    # unset, and the credential falls through to Gerard's sign-in.
    credential = DefaultAzureCredential()
    service = BlobServiceClient(account_url, credential=credential)
    upload = {
        "container": container,
        "blob": blob_name,
        "event_id": event.get("id"),
        "event_time": event.get("eventTime") or event.get("time"),
        "dequeue_count": dequeue_count,
    }

    blob = service.get_blob_client(container, blob_name)
    props = blob.get_blob_properties()
    topic = (props.metadata or {}).get(TOPIC_METADATA_KEY)
    upload["topic"] = topic
    if not topic:
        where = _write_result(service, blob_name, {
            "status": "error",
            "error": (f"blob has no '{TOPIC_METADATA_KEY}' metadata. Upload with "
                      f"--metadata {TOPIC_METADATA_KEY}=\"<topic>\"; see "
                      f"function/README.md for the upload contract."),
            "upload": upload,
        })
        return {"status": "error", "reason": "missing topic", "result": where}

    workdir = Path(tempfile.mkdtemp(prefix="iip-upload-"))
    try:
        local_image = (workdir / PurePosixPath(blob_name).name).resolve()
        local_image.write_bytes(blob.download_blob().readall())

        _add_scripts_to_path()
        import m7_orchestrator as orch  # lazy on purpose -- see module docstring

        provenance = orch.run_provenance(script="function/upload_handler.py")
        provenance["host"] = {
            "site_name": os.environ.get("WEBSITE_SITE_NAME"),
            "instance_id": os.environ.get("WEBSITE_INSTANCE_ID"),
            "note": ("git fields describe the build tree when run on a laptop, "
                     "and are expected to be errors inside the Function, which "
                     "has no git. Deployed-package provenance is an M11 follow-up."),
        }

        client = orch.build_client()
        toolset = orch.build_toolset()
        client.enable_auto_function_calls(toolset)
        agent = client.create_agent(
            model=os.environ["CHAT_DEPLOYMENT_GPT_5_4"],
            name=orch.AGENT_NAME,
            instructions=orch.ACTIVE_INSTRUCTIONS,
            toolset=toolset,
            temperature=orch.AGENT_TEMPERATURE,
        )
        try:
            item = {
                "id": f"upload:{blob_name}",
                "topic": topic,
                "thumbnail": str(local_image),  # ABSOLUTE -- see module docstring
            }
            record = orch.run_item(client, agent.id, item)
        finally:
            client.delete_agent(agent.id)
    finally:
        shutil.rmtree(workdir, ignore_errors=True)

    where = _write_result(service, blob_name, {
        "status": "ok",
        "upload": upload,
        "provenance": provenance,
        "record": record,
    })
    return {
        "status": "ok",
        "result": where,
        "run_status": record.get("run_status"),
        "actual_audit": record.get("actual_audit"),
        "final_text_passed": record.get("final_text_passed"),
    }
