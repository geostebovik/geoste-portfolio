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

import json
import os
from pathlib import Path

from dotenv import load_dotenv
from azure.ai.agents import AgentsClient
from azure.ai.agents.models import FunctionTool, ToolSet
from azure.identity import DefaultAzureCredential

from m7_cv_audit_tool import audit_thumbnail
from m7_evaluator_tool import evaluate_draft


FIXTURE_DIR = (
    Path(__file__).parent / ".." / "iip-docs" / "m7-riverside-hardware"
).resolve()

AGENT_NAME = "riverside-content-agent"

# Deliberately minimal. Silent on failure handling -- see the module docstring.
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

# The five items from content-items-plan.md. `expected_audit` is that document's
# expected-results table, carried here so a run is read against the rubric
# rather than by eye. Two clean controls, three single planted flaws.
ITEMS = [
    {
        "id": "item1",
        "topic": "How to Mix Exterior Paint Colors at Home",
        "thumbnail": "item1-paint-mixing-CLEAN.png",
        "expected_audit": {"text_legible": True, "brand_consistent": True, "info_accurate": True},
    },
    {
        "id": "item2",
        "topic": "Seasonal Maintenance Checklist for Homeowners",
        "thumbnail": "item2-seasonal-checklist-CLEAN.png",
        "expected_audit": {"text_legible": True, "brand_consistent": True, "info_accurate": True},
    },
    {
        "id": "item3",
        "topic": "Tool Rental 101: What We Offer",
        "thumbnail": "item3-tool-rental-FLAW-legibility.png",
        "expected_audit": {"text_legible": False, "brand_consistent": True, "info_accurate": True},
    },
    {
        "id": "item4",
        "topic": "Key Cutting While You Wait",
        "thumbnail": "item4-key-cutting-FLAW-brand.png",
        "expected_audit": {"text_legible": True, "brand_consistent": False, "info_accurate": True},
    },
    {
        "id": "item5",
        "topic": "Propane Tank Refill Safety Tips",
        "thumbnail": "item5-propane-refill-FLAW-info-accuracy.png",
        "expected_audit": {"text_legible": True, "brand_consistent": True, "info_accurate": False},
    },
]


def build_client() -> AgentsClient:
    """Build the project-scoped AgentsClient.

    Note this is the PROJECT endpoint (aif-dev-wus-01/proj-iip-dev-wus-01),
    not the account endpoint the openai-package clients in M2-M6 use, and it
    authenticates with DefaultAzureCredential rather than an account key.
    """
    load_dotenv()
    return AgentsClient(
        endpoint=os.environ["AIF_PROJECT_ENDPOINT"],
        credential=DefaultAzureCredential(),
    )


def build_toolset() -> ToolSet:
    """Register both M7 tools. FunctionTool reads each function's name, type
    hints and docstring to build the schema the model actually sees -- the
    Python source is never shown to it.
    """
    toolset = ToolSet()
    toolset.add(FunctionTool({evaluate_draft, audit_thumbnail}))
    return toolset


def summarize_tool_calls(client, thread_id: str, run_id: str) -> list[str]:
    """Names of the tools the agent actually called, in execution order.

    This is the primary observation of the first run: not whether the output
    reads well, but whether the agent picked the tools up at all.
    """
    called = []
    for step in client.run_steps.list(thread_id=thread_id, run_id=run_id, order="asc"):
        details = getattr(step, "step_details", None)
        for call in getattr(details, "tool_calls", None) or []:
            fn = getattr(call, "function", None)
            called.append(getattr(fn, "name", None) or getattr(call, "type", "?"))
    return called


def run_item(client, agent_id: str, item: dict) -> None:
    """Run one content item on its own thread, then print what happened.

    One thread per item is deliberate: a shared thread would leave the previous
    item's draft and tool results sitting in context while the next is drafted,
    which is the same cross-contamination the CV audit was split in two to
    remove on 2026-09-02.
    """
    thumbnail = FIXTURE_DIR / item["thumbnail"]
    print(f"\n{'=' * 70}\n{item['id']} -- {item['topic']}\n{'=' * 70}")

    thread = client.threads.create()
    client.messages.create(
        thread_id=thread.id,
        role="user",
        content=f"Topic: {item['topic']}\nThumbnail image path: {thumbnail}",
    )
    run = client.runs.create_and_process(thread_id=thread.id, agent_id=agent_id)

    print(f"run status: {run.status}")
    if run.status == "failed":
        print(f"run error:  {run.last_error}")

    called = summarize_tool_calls(client, thread.id, run.id)
    print(f"tools called ({len(called)}): {called or 'NONE'}")
    print(f"expected audit (content-items-plan.md): {json.dumps(item['expected_audit'])}")

    for msg in client.messages.list(thread_id=thread.id, order="desc"):
        if msg.role == "assistant" and msg.text_messages:
            print(f"\n--- agent output ---\n{msg.text_messages[-1].text.value}")
            break


def main():
    client = build_client()
    toolset = build_toolset()
    client.enable_auto_function_calls(toolset)

    agent = client.create_agent(
        model=os.environ["CHAT_DEPLOYMENT_GPT_5_4"],
        name=AGENT_NAME,
        instructions=INSTRUCTIONS_V1,
        toolset=toolset,
    )
    print(f"agent created: {agent.id} ({AGENT_NAME}), model={os.environ['CHAT_DEPLOYMENT_GPT_5_4']}")

    try:
        for item in ITEMS:
            run_item(client, agent.id, item)
    finally:
        # Agents persist in the project until deleted. Cleaning up keeps repeat
        # runs from leaving a pile of near-identical agents behind.
        client.delete_agent(agent.id)
        print(f"\nagent deleted: {agent.id}")


if __name__ == "__main__":
    main()
