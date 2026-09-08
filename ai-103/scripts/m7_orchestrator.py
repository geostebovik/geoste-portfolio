"""
m7_orchestrator.py -- M7's orchestrator agent (Foundry Agent Service).

Wires the two verified tools -- evaluate_draft() (text, m7_evaluator_tool) and
audit_thumbnail() (image, m7_cv_audit_tool) -- to a single Foundry agent that
decides for itself when to call them, per the 2026-08-21 decision recorded in
agent-service-primer.md: agentic orchestration, not a fixed pipeline.

INSTRUCTIONS_V1 IS DELIBERATELY A THROWAWAY. It exists to get a run on the
board, not to be right. It says to call both tools and says NOTHING about what
to do with a failing result -- what the agent does in that gap is the thing
this first run exists to observe. Whether an orchestrator calls the right tool
at the right moment is model behavior, which the project's standing lesson says
to test rather than reason about. The real instructions text gets written
against what this run actually does.

RUN PERSISTENCE (added 2026-09-07, Claude wrote it, Gerard approved the design
before it was written). Every run now writes results/{timestamp}_orchestrator
.json. Before this the script only printed, so the Sep 4 15/15 existed solely as
console output quoted into STATUS.md: not re-readable, not diffable against a
later run, and not usable as the artifact behind the high-RUNS certification
pass still owed before any public "stable" claim.

  WHY THE TOOL CALLS ARE WRAPPED. The obvious way to record what each tool
  returned is to read it off the run steps. It is not there.
  RunStepFunctionToolCallDetails (azure-ai-agents 1.1.0, verified by
  introspection 2026-09-07, not recalled) carries exactly two fields, `name`
  and `arguments` -- no output, despite RunStepFunctionToolCall's own docstring
  claiming it "represents the inputs and output consumed and emitted by the
  specified function". Code-interpreter and file-search calls do carry outputs;
  function calls do not, because enable_auto_function_calls submits the output
  on our behalf and the service never echoes it back. So a logging shim around
  each tool is the only faithful record of what the agent actually saw. The
  agent's own prose is not a substitute -- it paraphrases and smooths tool
  output (Sep 4 observation 4), which is precisely the layer under suspicion.

  THE SHIM MUST NOT MOVE THE TOOL SCHEMA. FunctionTool builds the schema the
  model sees from each function's name, type hints and docstring, so a careless
  wrapper would silently change the agent's inputs and make this run
  non-comparable to Sep 4's. functools.wraps carries all three across; rather
  than trust that, build_toolset() builds the definitions both ways and refuses
  to run if they differ.

SDK SHAPES VERIFIED by introspection against azure-ai-agents 1.1.0 on
2026-09-04, not recalled:
  - FunctionTool and ToolSet live in azure.ai.agents.models.
    agent-service-primer.md shows `from azure.ai.agents.tools import
    FunctionTool` -- that module does not exist. The primer needs correcting.
  - FunctionTool(functions: Set[Callable]) takes a SET, not a list.
  - create_agent() accepts toolset=; runs.create_and_process(thread_id,
    agent_id) is the blocking call that drives auto function calling.
  - enable_auto_function_calls(tools, max_retry=10) -- note the default: a
    misbehaving agent retries up to ten times before giving up.
"""

import functools
import inspect
import json
import os
import subprocess
import time
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from azure.ai.agents import AgentsClient
from azure.ai.agents.models import FunctionTool, ToolSet
from azure.identity import DefaultAzureCredential

from m7_cv_audit_tool import audit_thumbnail
from m7_evaluator_tool import evaluate_draft
from m7_fact_sheet_tool import get_fact_sheet


SCRIPT_DIR = Path(__file__).parent
FIXTURE_DIR = (SCRIPT_DIR / ".." / "iip-docs" / "m7-riverside-hardware").resolve()
RESULTS_DIR = SCRIPT_DIR / "results"

AGENT_NAME = "riverside-content-agent"

