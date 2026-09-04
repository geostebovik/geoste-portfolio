
import json
import math
import os
from dotenv import load_dotenv
from pathlib import Path
from m3_analyze import get_endpoint, get_subscription_key   # reuse, don't rewrite
from azure.ai.evaluation import AzureOpenAIModelConfiguration, GroundednessEvaluator, RelevanceEvaluator


FACT_SHEET_PATH = (
    Path(__file__).parent
    / ".."
    / "iip-docs"
    / "m7-riverside-hardware"
    / "fact-sheet.md"
).resolve()

def build_judge_config() -> AzureOpenAIModelConfiguration:
    load_dotenv()

    account, rg, azure_deployment = os.environ["AIF_ACCOUNT"], os.environ["AIF_RESOURCE_GROUP"], os.environ["CHAT_DEPLOYMENT_GPT_5_2"]

    endpoint = get_endpoint(account, rg)
    key = get_subscription_key(account, rg)

    judge_config = AzureOpenAIModelConfiguration(
        azure_endpoint=endpoint,
        api_key=key,
        azure_deployment=azure_deployment,
        api_version=os.environ["CHAT_API_VERSION"]
    )

    return judge_config


with open(FACT_SHEET_PATH, "r", encoding="utf-8") as f:
    context = f.read()

model_judge = build_judge_config()
evaluators = {
    "groundedness": GroundednessEvaluator(model_judge, is_reasoning_model=True),
    "relevance": RelevanceEvaluator(model_judge, is_reasoning_model=True)
}


def _flatten(metric: str, result: dict) -> dict:
    """Reduce one evaluator's raw output to the fields the orchestrator acts on.

    The SDK returns each metric with its own key prefix plus a `_properties`
    entry carrying the full judge prompt and completion -- for groundedness
    that embeds fact-sheet.md verbatim (~2.3 KB), which the orchestrator
    already holds. Returning that into the agent thread would cost roughly
    3,900 tokens per call (the SDK's own reported prompt_tokens: 2,026 +
    1,848, measured 2026-09-04) to deliver about 1 KB of signal, so it is
    dropped here.

    Score, pass verdict and threshold are the SDK's own values, passed
    through unchanged -- no threshold is invented in this file. `status` is
    carried through so the orchestrator can distinguish a genuine failed
    check from a judge call that did not complete; those should not lead to
    the same next action.

    :param metric (str): Metric name, used as the SDK's key prefix
        (e.g. "groundedness").
    :param result (dict): One evaluator's raw output dict.
    :return: Dict with keys score, passed, threshold, reason, status.
    :rtype: dict
    """
    score = result.get(f"{metric}_score")

    # A judge call that fails can return a non-finite score, and
    # json.dumps(float("nan")) emits a bare NaN token -- not valid JSON.
    # The orchestrator would receive an unparseable tool result, which is a
    # worse failure than a null score it can reason about.
    if isinstance(score, float) and not math.isfinite(score):
        score = None

    return {
        "score": score,
        "passed": result.get(f"{metric}_passed"),
        "threshold": result.get(f"{metric}_threshold"),
        "reason": result.get(f"{metric}_reason"),
        "status": result.get(f"{metric}_status"),
    }


def evaluate_draft(query: str, response: str) -> str:
    """
    Evaluate a drafted video title and description for Riverside Hardware &
    Supply against the store's fact sheet, returning two independent quality
    scores.

    Groundedness asks whether the claims in the draft are supported by the
    fact sheet -- hours, services, contact details, brand voice. Relevance
    asks whether the draft actually answers the drafting instruction it was
    given. Both are judged on a 1-5 scale by the Azure AI Evaluation SDK's
    GroundednessEvaluator and RelevanceEvaluator, each against a pass
    threshold the SDK supplies (3 for both, as of 2026-09-04).

    Call this after drafting text and before treating it as finished. A
    failing score means the draft should be revised; it never means the fact
    sheet is wrong -- the fact sheet is the ground truth both checks are
    measured against.

    Note that `query` is passed to BOTH evaluators (GroundednessEvaluator
    accepts it as an optional parameter), so the drafting instruction's
    wording influences the groundedness reasoning as well as the relevance
    score. Verified behavior, logged 2026-08-27, not a defect.

    :param query (str): The drafting instruction the text was written to
        satisfy, phrased as a request -- e.g. "Draft a video title and
        description for a piece of content about: '<topic>,' grounded in the
        store's fact sheet." Do not pass a bare topic: RelevanceEvaluator
        grades the response as an answer to this, and a bare title scores
        as an unanswered question.
    :param response (str): The drafted text to evaluate, title and
        description together, title first.
    :return: JSON string with one key per metric, "groundedness" and
        "relevance". Each holds score (float, 1-5), passed (bool), threshold
        (int), reason (str, the judge's written explanation of the score),
        and status (str, "completed" when the judge call succeeded). A
        top-level "all_passed" (bool) is true only when both metrics passed.
    :rtype: str
    """
    groundedness = evaluators["groundedness"](
        query=query,
        response=response,
        context=context,
    )
    relevance = evaluators["relevance"](
        query=query,
        response=response,
    )

    results = {
        "groundedness": _flatten("groundedness", groundedness),
        "relevance": _flatten("relevance", relevance),
    }

    # Derived here, not returned by the SDK: the orchestrator's instructions
    # need one unambiguous thing to branch on for "redraft or accept".
    # Remove if it proves redundant once that text is written.
    results["all_passed"] = all(
        results[m]["passed"] is True for m in ("groundedness", "relevance")
    )

    return json.dumps(results)


def main():

    query = "Draft a video title and description for a piece of content about: 'How to Mix Exterior Paint Colors at Home,' grounded in the store's fact sheet."
    title = "How to Mix Exterior Paint Colors at Home — Riverside Hardware & Supply"
    description = (
        "Ever stood in the paint aisle unsure which exterior color will actually hold up "
        "outside? In this quick video we show you how we custom-mix exterior paint right "
        "in store. We walk through the whole process, start to finish. Stop by Riverside "
        "Hardware & Supply, Monday–Saturday 8am–6pm."
    )
    response = f"Title: {title}\nDescription: {description}"
    results = evaluate_draft(query, response)
    print(results)

if __name__ == "__main__":
    main()