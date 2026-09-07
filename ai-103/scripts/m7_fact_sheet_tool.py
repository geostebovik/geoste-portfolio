"""
m7_fact_sheet_tool.py -- exposes fact-sheet.md to the orchestrator agent.

WHY THIS EXISTS. Until 2026-09-07 the orchestrator was instructed to ground
every claim in `fact-sheet.md`, and to take the store's hours or phone number
from it, without ever being given the document. The fact sheet reached the
JUDGE (m7_evaluator_tool reads it at import and passes it as `context`) and the
CV audit (m7_cv_audit_tool builds it into the content call), but never the
drafter. An open-book exam where only the grader has the book.

Run `20260907-131248_orchestrator.json` is what that produced, under
INSTRUCTIONS_V2: the agent stripped every specific it could not verify until
the copy said nothing at all ("This video focuses on the topic of exterior
paint color mixing at home"), groundedness sat at 2.0, relevance fell from
V1's 4.0 to 2.0 as the drafts emptied out, and item3 declined to act -- naming
the missing fact sheet as the reason, which was the correct diagnosis.

V2's redraft clause made it worse by design: "remove unsupported claims and do
not add detail to compensate" can only subtract when there is no source to add
from. Four of five items burned the full redraft cap; item1 never passed.

DELIVERED AS A TOOL, not inlined into the instructions text -- Gerard's call,
on his standing preference for the tool-shaped option. Tool calling is
AI-103's largest-weighted domain, and fetching grounding data on demand is
closer to a real system than pasting it into a system prompt.

The whole file is returned verbatim, deliberately. The judge grades against
the whole file; handing the drafter a curated subset would reintroduce the
same drafter/grader mismatch this module exists to remove, just smaller.
"""

from pathlib import Path

FACT_SHEET_PATH = (
    Path(__file__).parent / ".." / "iip-docs" / "m7-riverside-hardware" / "fact-sheet.md"
).resolve()


def get_fact_sheet() -> str:
    """Retrieve the Riverside Hardware & Supply fact sheet: the store's hours, services, contact details, tagline and brand guide. This is the only approved source of facts about the store and the same document the draft evaluator and thumbnail audit are measured against, so call it before drafting anything and never invent hours, prices or contact details.

    NOTE ON THE ONE-LINE DESCRIPTION ABOVE. FunctionTool truncates every
    description at the first newline -- verified 2026-09-07 by introspecting
    the generated schema, after `evaluate_draft` was found to reach the model
    as "Evaluate a drafted video title and description for Riverside Hardware
    &", cut mid-phrase, with its `query` guidance discarded entirely. So the
    whole description has to live on line one, however it reads in source.
    Anything below this point is for human readers only; the model never sees
    it.

    :return: The full text of the fact sheet, verbatim.
    :rtype: str
    """
    return FACT_SHEET_PATH.read_text(encoding="utf-8")


if __name__ == "__main__":
    text = get_fact_sheet()
    print(f"{FACT_SHEET_PATH}\n{len(text)} chars\n{'-' * 60}\n{text}")