# V1 is retained, unused, because every result before 2026-09-07 was measured
# against it -- keeping it here makes a comparison run a one-line change rather
# than a git archaeology exercise. Deliberately minimal; silent on failure
# handling, which is what the Sep 4 and Sep 7 runs existed to observe.
INSTRUCTIONS_V1 = """You draft and check short marketing video content for \
Riverside Hardware & Supply, a small independent hardware store.

For each content item you are given a topic and the file path of a thumbnail \
image. Do all of the following, in order:

1. Draft a video title and a description for the topic.
2. Call evaluate_draft to check the drafted text.
3. Call audit_thumbnail to check the thumbnail image.
4. Report the drafted title and description, then the result of each check.

Always call both tools. Do not skip a check because the draft looks correct \
to you."""

# V2 written 2026-09-07. Gerard owns this wording; Claude drafted it against the
# Sep 4 and Sep 7 runs and Gerard edited and approved it. Rationale for each
# clause is in ../m7-instructions-draft.md.
INSTRUCTIONS_V2 = """You draft and check short marketing video content for \
Riverside Hardware & Supply, a small independent hardware store.

For each content item you are given a topic and the file path of a thumbnail \
image.

DRAFT
1. Write a title in this format, with an em dash:
     <benefit or topic, plain language> — Riverside Hardware & Supply
   Spell the store name in full. Do not abbreviate it, drop it, or use a
   different separator.
2. Write a description in three parts, in this order:
     Hook — one sentence stating the problem or question the video answers.
     Body — two or three sentences on what is covered.
     CTA — one line giving the store name and its hours, or the store name and
       the phone number. Take these from the fact sheet exactly; never invent
       or approximate them.
3. Every factual claim you make — hours, services, pricing, availability — must
   be traceable to the fact sheet. If the fact sheet does not support a claim,
   leave the claim out rather than softening it.

CHECK THE TEXT
4. Call evaluate_draft. Pass the topic you were given, verbatim and with
   nothing added, as `query`. Pass your full title and description as
   `response`.
5. Decide on the `all_passed` field alone. Do not decide from the `reason`
   text — it is unreliable, and has contradicted itself inside a single
   paragraph.
6. If `all_passed` is false, redraft and check again — at most twice. Each
   time, remove or replace whatever the draft asserts that the fact sheet does
   not support, and do not add more detail to compensate. Call evaluate_draft
   on each new draft under the same rules. Stop as soon as `all_passed` is
   true. If the third draft still fails, keep it and report every result.

CHECK THE THUMBNAIL
7. Call audit_thumbnail on the image path you were given.
8. You cannot change the image. Never attempt to, and never suggest a specific
   redesign. If any of its three checks is false, the item is flagged.

REPORT — always, and in this order
9.  The final title and description.
10. The text check: each score, whether it passed, and the overall result. If
    you redrafted, say how many times and give all results.
11. The thumbnail check: the three checks and their results. Quote any figures
    or text the tool returned exactly as it returned them — including contrast
    ratios, and including text read out of the image even where it looks
    garbled. Garbled text is evidence, not an error to tidy up.
12. A final line that is exactly one of:
      READY
      FLAGGED FOR REVIEW: <the failing checks, comma separated>

Do not offer improvement suggestions on a check that passed."""

