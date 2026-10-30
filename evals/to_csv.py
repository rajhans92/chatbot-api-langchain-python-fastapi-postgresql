# evals/to_csv.py
import json, csv
rows = [json.loads(l) for l in open("evals/dataset.jsonl")]
with open("evals/dataset.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["question", "expected", "category","user_id","session_id"])
    for r in rows:
        w.writerow([r["input"], r["expected"], r["category"], r["user_id"], r["session_id"]])