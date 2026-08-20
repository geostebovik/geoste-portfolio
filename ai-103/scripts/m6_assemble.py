import json
from pathlib import Path

with open("../iip-docs/Loan_Agreement_Promissory_Note-CUPortal-Custom-Schema.json") as f2:
    doc_text = json.load(f2)["result"]["contents"][0]["markdown"]

file_path = Path("results")
json_files = sorted(file_path.glob("*_generate_results.json"))

def build_rows():
    rows = []
    if not json_files:
        raise FileNotFoundError("No JSON files found in the results directory. Run the m6_generate.py script first to generate results.")
    with open(json_files[-1]) as f:
        print(f"Loading results from: {json_files[-1]}")
        results = json.load(f)
        for result in results:
            result_row = {"model": result["model"], "query": result["question"], "response": result["answer"], "ground_truth": result["expected_answer"], "context": doc_text}
            rows.append(result_row)
    return rows

lines = build_rows()
with open("m6_eval_input.jsonl", "w") as f:
    for line in lines:
        f.write(json.dumps(line) + "\n")