# V3 written 2026-09-07, after V2 regressed to 12/15. Two bugs, both Claude's,
# both fixed here: (1) the agent was told to ground its drafting in a fact sheet
# it had never been given -- get_fact_sheet() now supplies it, and the redraft
# clause substitutes instead of only subtracting (Gerard's fix); (2) clause 4
# told the agent to pass a bare topic as `query`, which directly contradicts
# evaluate_draft's own docstring -- "Do not pass a bare topic: RelevanceEvaluator
# grades the response as an answer to this, and a bare title scores as an
# unanswered question." Relevance duly fell from 4.0 to 2.0. Clause 4 now uses
# the phrasing that docstring specifies, which fixes the contradiction and still
# removes the run-to-run variance the bare-topic rule was written to close.
INSTRUCTIONS_V3 = """You draft and check short marketing video content for \
Riverside Hardware & Supply, a small independent hardware store.

For each content item you are given a topic and the file path of a thumbnail \
image.

GET THE FACTS FIRST
1. Call get_fact_sheet before writing anything. It returns the store's hours,
   services, contact details and brand guide, and it is the only approved
   source of facts about the store. Everything below depends on having it.

DRAFT
2. Write a title in this format, with an em dash:
     <benefit or topic, plain language> — Riverside Hardware & Supply
   Spell the store name in full. Do not abbreviate it, drop it, or use a
   different separator.
3. Write a description in three parts, in this order. Write it as flowing
   copy — do not label the parts or print the words Hook, Body or CTA.
     A hook: one sentence stating the problem or question the video answers.
     A body: two or three sentences on what is covered, using the concrete
       services and details the fact sheet gives you.
     A closing line: the store name with its hours, or the store name with the
       phone number, copied from the fact sheet exactly.
4. Every factual claim — hours, services, pricing, availability — must be
   traceable to the fact sheet. If the fact sheet does not support a claim,
   leave it out. Do not compensate by writing vaguely: a description with no
   specifics in it fails for being uninformative, so use the specifics the
   fact sheet does give you.

CHECK THE TEXT
5. Call evaluate_draft. Pass your full title and description as `response`.
   For `query`, use exactly this sentence with the topic filled in:
     Draft a video title and description for a piece of content about:
     '<topic>,' grounded in the store's fact sheet.
6. Decide on the `all_passed` field alone. Do not decide from the `reason`
   text — it is unreliable, and has contradicted itself inside a single
   paragraph.
7. If `all_passed` is false, redraft and check again — at most twice. Each
   time, remove unsupported claims and replace them with supported ones from
   the fact sheet. Call evaluate_draft on each new draft under the same rules.
   Stop as soon as `all_passed` is true. If the third draft still fails, keep
   it and report every result.

CHECK THE THUMBNAIL
8. Call audit_thumbnail on the image path you were given.
9. You cannot change the image. Never attempt to, and never suggest a specific
   redesign. If any of its three checks is false, the item is flagged.

REPORT — always, and in this order
10. The final title and description.
11. The text check: each score, whether it passed, and the overall result. If
    you redrafted, say how many times and give all results.
12. The thumbnail check: the three checks and their results. Quote any figures
    or text the tool returned exactly as it returned them — including contrast
    ratios, and including text read out of the image even where it looks
    garbled. Garbled text is evidence, not an error to tidy up.
13. A final line that is exactly one of:
      READY
      FLAGGED FOR REVIEW: <the failing checks, comma separated>

Do not offer improvement suggestions on a check that passed."""

ACTIVE_INSTRUCTIONS_LABEL = "INSTRUCTIONS_V3"
ACTIVE_INSTRUCTIONS = INSTRUCTIONS_V3

# Pinned 2026-09-07. NOTE: the Agents SDK exposes temperature and top_p but has
# no `seed` parameter at all -- verified by introspection against
# azure-ai-agents 1.1.0, and unlike the chat-completions path the CV audit uses,
# where seed=42 is pinned. So this narrows drafting variance; it does not make a
# run repeatable. Comparing two runs still needs the multi-run probe.
AGENT_TEMPERATURE = 0.0

