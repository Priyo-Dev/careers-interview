import json
import os
from openai import OpenAI

_client: OpenAI | None = None


def _client_get() -> OpenAI:
    global _client
    if _client is None:
        key = os.environ.get("OPENAI_API_KEY")
        if not key:
            raise ValueError("OPENAI_API_KEY not set")
        _client = OpenAI(api_key=key)
    return _client


def generate_questions(role_description: str, num_questions: int = 5) -> list[str]:
    """Generate interview questions for the given role. Returns list of question strings."""
    client = _client_get()
    prompt = f"""Generate exactly {num_questions} interview questions for this role. Return ONLY a JSON array of strings, no other text.

Role description:
{role_description}

Example format: ["Question 1?", "Question 2?", ...]"""
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
    )
    text = resp.choices[0].message.content.strip()
    # Handle possible markdown code block
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
        text = text.strip()
    return json.loads(text)


def judge_answer(role_description: str, question: str, transcript: str) -> dict:
    """Judge the candidate answer. Returns { score: int 1-10, feedback: str }."""
    client = _client_get()
    prompt = f"""You are an interviewer. Score this candidate's answer from 1 to 10 and give brief feedback.

Role: {role_description}
Question: {question}
Candidate's answer (transcribed): {transcript}

Return ONLY valid JSON with exactly these keys: "score" (integer 1-10), "feedback" (string). No other text."""
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )
    text = resp.choices[0].message.content.strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
        text = text.strip()
    return json.loads(text)
