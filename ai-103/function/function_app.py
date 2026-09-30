"""
function_app.py -- M11's Function entry point (Python v2 programming model).

Written by Claude, 2026-09-24; results page added 2026-09-30. A thin adapter:
the decisions live in upload_handler.py and results_page.py, which run without
the Functions host (see local_run.py).

The connection "UploadEvents" is IDENTITY-BASED. It needs these app settings,
which the M11 Bicep sets (no connection string, no key):
  UploadEvents__queueServiceUri = https://stiipdevwus01.queue.core.windows.net
  UploadEvents__credential      = managedidentity
  UploadEvents__clientId        = <client ID of id-iip-dev-wus-01>
The roles behind it are RBAC rows 15 and 16 (phase2-rbac-model-draft.md).

The results page (RBAC rows 6, 10, 11, 17) needs RESULTS_BLOB_ENDPOINT and
built-in authentication, both set by app.bicep. Its auth level is ANONYMOUS
on purpose: built-in authentication is the gate, and a function key would add
a shared secret to every URL, which is the opposite of keyless.
results_page.require_principal() is the second lock.
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


def _respond(body: str, status: int = 200) -> func.HttpResponse:
    import results_page as rp
    return func.HttpResponse(body, status_code=status, mimetype="text/html",
                             charset="utf-8", headers=rp.SECURITY_HEADERS)


@app.route(route="results", methods=["GET"], auth_level=func.AuthLevel.ANONYMOUS)
def results_list(req: func.HttpRequest) -> func.HttpResponse:
    import results_page as rp
    try:
        viewer = rp.require_principal(req.headers)
    except rp.NotSignedIn:
        return _respond(rp.render_message("Not signed in", "Sign-in is required."), 401)
    rows = [rp.summarize(name, data) for name, data in rp.load_newest(rp._container())]
    return _respond(rp.render_list(rows, viewer))


@app.route(route="results/{stem}/{stamp}", methods=["GET"],
           auth_level=func.AuthLevel.ANONYMOUS)
def results_detail(req: func.HttpRequest) -> func.HttpResponse:
    import results_page as rp
    from azure.core.exceptions import ResourceNotFoundError
    try:
        viewer = rp.require_principal(req.headers)
    except rp.NotSignedIn:
        return _respond(rp.render_message("Not signed in", "Sign-in is required."), 401)
    try:
        name = rp.blob_name(req.route_params.get("stem"), req.route_params.get("stamp"))
        data = rp.load_one(rp._container(), name)
    except (rp.BadName, ResourceNotFoundError):
        return _respond(rp.render_message("Not found", "No such result.", viewer), 404)
    return _respond(rp.render_detail(name, data, viewer))