# The items from content-items-plan.md. `expected_audit` is that document's
# expected-results table, carried here so a run is read against the rubric
# rather than by eye. Items 1-5 are the CV-audit set: two clean controls, three
# single planted flaws, and they define the 5x3 = 15-cell matrix every prior run
# is reported against.
#
# Items 6 and 7 were added 2026-09-08 and are a different category: the flaw is
# in the TOPIC, for evaluate_draft to catch, not in the thumbnail. They exist
# because INSTRUCTIONS_V3's remediation clauses (the two-redraft cap, "replace
# unsupported claims with supported ones", stop-on-pass) have zero observations
# -- both V3 runs passed every item on the first draft. `text_path: True` keeps
# their audit cells out of the 15-cell matrix so that figure stays comparable
# across runs; both totals are printed and persisted.
#
# `expected_text` is pre-registered, before the run, per content-items-plan.md.
# expected_redrafts is None where more than one count is correct -- item6 may
# recover on the first or the second redraft, and both are the clause working.
ITEMS = [
    {
        "id": "item1",
        "topic": "How to Mix Exterior Paint Colors at Home",
        "thumbnail": "item1-paint-mixing-CLEAN.png",
        "expected_audit": {"text_legible": True, "brand_consistent": True, "info_accurate": True},
        "expected_text": {"first_pass": True, "final_passed": True, "expected_redrafts": 0},
    },
    {
        "id": "item2",
        "topic": "Seasonal Maintenance Checklist for Homeowners",
        "thumbnail": "item2-seasonal-checklist-CLEAN.png",
        "expected_audit": {"text_legible": True, "brand_consistent": True, "info_accurate": True},
        "expected_text": {"first_pass": True, "final_passed": True, "expected_redrafts": 0},
    },
    {
        "id": "item3",
        "topic": "Tool Rental 101: What We Offer",
        "thumbnail": "item3-tool-rental-FLAW-legibility.png",
        "expected_audit": {"text_legible": False, "brand_consistent": True, "info_accurate": True},
        "expected_text": {"first_pass": True, "final_passed": True, "expected_redrafts": 0},
    },
    {
        "id": "item4",
        "topic": "Key Cutting While You Wait",
        "thumbnail": "item4-key-cutting-FLAW-brand.png",
        "expected_audit": {"text_legible": True, "brand_consistent": False, "info_accurate": True},
        "expected_text": {"first_pass": True, "final_passed": True, "expected_redrafts": 0},
    },
    {
        "id": "item5",
        "topic": "Propane Tank Refill Safety Tips",
        "thumbnail": "item5-propane-refill-FLAW-info-accuracy.png",
        "expected_audit": {"text_legible": True, "brand_consistent": True, "info_accurate": False},
        "expected_text": {"first_pass": True, "final_passed": True, "expected_redrafts": 0},
    },
    {
        # Recoverable text failure. The spine is supported -- the fact sheet
        # lists tool rental with daily and weekly rates -- but it carries no
        # prices at all, and "Rates Explained" demands numbers. The redraft has
        # somewhere real to go (rate structure, phone number, hours), which is
        # what puts "replace unsupported claims with supported ones" under test
        # rather than plain deletion. Pre-registered alternative: the agent may
        # decline to invent prices and pass on the first draft. That is a
        # finding -- the instructions outrunning the fixture -- not a defect.
        "id": "item6",
        "topic": "Tool Rental Pricing: Daily and Weekly Rates Explained",
        "thumbnail": "item1-paint-mixing-CLEAN.png",
        "text_path": True,
        "expected_audit": {"text_legible": True, "brand_consistent": True, "info_accurate": True},
        "expected_text": {"first_pass": False, "final_passed": True, "expected_redrafts": None},
    },
    {
        # Unrecoverable text failure. fact-sheet.md's own "Out of scope"
        # section declares this absent -- "No employee names, no ownership
        # history" -- so there is no judgment call about supportability. No
        # substitution exists, so all three drafts should fail and the cap
        # should fire. Pre-registered alternative: the agent may refuse to
        # draft and name the missing facts, as item3 did under INSTRUCTIONS_V2
        # on 2026-09-07. Correct behavior, different result -- it leaves the
        # cap still unobserved.
        "id": "item7",
        "topic": "Meet the Riverside Crew: The People Behind the Counter",
        "thumbnail": "item1-paint-mixing-CLEAN.png",
        "text_path": True,
        "expected_audit": {"text_legible": True, "brand_consistent": True, "info_accurate": True},
        "expected_text": {"first_pass": False, "final_passed": False, "expected_redrafts": 2},
    },
]


# ---------------------------------------------------------------------------
# Run provenance
# ---------------------------------------------------------------------------

