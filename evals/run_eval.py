import json, time, httpx, statistics
from datetime import datetime
from judges import judge_answer

API_URL = "http://127.0.0.1:8000/api/v1/chatbot/"

def load(path):
    with open(path) as f:
        return [json.loads(line) for line in f]

def call_bot(message, user_id="1", session_id="eval"):
    start = time.time()
    first_token_time = None
    chunks = []
    try:
        with httpx.stream(
            "POST",
            API_URL,
            params={"message": message},
            headers={"userId": str(user_id), "sessionId": f"{session_id}"},
            timeout=60,
            follow_redirects=True,
        ) as r:
            if r.status_code >= 400:
                body = r.read().decode(errors="replace")[:300]
                raise RuntimeError(f"{r.status_code}: {body}")
            for chunk in r.iter_text():
                if chunk and first_token_time is None:
                    first_token_time = time.time() - start
                chunks.append(chunk)

        answer = "".join(chunks).strip()
        return {
            "answer": answer,
            "latency": time.time() - start,
            "ttft": first_token_time,      # time to first token
            "tokens": None,
            "error": None if answer else "empty response",
        }
    except Exception as e:
        return {"answer": "", "latency": time.time() - start, "ttft": None,
                "tokens": None, "error": repr(e)}
def main():
    cases = load("evals/dataset.jsonl")
    rows = []
    for case in cases:
        # print(f"Running case {case['id']} (category: {case['input']})")
        out = call_bot(case["input"], 1,session_id=case["id"])
        scores = judge_answer(case, out["answer"]) if not out["error"] else {}
        rows.append({**case, **out, **scores})

    # summary
    latencies = sorted(r["latency"] for r in rows)
    p95 = latencies[int(0.95 * (len(latencies) - 1))]
    print(f"Cases: {len(rows)}")
    print(f"Error rate: {sum(1 for r in rows if r['error']) / len(rows):.0%}")
    print(f"Avg quality: {statistics.mean(r.get('quality', 0) for r in rows):.2f} / 5")
    print(f"Hallucination rate: {sum(1 for r in rows if r.get('hallucinated')) / len(rows):.0%}")
    print(f"Latency p95: {p95:.2f}s")

    path = f"evals/results/run_{datetime.now():%Y%m%d_%H%M%S}.json"
    with open(path, "w") as f:
        json.dump(rows, f, indent=2)
    print("Saved:", path)

if __name__ == "__main__":
    main()