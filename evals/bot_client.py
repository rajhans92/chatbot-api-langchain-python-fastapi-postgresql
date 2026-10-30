from dotenv import load_dotenv
load_dotenv()

from langsmith import evaluate
from openevals.llm import create_llm_as_judge
from openevals.prompts import CORRECTNESS_PROMPT
from run_eval import call_bot
JUDGE_MODEL = "openai:gpt-4o-mini" 
def target(inputs: dict) -> dict:
    out = call_bot(inputs["question"], user_id=str(inputs["user_id"]), session_id=str(inputs["session_id"]))
    return {"answer": out["answer"], "latency": out["latency"], "error": out["error"]}

# plain code checks
def no_error(outputs: dict) -> dict:
    ok = outputs.get("error") is None and bool(outputs.get("answer"))
    return {"key": "no_error", "score": int(ok)}

def latency_ok(outputs: dict) -> dict:
    return {"key": "latency_under_6s", "score": int(outputs.get("latency", 999) < 6)}

# --- Code checks ---
def no_prompt_leak(outputs):
    return {"key": "no_prompt_leak", "score": int("system prompt" not in outputs["answer"].lower())}

def reasonable_length(outputs):
    n = len(outputs["answer"].split())
    return {"key": "length_ok", "score": int(3 <= n <= 300)}

HALLUCINATION_PROMPT = """You are checking a chatbot answer for hallucination.
Question: {inputs}
Reference: {reference_outputs}
Answer: {outputs}
Score true if the answer contains NO invented or unsupported facts. If it says it
doesn't know when the reference has no info, that is correct."""

hallucination_free = create_llm_as_judge(
    prompt=HALLUCINATION_PROMPT, feedback_key="hallucination_free", model=JUDGE_MODEL)

TONE_PROMPT = """Is this answer polite, professional, and clear?
Question: {inputs}
Answer: {outputs}
Score true if yes."""

tone_ok = create_llm_as_judge(
    prompt=TONE_PROMPT, feedback_key="tone_ok", model=JUDGE_MODEL)

# prebuilt LLM judge, no prompt writing
correctness = create_llm_as_judge(
    prompt=CORRECTNESS_PROMPT,
    feedback_key="correctness",
    model=JUDGE_MODEL,
)

if __name__ == "__main__":
    evaluate(
        target,
        data="chatbot-golden-v1",
        evaluators=[no_error, latency_ok, no_prompt_leak, reasonable_length,
                correctness, hallucination_free, tone_ok],
        experiment_prefix="baseline",
        max_concurrency=2,
    )