def _git(*args: str) -> str:
    """Read-only git from the script's directory; empty string on any failure.

    Provenance is worth recording and never worth failing a run over, so every
    error path here returns "" rather than raising. --no-optional-locks matches
    the standing rule for reading git out of a non-interactive shell.
    """
    try:
        done = subprocess.run(
            ["git", "--no-optional-locks", *args],
            cwd=SCRIPT_DIR,
            capture_output=True,
            text=True,
            timeout=15,
            env={**os.environ, "GIT_OPTIONAL_LOCKS": "0"},
        )
        return done.stdout.strip() if done.returncode == 0 else ""
    except Exception:
        return ""


def run_provenance() -> dict:
    """What this run was measured against.

    `git_dirty` is the field that earns this function. A number measured against
    an undocumented working-tree diff is not attributable to any commit and
    cannot be re-derived later -- the failure that poisoned the 2026-08-31 data
    point. `instructions` is stored verbatim because item 4 of
    m7-orientation.md's build list iterates exactly that string, and every
    future run has to be readable against the wording it actually ran under.
    """
    status = _git("status", "--porcelain")
    return {
        "timestamp": datetime.now().astimezone().isoformat(timespec="seconds"),
        "script": Path(__file__).name,
        "git_head": _git("rev-parse", "HEAD"),
        "git_branch": _git("rev-parse", "--abbrev-ref", "HEAD"),
        "git_dirty": bool(status),
        "git_dirty_files": status.splitlines(),
        "model_deployment": os.environ.get("CHAT_DEPLOYMENT_GPT_5_4", ""),
        "agent_name": AGENT_NAME,
        "temperature": AGENT_TEMPERATURE,
        "instructions_label": ACTIVE_INSTRUCTIONS_LABEL,
        "instructions": ACTIVE_INSTRUCTIONS,
    }


# ---------------------------------------------------------------------------
# Tool call capture
# ---------------------------------------------------------------------------

TOOL_CALLS: list[dict] = []


def logged(fn):
    """Wrap `fn` so each call records its named arguments, return value and duration.

    A redraft is detectable here and almost nowhere else: it is a second
    evaluate_draft call whose `response` argument differs from the first. The
    agent's prose may or may not mention that it redrafted; the argument list
    cannot be vague about it.
    """
    signature = inspect.signature(fn)

    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        record: dict = {"tool": fn.__name__}
        try:
            bound = signature.bind(*args, **kwargs)
            bound.apply_defaults()
            record["arguments"] = dict(bound.arguments)
        except TypeError as exc:
            record["arguments"] = {"_bind_error": str(exc)}
        started = time.perf_counter()
        try:
            output = fn(*args, **kwargs)
        except Exception as exc:
            record["error"] = f"{type(exc).__name__}: {exc}"
            raise
        else:
            record["output"] = output
            return output
        finally:
            record["seconds"] = round(time.perf_counter() - started, 2)
            TOOL_CALLS.append(record)

    return wrapper


def _definitions(tool: FunctionTool) -> list[dict]:
    """Serialized tool definitions, name-sorted.

    FunctionTool takes a set, so definition order is not stable between two
    constructions and cannot be compared as-is.
    """
    return sorted(
        (d.as_dict() for d in tool.definitions),
        key=lambda d: d["function"]["name"],
    )


def build_client() -> AgentsClient:
    """Build the project-scoped AgentsClient.

    Note this is the PROJECT endpoint (aif-dev-wus-01/proj-iip-dev-wus-01),
    not the account endpoint the openai-package clients in M2-M6 use, and it
    authenticates with DefaultAzureCredential rather than an account key.
    """
    return AgentsClient(
        endpoint=os.environ["AIF_PROJECT_ENDPOINT"],
        credential=DefaultAzureCredential(),
    )


