
from datetime import datetime
from dotenv import load_dotenv
import os
from m3_analyze import get_endpoint, get_subscription_key   # reuse, don't rewrite
from azure.ai.evaluation import evaluate, AzureOpenAIModelConfiguration, GroundednessEvaluator, RelevanceEvaluator, SimilarityEvaluator, F1ScoreEvaluator

# load .env
# build judge
def model_config():

    load_dotenv()
    account, rg = os.environ["AIF_ACCOUNT"], os.environ["AIF_RESOURCE_GROUP"]

    endpoint = get_endpoint(account, rg)
    key = get_subscription_key(account, rg)
    
    judge = AzureOpenAIModelConfiguration(
        azure_endpoint=endpoint,
        api_key=key,
        api_version=os.environ["CHAT_API_VERSION"],   # "2024-06-01"
        azure_deployment="gpt-5-2",  # this is the judge model deployment name
    )
    return judge

# define evaluators dict
model_judge = model_config()
evaluators = {
    "groundedness": GroundednessEvaluator(model_judge, is_reasoning_model=True),
    "relevance": RelevanceEvaluator(model_judge, is_reasoning_model=True),
    "similarity": SimilarityEvaluator(model_judge, is_reasoning_model=True),
    "f1score": F1ScoreEvaluator()
}
# evaluate now
timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
evaluate(
    data="data.jsonl",
    evaluators=evaluators,
    output_path=f"results/{timestamp}_eval_results.json",
    fail_on_evaluator_errors=True # is this where this line goes?
)
