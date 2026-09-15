"""Record the structured-output schema a model call actually receives.

ADDED 2026-09-15 (Claude wrote it), after the Sep 15 orchestrator pass failed
its decision rule at 82/119 audit rows. The probes recorded the system prompt
and each Field description, and both were verified against the Sep 14 runs.
Neither recorded the ContentAudit CLASS DOCSTRING, which pydantic emits as the
schema's top-level "description" and the OpenAI SDK sends with every
response_format call -- 6,177 characters of it at d46353d, confirmed on
Gerard's venv. A channel the provenance does not record is a channel a change
can travel through unseen, which is how the Sep 14 A/B came to differ in more
than the one clause it was meant to test.

The rule this module enforces: record the WHOLE schema object the model is
sent, not a hand-picked list of the parts someone thought mattered. Read it
off the live class, never copy it, for the same reason the probes read the
system prompt out of build_content_messages().

Imports openai and pydantic lazily and never raises: provenance is worth
recording and never worth failing a run over (the same rule as provenance.py,
which stays stdlib-only and so cannot host this).
"""


def sent_schema(model) -> dict:
    """The JSON schema `response_format=model` puts on the wire, and its source.

    Prefers the SDK's own transform (openai.lib._pydantic.to_strict_json_schema),
    which is what the request actually carries. That path is private and
    openai is unpinned in requirements.txt, so it can move between versions;
    when it is unavailable this falls back to pydantic's model_json_schema(),
    which carries the same "description" but not the SDK's strict-mode
    additions. `source` says which one was recorded, so a reader never has to
    guess.
    """
    try:
        from openai.lib._pydantic import to_strict_json_schema
        import openai
        return {"source": f"openai {openai.__version__} to_strict_json_schema",
                "schema": to_strict_json_schema(model)}
    except Exception as exc:  # noqa: BLE001 -- provenance must not fail a run
        try:
            import pydantic
            return {"source": (f"pydantic {pydantic.VERSION} model_json_schema "
                               f"(SDK transform unavailable: {type(exc).__name__})"),
                    "schema": model.model_json_schema()}
        except Exception as exc2:  # noqa: BLE001
            return {"source": f"unavailable: {type(exc2).__name__}: {exc2}",
                    "schema": None}