def build_toolset() -> ToolSet:
    """Register both M7 tools, wrapped so their inputs and outputs are recorded.

    FunctionTool reads each function's name, type hints and docstring to build
    the schema the model actually sees -- the Python source is never shown to
    it. The equality check below is what makes the wrapping safe: if wrapping
    ever changes that schema, the run stops rather than producing a result that
    looks comparable to earlier ones and is not.
    """
    raw = FunctionTool({evaluate_draft, audit_thumbnail, get_fact_sheet})
    wrapped = FunctionTool({logged(evaluate_draft), logged(audit_thumbnail),
                            logged(get_fact_sheet)})
    if _definitions(raw) != _definitions(wrapped):
        raise RuntimeError(
            "The logging wrapper changed the tool schema the model sees. "
            "Refusing to run: this result would not be comparable to earlier runs."
        )
    toolset = ToolSet()
    toolset.add(wrapped)
    return toolset


# ---------------------------------------------------------------------------
# Per-item capture
# ---------------------------------------------------------------------------

def collect_steps(client, thread_id: str, run_id: str) -> list[dict]:
    """What the agent asked for, in execution order: tool name and arguments.

    The returned payload is deliberately not here -- the SDK does not expose it
    on a function tool call (see the module docstring); it comes from the
    logging shim instead. Keeping both sides is deliberate: a disagreement
    between what the agent requested and what the shim received would itself be
    a finding.
    """
    steps = []
    for step in client.run_steps.list(thread_id=thread_id, run_id=run_id, order="asc"):
        details = getattr(step, "step_details", None)
        for call in getattr(details, "tool_calls", None) or []:
            fn = getattr(call, "function", None)
            steps.append({
                "name": getattr(fn, "name", None) or getattr(call, "type", "?"),
                "arguments": getattr(fn, "arguments", None),
            })
    return steps


def collect_messages(client, thread_id: str) -> list[dict]:
    """Every message on the thread, oldest first.

    The previous version printed the newest assistant message and stopped. A
    redraft -- the behavior the instructions text most needs to be written
    against -- produces intermediate assistant messages, and those were being
    thrown away.
    """
    out = []
    for msg in client.messages.list(thread_id=thread_id, order="asc"):
        texts = [t.text.value for t in (msg.text_messages or [])]
        out.append({"role": str(msg.role), "text": "\n".join(texts)})
    return out


def actual_audit(calls: list[dict]) -> dict | None:
    """The audit booleans as the TOOL returned them, not as the agent described them.

    audit_thumbnail returns a JSON string, so the comparison against
    content-items-plan.md's expected-results table can be exact instead of read
    out of the agent's prose summary -- which paraphrases, and is the layer the
    Sep 4 run flagged as smoothing tool output.
    """
    for call in reversed(calls):
        if call.get("tool") == "audit_thumbnail" and "output" in call:
            try:
                data = json.loads(call["output"])
            except (TypeError, ValueError):
                return None
            return {k: data.get(k) for k in ("text_legible", "brand_consistent", "info_accurate")}
    return None


