"""
function_app.py -- M11's Function entry point (Python v2 programming model).

Written by Claude, 2026-09-24. A thin adapter: every decision lives in
upload_handler.py, which runs without the Functions host (see local_run.py).

The connection "UploadEvents" is IDENTITY-BASED. It needs these app settings,
which the M11 Bicep sets (no connection string, no key):
  UploadEvents__queueServiceUri = https://stiipdevwus01.queue.core.windows.net
  UploadEvents__credential      = managedidentity
  UploadEvents__clientId        = <client ID of id-iip-dev-wus-01>
The roles behind it are RBAC rows 15 and 16 (phase2-rbac-model-draft.md).
"""

import json
import logging

import azure.functions as func

app = func.FunctionApp()


@app.queue_trigger(arg_name="msg", queue_name="upload-events",
                   connection="UploadEvents")
def process_upload(msg: func.QueueMessage) -> None:
    # Imported here, not at the top: keeps the orchestrator's ~4.6 s of imports
    # (probe 2) out of the host's 30-second start window.
    from upload_handler import process

    summary = process(msg.get_body().decode("utf-8"),
                      dequeue_count=msg.dequeue_count)
    logging.info("process_upload: %s", json.dumps(summary, default=str))
