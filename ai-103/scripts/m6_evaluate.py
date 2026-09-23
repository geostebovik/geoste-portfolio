
from datetime import datetime
from dotenv import load_dotenv
import os
from m3_analyze import get_endpoint   # reuse, don't rewrite
from azure.ai.evaluation import evaluate, AzureOpenAIModelConfiguration, GroundednessEvaluator, RelevanceEvaluator, SimilarityEvaluator, F1ScoreEvaluator

# load .env
# build judge
def model_config():

    load_dotenv()
    account, rg = os.environ["AIF_ACCOUNT"], os.environ["AIF_RESOURCE_GROUP"]

    endpoint = get_endpoint(account, rg)
    # M10 (2026-09-22): keyless. AzureOpenAIModelConfiguration is a TypedDict,
    # NOT an OpenAI client -- it has no azure_ad_token_provider parameter, so
    # this is a different fix from every other call site.
    #
    # DO NOT 'improve' this by passing credential=DefaultAzureCredential().
    # `credential` IS an accepted key on the TypedDict -- introspection shows
    # it -- but the SDK's own validator then rejects the config with
    # 'Model config validation failed' (MISSING_FIELD / USER_ERROR). Tried
    # 2026-09-22 and reverted. Accepting a key and validating it are not the
    # same thing, and introspection cannot tell you the difference.
    #
    # OMITTING api_key is the working form: the SDK falls back to a credential
    # chain. Verified by probe_keyless_eval.py before this edit.
    judge = AzureOpenAIModelConfiguration(
        azure_endpoint=endpoint,
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
    data="m6_eval_input.jsonl",
    evaluators=evaluators,
    output_path=f"results/{timestamp}_eval_results.json",
    fail_on_evaluator_errors=True
)