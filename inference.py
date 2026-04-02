import os, json
from openai import OpenAI
from client import SQLReviewEnv
from models import SQLReviewAction

API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
HF_TOKEN     = os.getenv("HF_TOKEN")
MODEL_NAME   = os.getenv("MODEL_NAME", "Qwen/Qwen2.5-Coder-32B-Instruct")
HF_SPACE_URL = os.getenv("HF_SPACE_URL")

SYSTEM_PROMPT = """You are a Principal Data Engineer. You receive a SQL schema, a broken or
inefficient query, and a task description. 

RULES FOR MAX REWARD:
1. Prefer explicit JOINs over implicit comma-separated WHERE joins.
2. Use Window Functions instead of slow correlated subqueries where possible.
3. Ensure exact output column names match the requested task.
4. Keep the query strictly ANSI SQL compliant.

Respond ONLY with valid JSON in this exact format (no markdown, no backticks):
{"rewritten_query": "SELECT ...", "explanation": "Reason for changes..."}"""

DIFFICULTIES = ["easy", "medium", "hard"]

def _parse(text):
    try:
        return json.loads(text.strip())
    except Exception:
        import re
        m = re.search(r'\{.*\}', text, re.DOTALL)
        if m:
            return json.loads(m.group(0))
        return {"rewritten_query": text.strip(), "explanation": ""}

def main():
    client = OpenAI(base_url=API_BASE_URL, api_key=HF_TOKEN)
    scores = {}

    for difficulty in DIFFICULTIES:
        print(f"START: {difficulty} scenario")
        with SQLReviewEnv(base_url=HF_SPACE_URL).sync() as env:
            result = env.reset(difficulty=difficulty)
            obs = result.observation
            episode_scores = []

            for step in range(3):
                if result.done:
                    break
                user_msg = (
                    f"Schema:\n{obs.schema_ddl}\n\n"
                    f"Query to review:\n{obs.original_query}\n\n"
                    f"Task: {obs.task_description}\n"
                    f"Hint: {obs.issue_hint}"
                )
                resp = client.chat.completions.create(
                    model=MODEL_NAME,
                    max_tokens=800,
                    temperature=0.1,
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user",   "content": user_msg},
                    ],
                )
                parsed = _parse(resp.choices[0].message.content)
                action = SQLReviewAction(**parsed)
                result = env.step(action)
                obs = result.observation
                episode_scores.append(result.reward or 0.0)
                print(f"STEP: {step+1} | reward: {result.reward:.4f}")

            scores[difficulty] = max(episode_scores, default=0.0)
            print(f"END: {difficulty} | final score: {scores[difficulty]:.4f}")

    print("\n-- Baseline Scores ----------")
    for d, s in scores.items():
        print(f"  {d:8s}: {s:.4f}")
    print(f"  average : {sum(scores.values())/len(scores):.4f}")

if __name__ == "__main__":
    main()