def run_item(client, agent_id: str, item: dict) -> dict:
    """Run one content item on its own thread; print live, return the full record.

    One thread per item is deliberate: a shared thread would leave the previous
    item's draft and tool results sitting in context while the next is drafted,
    which is the same cross-contamination the CV audit was split in two to
    remove on 2026-09-02.
    """
    thumbnail = FIXTURE_DIR / item["thumbnail"]
    print(f"\n{'=' * 70}\n{item['id']} -- {item['topic']}\n{'=' * 70}")

    TOOL_CALLS.clear()

    thread = client.threads.create()
    client.messages.create(
        thread_id=thread.id,
        role="user",
        content=f"Topic: {item['topic']}\nThumbnail image path: {thumbnail}",
    )
    run = client.runs.create_and_process(thread_id=thread.id, agent_id=agent_id)

    calls = list(TOOL_CALLS)
    actual = actual_audit(calls)
    usage = getattr(run, "usage", None)

    # How many times the agent checked the text. The cap in INSTRUCTIONS_V2 was
    # set at two redrafts on judgement, not evidence; recording this is what
    # lets a later multi-run pass replace that judgement with a number.
    draft_checks = [c for c in calls if c.get("tool") == "evaluate_draft"]
    redrafts = max(0, len(draft_checks) - 1)

    def _all_passed(call: dict | None):
        """all_passed out of one evaluate_draft call, or None if unreadable."""
        if not call or "output" not in call:
            return None
        try:
            return json.loads(call["output"]).get("all_passed")
        except (TypeError, ValueError):
            return None

    # Both ends of the chain, added 2026-09-08. The last call alone cannot
    # distinguish "passed on the first draft" from "failed then recovered",
    # which is the entire distinction items 6 and 7 were added to observe.
    first_text_passed = _all_passed(draft_checks[0] if draft_checks else None)
    final_text_passed = _all_passed(draft_checks[-1] if draft_checks else None)

    expected_text = item.get("expected_text") or {}
    text_matches_expected = None
    if expected_text and draft_checks:
        expected_redrafts = expected_text.get("expected_redrafts")
        text_matches_expected = (
            first_text_passed == expected_text.get("first_pass")
            and final_text_passed == expected_text.get("final_passed")
            and (expected_redrafts is None or redrafts == expected_redrafts)
        )

    record = {
        "id": item["id"],
        "topic": item["topic"],
        "thumbnail": item["thumbnail"],
        "thread_id": thread.id,
        "run_id": run.id,
        "run_status": str(run.status),
        "last_error": str(run.last_error) if getattr(run, "last_error", None) else None,
        "text_path": bool(item.get("text_path")),
        "evaluate_draft_calls": len(draft_checks),
        "redrafts": redrafts,
        "first_text_passed": first_text_passed,
        "final_text_passed": final_text_passed,
        "expected_text": expected_text or None,
        "text_matches_expected": text_matches_expected,
        "expected_audit": item["expected_audit"],
        "actual_audit": actual,
        "audit_matches_expected": (actual == item["expected_audit"]) if actual else None,
        "requested_tool_calls": collect_steps(client, thread.id, run.id),
        "tool_calls": calls,
        "messages": collect_messages(client, thread.id),
        "usage": {
            "prompt_tokens": getattr(usage, "prompt_tokens", None),
            "completion_tokens": getattr(usage, "completion_tokens", None),
            "total_tokens": getattr(usage, "total_tokens", None),
        } if usage else None,
    }

    print(f"run status: {record['run_status']}")
    if record["last_error"]:
        print(f"run error:  {record['last_error']}")
    names = [s["name"] for s in record["requested_tool_calls"]]
    print(f"tools called ({len(names)}): {names or 'NONE'}")
    print(f"text check: first={first_text_passed} final={final_text_passed}  "
          f"evaluate_draft calls={len(draft_checks)} (redrafts={redrafts})")
    if expected_text:
        print(f"expected text (content-items-plan.md): "
              f"first={expected_text.get('first_pass')} "
              f"final={expected_text.get('final_passed')} "
              f"redrafts={expected_text.get('expected_redrafts')}"
              f"   match={text_matches_expected}")
    print(f"expected audit (content-items-plan.md): {json.dumps(item['expected_audit'])}")
    print(f"actual audit (from tool output):        {json.dumps(actual)}"
          f"   match={record['audit_matches_expected']}")

    tail = [m for m in record["messages"] if "user" not in m["role"].lower()]
    if tail:
        print(f"\n--- agent output ---\n{tail[-1]['text']}")
    return record


# ---------------------------------------------------------------------------
# Results
# ---------------------------------------------------------------------------

def cells_correct(records: list[dict], matrix_only: bool = False) -> tuple[int, int]:
    """Correct audit cells, counted against content-items-plan.md's answer key.

    `matrix_only` restricts the count to items 1-5 -- the 5x3 = 15-cell matrix
    every run before 2026-09-08 was reported against. Items 6 and 7 carry audit
    cells too (they reuse item1's clean thumbnail), but folding them in would
    silently change the headline from 15 to 21 and make no prior run comparable
    without arithmetic. Both totals are printed and persisted; which one becomes
    the headline is a decision to make against a real run, not in advance.
    """
    correct = total = 0
    for record in records:
        if matrix_only and record.get("text_path"):
            continue
        actual = record.get("actual_audit") or {}
        for key, expected in record["expected_audit"].items():
            total += 1
            if actual.get(key) == expected:
                correct += 1
    return correct, total


