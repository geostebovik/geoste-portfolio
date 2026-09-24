"""
local_run.py -- run the Function's per-upload logic on the laptop, without the
Functions host.

Written by Claude, 2026-09-24. It builds the Event Grid BlobCreated event the
queue would have delivered, for a blob ALREADY in `uploads`, and hands it to
upload_handler.process(). Everything runs for real, except the queue and the
host: Gerard's sign-in (DefaultAzureCredential), the blob read, one agent run
(roughly 1-2 minutes and a few cents of tokens), and the result written to
`results`.

    python local_run.py item4-key-cutting-FLAW-brand.png

Run it from ai-103/function with the venv active and ../scripts/.env present,
the same .env the M7 scripts use.
"""

import json
import sys
from pathlib import Path

from dotenv import load_dotenv

ACCOUNT_URL = "https://stiipdevwus01.blob.core.windows.net"


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    blob_name = sys.argv[1]
    load_dotenv(Path(__file__).resolve().parent.parent / "scripts" / ".env")

    from upload_handler import process
    event = {
        "id": "local-run",
        "eventType": "Microsoft.Storage.BlobCreated",
        "eventTime": None,
        "data": {"url": f"{ACCOUNT_URL}/uploads/{blob_name}"},
    }
    summary = process(json.dumps(event), dequeue_count=None)
    print(json.dumps(summary, indent=2, default=str))
    return 0 if summary.get("status") in ("ok", "skipped") else 1


if __name__ == "__main__":
    sys.exit(main())
