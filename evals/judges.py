from dotenv import load_dotenv
load_dotenv()
import json
from langchain_openai import ChatOpenAI  # swap for your provider

judge = ChatOpenAI(model="gpt-4o-mini", temperature=0)  # use any capable model

PROMPT = """You are grading a chatbot answer.

Question: {input}
Expected behavior / reference: {expected}
Chatbot answer: {answer}

Return ONLY JSON:
{{"quality": <1-5>, "hallucinated": <true/false>, "on_tone": <true/false>, "reason": "<one sentence>"}}

Rules: quality 5 = correct, relevant, complete. hallucinated = true if the answer
states facts not supported by the reference or invents information."""

def judge_answer(case, answer):
    msg = PROMPT.format(input=case["input"], expected=case["expected"], answer=answer)
    raw = judge.invoke(msg).content
    try:
        return json.loads(raw.strip().strip("`").replace("json", "", 1))
    except Exception:
        return {"quality": 0, "hallucinated": False, "reason": "judge parse error"}

def code_checks(case, answer):
    return {
        "not_empty": bool(answer.strip()),
        "no_prompt_leak": "system prompt" not in answer.lower(),
    }