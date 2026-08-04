import os, json
from dotenv import load_dotenv
from openai import AzureOpenAI
from pathlib import Path
from datetime import datetime
from m3_analyze import get_endpoint, get_subscription_key   # reuse, don't rewrite

# This script reads a text file containing question and answer pairs separated by "|"
# Splits each line into question and answer parts and removes any leading or trailing whitespace
# starting from the second line (skipping the header)
# and converts them into a list of dictionaries with "question" and "answer" keys.
def load_qa_pairs():
    # this should be replaced with user input options rather than hardcoding the file path
    with open("../iip-docs/q_a_pairs_sample.txt") as f: 
        lines = f.readlines()
    qa_pairs = []
    for line in lines[1:]:
        parts = line.split("|")
        question = parts[0].strip()
        answer = parts[1].strip()
        pair = {"question": question, "answer": answer}
        qa_pairs.append(pair)

    return qa_pairs

# Build and return an AzureOpenAI client using environment variables and helper functions.
def build_client():

    load_dotenv()
    account, rg = os.environ["AIF_ACCOUNT"], os.environ["AIF_RESOURCE_GROUP"]

    endpoint = get_endpoint(account, rg)
    key = get_subscription_key(account, rg)
    
    client = AzureOpenAI(
        azure_endpoint=endpoint,
        api_key=key,
        api_version=os.environ["CHAT_API_VERSION"],   # "2024-06-01"
    )
    return client

# this should be replaced with user input options rather than hardcoding the file path
with open("../iip-docs/Loan_Agreement_Promissory_Note-CUPortal-Custom-Schema.json") as f:
    document_text = json.load(f)["result"]["contents"][0]["markdown"]

qa_pairs = load_qa_pairs()
question = qa_pairs[0]["question"]

client = build_client()

chat_models = [os.environ["CHAT_DEPLOYMENT_GPT_5_4"], os.environ["CHAT_DEPLOYMENT_GPT_5_4_MINI"]]
results = []
for model in chat_models:
    for qa_pair in qa_pairs:
        question = qa_pair["question"]
        response = client.chat.completions.create(
            model=model,
            temperature=0,
            messages=[
                {"role": "system", "content": "Answer the question using only information from the provided document. If the answer isn't in the document, say so."},
                {"role": "user", "content": f"{document_text}\n\nQuestion: {question}"},
            ],
        )
        results.append({
            "model": model,
            "question": question,
            "answer": response.choices[0].message.content,
            "expected_answer": qa_pair["answer"]
        })

results_dir = Path("results")
results_dir.mkdir(parents=True, exist_ok=True)
timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
out_path = results_dir / f"{timestamp}_results.json"
out_path.write_text(json.dumps(results, indent=2))
print(f"Saved: {out_path}")