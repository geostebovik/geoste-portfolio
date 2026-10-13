"""
tracing.py -- M14 part 3: OpenTelemetry traces from the Function to App Insights.

Written by Claude, 2026-10-13, to Gerard's decisions D-M14-3 (trace now, on the
classic Agents API), D-M14-6 (the lean package set, not the distro) and D-M14-7
(a span around the orchestrator's logged() wrapper, so each tool call is named).
Design and sources: ../m14-prep.md, "Part 3".

WHAT ONE TRACED UPLOAD LOOKS LIKE in App Insights (Transaction search -> the
process_upload request -> end-to-end view):

  process_upload                       the HOST's request (not ours)
  └ iip.process_upload                 invocation_span(), below
    ├ blob / Vision / agents HTTP      Azure SDK spans (azure-core bridge)
    ├ create_agent, create_thread ...  the Agents SDK's own spans
    └ create_and_process
      └ execute_tool get_fact_sheet    instrument_tools(), below
        execute_tool evaluate_draft
        execute_tool audit_thumbnail

WHAT IT DOESN'T SHOW, on purpose or by limit:
  - No message content, prompts, tool arguments or tool output. The prompts
    carry the store's fact sheet, and the trace doesn't need them. Content
    recording is switched off in code below, not by an app setting.
  - The judge's own model call. evaluate_draft reaches its model through the
    `openai` package, which the lean set doesn't instrument. Its time is still
    inside the `execute_tool evaluate_draft` span.

WHY NOT configure_azure_monitor() (the distro). Gerard chose the lean set
(D-M14-6): the distro adds 25 packages, 13 of them for frameworks this Function
doesn't use. This module does the three parts of it that matter here: a tracer
provider with the Azure Monitor exporter, the Azure SDK bridge, and nothing for
logs. The Functions worker already sends logs, so adding a log exporter would
duplicate every AppTraces row (Microsoft Learn, OpenTelemetry with Azure
Functions).

AUTHENTICATION. App Insights accepts only Entra-authenticated telemetry (M11).
The exporter builds its credential from APPLICATIONINSIGHTS_AUTHENTICATION_STRING
when none is passed (exporter README, 1.0.0b58), and that setting already names
the Function's identity, id-iip-dev-wus-01, which holds Monitoring Metrics
Publisher (RBAC row 8). So no new role and no new setting.

OFF SWITCHES, both checked once per worker process:
  - No APPLICATIONINSIGHTS_CONNECTION_STRING (the laptop, local_run.py): every
    function here is a no-op.
  - App setting IIP_TRACING=off: the same, in Azure, without a redeploy.

RETIRES WITH THE CLASSIC API (2027-03-31, Todoist): AIAgentsInstrumentor and
the logged() patch are both classic-SDK specific and get redone at that
migration (D-M14-3).
"""

from __future__ import annotations

import contextlib
import functools
import logging
import os

_log = logging.getLogger(__name__)

TRACER_NAME = "iip.function"

_enabled: bool | None = None   # None = setup() hasn't run in this process yet
_provider = None


def setup(_exporter=None) -> bool:
    """Configure tracing once per worker process. Returns whether it's on.

    `_exporter` is for the offline tests only: they pass an in-memory exporter
    instead of sending to App Insights.
    """
    global _enabled, _provider
    if _enabled is not None:
        return _enabled

    connection_string = os.environ.get("APPLICATIONINSIGHTS_CONNECTION_STRING")
    if os.environ.get("IIP_TRACING", "").strip().lower() == "off":
        _log.info("tracing: off (IIP_TRACING=off)")
        _enabled = False
        return False
    if not connection_string and _exporter is None:
        _enabled = False   # the laptop: nothing to send to
        return False

    # The Azure SDK bridge. Must be set BEFORE the Agents SDK is instrumented,
    # because the instrumentor asks azure-core which span type to create.
    from azure.core.settings import settings
    settings.tracing_implementation = "opentelemetry"

    from opentelemetry import trace
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor, SimpleSpanProcessor
    from azure.monitor.opentelemetry.exporter import ApplicationInsightsSampler

    # service.name becomes cloud_RoleName in App Insights. The site name keeps
    # these spans on the same node as the host's own telemetry.
    resource = Resource.create({
        "service.name": os.environ.get("WEBSITE_SITE_NAME", "iip-function-local"),
    })
    # The exporter's README: ApplicationInsightsSampler MUST be used with
    # AzureMonitorTraceExporter. 1.0 = keep every trace; volume is a handful of
    # uploads a day.
    provider = TracerProvider(resource=resource,
                              sampler=ApplicationInsightsSampler(sampling_ratio=1.0))
    if _exporter is None:
        from azure.monitor.opentelemetry.exporter import AzureMonitorTraceExporter
        provider.add_span_processor(BatchSpanProcessor(
            AzureMonitorTraceExporter(connection_string=connection_string)))
    else:
        provider.add_span_processor(SimpleSpanProcessor(_exporter))
    trace.set_tracer_provider(provider)
    _provider = provider

    # The classic Agents SDK's own spans. Content recording OFF, explicitly:
    # the default would read AZURE_TRACING_GEN_AI_CONTENT_RECORDING_ENABLED, and
    # an app setting is easier to flip by accident than this line.
    from azure.ai.agents.telemetry import AIAgentsInstrumentor
    AIAgentsInstrumentor().instrument(enable_content_recording=False)

    _enabled = True
    _log.info("tracing: on (service.name=%s)",
              resource.attributes.get("service.name"))
    return True