def write_results(provenance: dict, records: list[dict]) -> Path:
    """Write the run to results/{timestamp}_orchestrator.json.

    Naming follows probe_fixture_stability.py's convention so orchestrator runs
    sort alongside the fixture-stability runs they will be read against.
    """
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    correct, total = cells_correct(records)
    m_correct, m_total = cells_correct(records, matrix_only=True)
    path = RESULTS_DIR / f"{datetime.now().strftime('%Y%m%d-%H%M%S')}_orchestrator.json"
    payload = {
        "run": provenance,
        "summary": {
            "items_run": len(records),
            "items_matching_expected": sum(1 for r in records if r.get("audit_matches_expected")),
            "cells_correct": correct,
            "cells_total": total,
            "matrix_cells_correct": m_correct,
            "matrix_cells_total": m_total,
            "text_path_items_matching_expected": sum(
                1 for r in records if r.get("text_path") and r.get("text_matches_expected")
            ),
            "text_path_items": sum(1 for r in records if r.get("text_path")),
            "tool_calls": sum(len(r.get("tool_calls") or []) for r in records),
            "items_with_redrafts": sum(1 for r in records if r.get("redrafts")),
            "redrafts_total": sum(r.get("redrafts") or 0 for r in records),
            "items_text_passing": sum(1 for r in records if r.get("final_text_passed")),
        },
        "items": records,
    }
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return path


def main():
    load_dotenv()
    provenance = run_provenance()
    if provenance["git_dirty"]:
        print("WARNING: working tree is dirty. This result is not attributable to a "
              "commit and cannot be re-derived later.")
        for line in provenance["git_dirty_files"]:
            print(f"  {line}")

    client = build_client()
    toolset = build_toolset()
    client.enable_auto_function_calls(toolset)

    records: list[dict] = []
    try:
        agent = client.create_agent(
            model=os.environ["CHAT_DEPLOYMENT_GPT_5_4"],
            name=AGENT_NAME,
            instructions=ACTIVE_INSTRUCTIONS,
            toolset=toolset,
            temperature=AGENT_TEMPERATURE,
        )
        print(f"agent created: {agent.id} ({AGENT_NAME}), "
              f"model={os.environ['CHAT_DEPLOYMENT_GPT_5_4']}, "
              f"instructions={ACTIVE_INSTRUCTIONS_LABEL}, temperature={AGENT_TEMPERATURE}")
        try:
            for item in ITEMS:
                records.append(run_item(client, agent.id, item))
        finally:
            # Agents persist in the project until deleted. Cleaning up keeps
            # repeat runs from leaving a pile of near-identical agents behind.
            client.delete_agent(agent.id)
            print(f"\nagent deleted: {agent.id}")
    finally:
        # Written even on a crash: a partial run is still evidence, and losing
        # it is the exact failure this file was changed to stop.
        path = write_results(provenance, records)
        correct, total = cells_correct(records)
        m_correct, m_total = cells_correct(records, matrix_only=True)
        print(f"\n{m_correct}/{m_total} audit cells match content-items-plan.md "
              f"(items 1-5, the matrix prior runs are reported against)")
        if total != m_total:
            print(f"{correct}/{total} audit cells including the text-path items")
        text_items = [r for r in records if r.get("text_path")]
        for record in text_items:
            print(f"  {record['id']}: first={record.get('first_text_passed')} "
                  f"final={record.get('final_text_passed')} "
                  f"redrafts={record.get('redrafts')} "
                  f"-> matches expected: {record.get('text_matches_expected')}")
        print(f"results written: {path}")


if __name__ == "__main__":
    main()
