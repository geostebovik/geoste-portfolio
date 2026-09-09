
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

def judge_deployment() -> str:
    """Which deployment judges. `JUDGE_DEPLOYMENT` wins; otherwise gpt-5-4.

    ADDED 2026-09-09, together with the change of default recorded below. Every
    result dated BEFORE 2026-09-09 was measured on gpt-5-2 and is not comparable
    to one measured after, which is why `ACTIVE_JUDGE_DEPLOYMENT` exists and why
    probes record it.

    WHY IT EXISTS. Two reasons, one of them a standing backlog item.
    (1) The judge deployment was hardcoded to `CHAT_DEPLOYMENT_GPT_5_2`, a
        variable named after one specific model, carried over from M6 where the
        hardcoded judge is already logged as a defect. Nobody ever chose gpt-5-2
        for M7; it is the Content Understanding analyzer model. Reading a
        purpose-named variable makes the judge a decision rather than an
        inheritance.
    (2) On 2026-09-09 `reasoning_effort` was found to be unreachable through the
        Evaluation SDK -- accepted by `**kwargs` and retained nowhere -- so the
        deployment is the ONLY judge-side variable that can be changed. An
        experiment comparing judges needs a way to switch them that does not
        involve editing this file between runs.

    Probes set it in `os.environ` before importing this module, because
    `build_judge_config()` runs at module scope. Anything importing this after
    the variable is set picks it up; anything importing it before does not.

    THE DEFAULT WAS CHOSEN 2026-09-09, on 60 measured judge calls. It was
    `CHAT_DEPLOYMENT_GPT_5_2` until then -- inherited from M6, never chosen. Six
    probe_judge_isolation runs, two drafts x three deployments x n=10:

      item7 (a draft whose claims are supported but which dodges the topic)
        gpt-5-2       groundedness 1.0 x8, 4.0 x2
        gpt-5-4-mini  groundedness 2.0 x8, 4.0 x2
        gpt-5-4       groundedness 4.0 x10   <- no variance
      item6 (a well-posed draft)
        all three     groundedness 4.0 x10, relevance 3.0 x10   <- identical

    Microsoft documents groundedness as measuring whether claims are SUPPORTED,
    not whether the response ANSWERS. gpt-5-4 applies that definition every
    time; gpt-5-2 usually lets off-topic-ness dominate and collapses to the
    floor. So this is not "newer is better" -- it is fidelity to the metric's
    own contract, and the older deployment failing to implement it.

    THE OBJECTION, AND THE ANSWER TO IT. gpt-5-4 is also what the orchestrator
    drafts on, so the judge now shares a deployment with the drafter. The same
    six runs answer it: `all_passed` was 0/10 on item7 and 10/10 on item6 for
    ALL THREE judges, two of which are not the drafter. Zero crossings in 60
    calls. Self-grading is not buying the drafter a favorable verdict -- that is
    measured, not argued. Re-check it if either model changes.
    """
    load_dotenv()
    return os.environ.get("JUDGE_DEPLOYMENT") or os.environ["CHAT_DEPLOYMENT_GPT_5_4"]


def build_judge_config() -> AzureOpenAIModelConfiguration:
    load_dotenv()

    account, rg, azure_deployment = os.environ["AIF_ACCOUNT"], os.environ["AIF_RESOURCE_GROUP"], judge_deployment()

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
# Recorded at import so a probe or a run record can state which judge produced a
# number without re-deriving it. A result whose judge is unstated is not
# comparable to one from a different judge, and after 2026-09-09 that is a real
# possibility rather than a theoretical one.
ACTIVE_JUDGE_DEPLOYMENT = model_judge["azure_deployment"]
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
    """Evaluate a drafted video title and description for Riverside Hardware & Supply against the store's fact sheet, returning two independent 1-5 scores: groundedness (are the draft's claims supported by the fact sheet) and relevance (does the draft answer the drafting instruction it was given), each with a pass/fail against the SDK's threshold of 3. Call it after drafting and before treating any text as finished. A failing score means the draft should be revised; it never means the fact sheet is wrong.

    NOTE ON THE ONE-LINE DESCRIPTION AND :param: LINES ABOVE. FunctionTool
    truncates every description at the first newline -- verified 2026-09-07 by
    introspecting the generated schema. Before that fix this function reached
    the model as "Evaluate a drafted video title and description for Riverside Hardware &", cut mid-phrase, and its
    parameter guidance was discarded entirely. So the whole description, and
    each :param: description, has to fit on one physical line however it reads
    in source. Everything below this note is for human readers only; the model
    never sees it.

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

    :param query (str): The drafting instruction the text was written to satisfy, phrased as a full request -- use "Draft a video title and description for a piece of content about: '<topic>,' grounded in the store's fact sheet." Never pass a bare topic or title: RelevanceEvaluator grades the response as an answer to this, and a bare title scores as an unanswered question.
    :param response (str): The drafted text to evaluate, title and description together, title first.
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