
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


def evaluate_draft(query: str, response: str) -> dict:
    evaluation_results = {}

    evaluation_results["groundedness"] = evaluators["groundedness"](
        query=query,
        response=response,
        context=context
    )
    evaluation_results["relevance"] = evaluators["relevance"](
        query=query,
        response=response,
    )
    
    return evaluation_results


def main():

    query = "Draft a video title and description for a piece of content about: 'How to Mix Exterior Paint Colors at Home,' grounded in the store's fact sheet."
    title = "How to Mix Exterior Paint Colors at Home — Riverside Hardware & Supply"
    description = (
        "Ever stood in the paint aisle unsure which exterior color will actually hold up "
        "outside? In this quick video we show you how we custom-mix exterior paint right "
        "in store, matched to any swatch or sample you bring in. Stop by Riverside "
        "Hardware & Supply, Monday–Saturday 8am–6pm, and we'll mix it while you shop."
    )
    response = f"Title: {title}\nDescription: {description}"
    results = evaluate_draft(query, response)
    print(results)

if __name__ == "__main__":
    main()