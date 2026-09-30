"""
results_page.py -- the M11 results page: what a signed-in viewer sees.

Written by Claude, 2026-09-30, to Gerard's decisions of the same day: a list
plus a detail view, served at /api/results, host.json unchanged.

WHY THIS IS NOT IN function_app.py. Like upload_handler.py, this module never
imports azure.functions, so its rendering can be tested without the Functions
host. function_app.py is a thin adapter over it.

WHO READS WHAT
  * The VIEWER signs in through built-in authentication (Easy Auth), gated by
    "Assignment required" on IIP Results (dev) (RBAC rows 10, 11). The viewer
    holds NO Azure role (RBAC principle 3) and never touches storage.
  * THIS CODE reads the `results` container with the Function's own identity,
    id-iip-dev-wus-01 (AZURE_CLIENT_ID), under RBAC row 6.

SECURITY, IN ORDER OF IMPORTANCE
  1. The gate is Easy Auth, configured in app.bicep (requireAuthentication).
  2. require_principal() is a second lock. Easy Auth injects the
     X-MS-CLIENT-PRINCIPAL-* headers for a signed-in user and strips any
     that a client sends itself. If they're absent, Easy Auth didn't
     authenticate this request (for example, if it was switched off by
     mistake), so the page refuses with 401 instead of going public.
  3. Every value from a result file is HTML-escaped. The drafted copy is
     model output, and model output is untrusted input to a web page.
  4. The detail route only accepts names shaped like the ones
     upload_handler._write_result() writes, so a crafted URL can't read an
     arbitrary blob.
  5. Responses carry a strict Content-Security-Policy (no scripts at all),
     nosniff, and no-store. The page must not sit in a shared cache.
"""

from __future__ import annotations

import html
import json
import os
import re
from urllib.parse import quote

RESULTS_CONTAINER = "results"
LIST_LIMIT = 25

# upload_handler._write_result(): "<upload stem>/<YYYYMMDDTHHMMSSZ>.json"
_STEM_RE = re.compile(r"^[A-Za-z0-9._ ()-]{1,200}$")
_STAMP_RE = re.compile(r"^\d{8}T\d{6}Z$")

AUDIT_FIELDS = ("text_legible", "brand_consistent", "info_accurate")

SECURITY_HEADERS = {
    "Content-Security-Policy": ("default-src 'none'; style-src 'unsafe-inline'; "
                                "base-uri 'none'; form-action 'none'; frame-ancestors 'none'"),
    "X-Content-Type-Options": "nosniff",
    "Cache-Control": "no-store",
    "Referrer-Policy": "no-referrer",
}


class NotSignedIn(Exception):
    """No Easy Auth principal on the request."""


class BadName(Exception):
    """A detail URL that doesn't name a result this page would have written."""


# --- the viewer --------------------------------------------------------------------
def require_principal(headers) -> str:
    """Return the signed-in viewer's display name, or raise NotSignedIn.

    `headers` is any case-insensitive mapping (func.HttpRequest.headers is).
    """
    principal_id = headers.get("x-ms-client-principal-id")
    if not principal_id:
        raise NotSignedIn()
    return headers.get("x-ms-client-principal-name") or principal_id


# --- storage (identity -01; RBAC row 6) ---------------------------------------------
_service = None


def _container():
    """The results container, via DefaultAzureCredential (AZURE_CLIENT_ID = -01)."""
    global _service
    if _service is None:
        from azure.identity import DefaultAzureCredential
        from azure.storage.blob import BlobServiceClient
        _service = BlobServiceClient(os.environ["RESULTS_BLOB_ENDPOINT"],
                                     credential=DefaultAzureCredential())
    return _service.get_container_client(RESULTS_CONTAINER)


def blob_name(stem: str, stamp: str) -> str:
    """Validate a detail URL's two parts and rebuild the blob name from them."""
    if not _STEM_RE.match(stem or "") or ".." in stem or not _STAMP_RE.match(stamp or ""):
        raise BadName()
    return f"{stem}/{stamp}.json"


def load_newest(container, limit: int = LIST_LIMIT) -> list[tuple[str, dict | None]]:
    """(blob name, parsed JSON or None) for the newest `limit` result files."""
    blobs = [b for b in container.list_blobs() if b.name.endswith(".json")]
    blobs.sort(key=lambda b: b.last_modified, reverse=True)
    out = []
    for b in blobs[:limit]:
        try:
            data = json.loads(container.download_blob(b.name).readall())
        except (ValueError, UnicodeDecodeError):
            data = None
        out.append((b.name, data))
    return out


def load_one(container, name: str) -> dict:
    """Parsed JSON for one result. Raises ResourceNotFoundError if absent."""
    return json.loads(container.download_blob(name).readall())


# --- what the page shows from a result -------------------------------------------
def summarize(name: str, data: dict | None) -> dict:
    """The fields one list row shows. Tolerates older or partial result files."""
    stem, _, rest = name.partition("/")
    row = {"name": name, "stem": stem, "stamp": rest.removesuffix(".json"),
           "status": None, "topic": None, "run_status": None,
           "audit": None, "text_passed": None, "redrafts": None, "error": None}
    if not isinstance(data, dict):
        row["status"] = "unreadable"
        return row
    record = data.get("record") or {}
    upload = data.get("upload") or {}
    row.update(
        status=data.get("status"),
        topic=upload.get("topic") or record.get("topic"),
        run_status=record.get("run_status"),
        audit=record.get("actual_audit"),
        text_passed=record.get("final_text_passed"),
        redrafts=record.get("redrafts"),
        error=data.get("error"),
    )
    return row


