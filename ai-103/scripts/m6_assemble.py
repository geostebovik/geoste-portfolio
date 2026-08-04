import json

with open("../iip-docs/Loan_Agreement_Promissory_Note-CUPortal-Custom-Schema.json") as f2:
    doc_text = json.load(f2)["result"]["contents"][0]["markdown"]

def build_rows():
    with open("results/20260730-131154_results.json") as f:
        results = json.load(f)
        rows = []
        for result in results:
            result_row = {"model": result["model"], "query": result["question"], "response": result["answer"], "ground_truth": result["expected_answer"], "context": doc_text}
            rows.append(result_row)
    return rows

lines = build_rows()
with open("data.jsonl", "w") as f:
    for line in lines:
        f.write(json.dumps(line) + "\n")