@contextlib.contextmanager
def invocation_span(name: str, trace_parent: str | None = None,
                    trace_state: str | None = None, attributes: dict | None = None):
    """One span around one invocation, parented to the host's request.

    The host creates the request ("process_upload" in AppRequests) and hands
    the worker its W3C traceparent in context.trace_context. Parenting to it is
    what puts our spans in the same end-to-end view as the host's request; the
    worker doesn't do this by itself (Learn's Functions caveat).

    Flushes before returning, including on an exception, so a failed try's
    spans aren't lost if the instance is recycled or scaled in afterwards.
    """
    if not setup():
        yield None
        return

    from opentelemetry import trace
    from opentelemetry.trace import SpanKind
    from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator

    parent = None
    if trace_parent:
        carrier = {"traceparent": trace_parent}
        if trace_state:
            carrier["tracestate"] = trace_state
        parent = TraceContextTextMapPropagator().extract(carrier)

    tracer = trace.get_tracer(TRACER_NAME)
    try:
        # start_as_current_span records an exception and marks the span as
        # failed by default, then re-raises it, so the host's retry still happens.
        with tracer.start_as_current_span(name, context=parent, kind=SpanKind.INTERNAL,
                                          attributes=attributes or {}) as span:
            yield span
    finally:
        flush()


def flush(timeout_millis: int = 10_000) -> None:
    """Send what's buffered now rather than on the processor's 5 s schedule."""
    if _provider is not None:
        try:
            _provider.force_flush(timeout_millis=timeout_millis)
        except Exception:  # never let telemetry fail an upload
            _log.warning("tracing: flush failed", exc_info=True)


def instrument_tools(orch) -> None:
    """Name each tool call in the trace (D-M14-7).

    The Agents SDK 1.1.0 has an execute_tool span helper but never calls it
    (checked in its source on 2026-10-13), and with content recording off the
    tool names aren't recorded anywhere else. So this wraps the orchestrator's
    own logged() helper: every tool still goes through logged() exactly as
    certified, inside a span named `execute_tool <tool>`.

    NO CERTIFIED FILE CHANGES. This replaces the module attribute orch.logged
    at runtime, before build_toolset() is called. build_toolset() then builds
    the tool schema both ways and REFUSES TO RUN if the wrapping moved it. That
    check is what proves the agent sees exactly the tools it was certified with.

    Idempotent: a warm worker that handles a second upload doesn't wrap twice.
    """
    if not setup() or getattr(orch, "_iip_tools_traced", False):
        return

    from opentelemetry import trace

    certified_logged = orch.logged
    tracer = trace.get_tracer(TRACER_NAME)

    def traced_logged(fn):
        inner = certified_logged(fn)

        @functools.wraps(inner)
        def wrapper(*args, **kwargs):
            with tracer.start_as_current_span(
                f"execute_tool {fn.__name__}",
                attributes={
                    # Names only. Arguments and output stay out (content).
                    "gen_ai.operation.name": "execute_tool",
                    "gen_ai.tool.name": fn.__name__,
                },
            ):
                return inner(*args, **kwargs)

        return wrapper

    orch.logged = traced_logged
    orch._iip_tools_traced = True