def final_draft(data: dict) -> str | None:
    """The agent's last message: its final drafted copy.

    Same role test run_item() uses for its printed tail: anything not a user
    message is the agent's.
    """
    messages = ((data.get("record") or {}).get("messages")) or []
    agent = [m for m in messages if "user" not in str(m.get("role", "")).lower()]
    return agent[-1].get("text") if agent else None


# --- rendering (every value escaped) ----------------------------------------------
_CSS = """
body{font-family:Segoe UI,system-ui,sans-serif;background:#0e0f11;color:#e8e6e1;margin:0;padding:24px}
h1{font-size:22px;margin:0 0 4px}h2{font-size:17px;margin:24px 0 8px}
.who{color:#9aa0a6;font-size:13px;margin-bottom:18px}
table{border-collapse:collapse;width:100%;font-size:14px}
th,td{text-align:left;padding:7px 10px;border-bottom:1px solid #2a2d33;vertical-align:top}
th{color:#9aa0a6;font-weight:600}
a{color:#7fb3ff}
.ok{color:#6fcf97}.bad{color:#ff7b72}.na{color:#9aa0a6}
pre{white-space:pre-wrap;background:#16181c;border:1px solid #2a2d33;padding:14px;border-radius:6px;font-size:14px;line-height:1.5}
dl{display:grid;grid-template-columns:max-content 1fr;gap:6px 16px;font-size:14px}dt{color:#9aa0a6}
.note{color:#9aa0a6;font-size:13px}
"""


def _e(value) -> str:
    return html.escape("" if value is None else str(value), quote=True)


def _verdict(value) -> str:
    if value is True:
        return '<span class="ok">pass</span>'
    if value is False:
        return '<span class="bad">fail</span>'
    return '<span class="na">—</span>'


def _audit_cells(audit) -> str:
    audit = audit if isinstance(audit, dict) else {}
    return "".join(f"<td>{_verdict(audit.get(k))}</td>" for k in AUDIT_FIELDS)


def _page(title: str, viewer: str, body: str) -> str:
    return (f"<!doctype html><html lang=\"en\"><head><meta charset=\"utf-8\">"
            f"<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">"
            f"<title>{_e(title)}</title><style>{_CSS}</style></head><body>"
            f"<h1>{_e(title)}</h1><div class=\"who\">Signed in as {_e(viewer)}</div>"
            f"{body}</body></html>")


def render_list(rows: list[dict], viewer: str) -> str:
    if not rows:
        body = "<p>No results yet.</p>"
    else:
        head = ("<tr><th>Upload</th><th>Result time (UTC)</th><th>Topic</th><th>Status</th>"
                "<th>Legible</th><th>Brand</th><th>Info</th><th>Copy passed</th></tr>")
        trs = []
        for r in rows:
            # URL-encode the path segments, then HTML-escape the result.
            link = _e(f"results/{quote(r['stem'], safe='')}/{quote(r['stamp'], safe='')}")
            trs.append(
                f"<tr><td><a href=\"{link}\">{_e(r['stem'])}</a></td>"
                f"<td>{_e(r['stamp'])}</td><td>{_e(r['topic'])}</td>"
                f"<td>{_e(r['status'])}</td>{_audit_cells(r['audit'])}"
                f"<td>{_verdict(r['text_passed'])}</td></tr>")
        body = (f"<table>{head}{''.join(trs)}</table>"
                f"<p class=\"note\">Newest {LIST_LIMIT} results. Audit verdicts are the "
                f"audit tool's own output. An uploaded item has no answer key, so these "
                f"are verdicts, not scores.</p>")
    return _page("IIP results (dev)", viewer, body)


def render_detail(name: str, data: dict, viewer: str) -> str:
    r = summarize(name, data)
    audit = r["audit"] if isinstance(r["audit"], dict) else {}
    facts = "".join(f"<dt>{_e(k)}</dt><dd>{v}</dd>" for k, v in [
        ("Upload", _e(r["stem"])),
        ("Result time (UTC)", _e(r["stamp"])),
        ("Topic", _e(r["topic"])),
        ("Status", _e(r["status"])),
        ("Agent run", _e(r["run_status"])),
        ("Redrafts", _e(r["redrafts"])),
        ("Copy passed", _verdict(r["text_passed"])),
        *[(f"Audit: {k}", _verdict(audit.get(k))) for k in AUDIT_FIELDS],
    ])
    parts = [f"<p><a href=\"../../results\">← All results</a></p><dl>{facts}</dl>"]
    if r["error"]:
        parts.append(f"<h2>Error</h2><pre>{_e(r['error'])}</pre>")
    draft = final_draft(data)
    if draft:
        parts.append(f"<h2>Final drafted copy</h2><pre>{_e(draft)}</pre>")
    return _page(f"Result: {r['stem']}", viewer, "".join(parts))


def render_message(title: str, message: str, viewer: str = "unknown") -> str:
    return _page(title, viewer, f"<p>{_e(message)}</p>")
