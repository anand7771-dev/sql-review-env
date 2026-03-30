---
title: SQL Review Environment
emoji: 🧠
colorFrom: blue
colorTo: purple
sdk: docker
app_port: 7860
pinned: false
license: mit
tags:
  - openenv
  - sql
  - code-review
  - data-engineering
  - optimization
---

# 🧠 SQL Review Environment

An [OpenEnv](https://github.com/meta-pytorch/OpenEnv)-compatible reinforcement learning environment that trains AI agents to **review, debug, and optimize SQL queries** using an in-memory SQLite database for deterministic grading.

## Why This Environment?

SQL skills are among the most critical competencies for data engineers, backend developers, and data scientists. Yet even experienced engineers routinely write queries that are:

- **Incorrect** — wrong JOIN types that drop rows, missing WHERE clauses, type mismatches
- **Inefficient** — correlated subqueries, SELECT *, unnecessary DISTINCT, missing index usage
- **Hard to maintain** — deeply nested subqueries instead of CTEs, ambiguous GROUP BY

This environment provides a safe, deterministic sandbox where an LLM agent can practice identifying and fixing these exact issues across **20+ realistic scenarios** spanning three difficulty tiers.

---

## 🎯 Tasks

| Difficulty | Task ID | Description | Agent Behavior |
|------------|---------|-------------|----------------|
| **Easy** | `fix_broken_sql` | Fix broken/incorrect SQL queries | Identify wrong JOINs, missing WHEREs, bad aliases, type mismatches, wrong aggregates |
| **Medium** | `optimize_slow_query` | Optimize correct but slow queries | Replace N+1 subqueries with JOINs, remove SELECT *, eliminate redundant DISTINCT/subqueries |
| **Hard** | `rewrite_complex_query` | Rewrite complex multi-table queries | Convert correlated subqueries to CTEs, fix multi-table JOINs with NULLs, add window functions |

---

## 📦 Action Space

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `rewritten_query` | `str` | ✅ | The corrected/optimized SQL query |
| `explanation` | `str` | ❌ | Explanation of changes made (improves score) |

## 👁️ Observation Space

| Field | Type | Description |
|-------|------|-------------|
| `schema_ddl` | `str` | CREATE TABLE statements for the database |
| `original_query` | `str` | The broken/slow query to fix |
| `sample_data` | `dict` | Seed data rows per table |
| `issue_hint` | `str` | Natural language hint about the problem |
| `task_description` | `str` | What the agent should achieve |
| `difficulty` | `str` | `"easy"`, `"medium"`, or `"hard"` |
| `done` | `bool` | Whether the episode has ended |
| `reward` | `float` | Score from 0.0 to 1.0 |

---

## ⚙️ Scoring (0.0 – 1.0)

| Component | Weight | Description |
|-----------|--------|-------------|
| **Correctness** | 0.50 | Result-set comparison against reference query |
| **Plan Improvement** | 0.30 | EXPLAIN QUERY PLAN comparison (SCAN → SEARCH, fewer steps) |
| **Explanation Quality** | 0.20 | Keyword recall against known issues |

---

## 🚀 Setup

### Prerequisites

```bash
pip install openenv-core fastapi uvicorn openai
```

### Run Locally

```bash
# From the project root
cd sql-review-env

# Start the server
uvicorn server.app:app --host 0.0.0.0 --port 7860

# In another terminal, run inference
export HF_SPACE_URL="http://localhost:7860"
export API_BASE_URL="https://router.huggingface.co/v1"
export HF_TOKEN="your-hf-token"
export MODEL_NAME="your-model-name"
python inference.py
```

### Docker

```bash
# Build from project root
docker build -f server/Dockerfile -t sql-review-env .

# Run
docker run -p 7860:7860 sql-review-env
```

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `API_BASE_URL` | ✅ | LLM API endpoint (default: `https://router.huggingface.co/v1`) |
| `MODEL_NAME` | ✅ | Model identifier for inference |
| `HF_TOKEN` | ✅ | HuggingFace API token |
| `HF_SPACE_URL` | ✅ | URL of the deployed environment |

---

## 📊 Baseline Scores

| Difficulty | Score |
|------------|-------|
| easy       | 0.69  |
| medium     | 0.89  |
| hard       | 0.80  |
| **average** | **0.79** |

> Baseline scores using `Qwen/Qwen2.5-72B-Instruct` via HuggingFace Inference Providers.

---

## 📁 Project Structure

```
sql-review-env/
├── models.py              # Pydantic models: Action, Observation, State
├── client.py              # WebSocket client (MCPToolClient subclass)
├── inference.py           # Baseline agent script (MANDATORY)
├── openenv.yaml           # OpenEnv manifest
├── README.md              # This file
├── pyproject.toml          # Package configuration
├── __init__.py            # Package exports
└── server/
    ├── environment.py     # Core logic: reset/step/state + SQLite grading
    ├── scenarios.py       # 20+ query scenarios (7 easy, 7 medium, 6 hard)
    ├── grader.py          # Deterministic scoring engine
    ├── app.py             # FastAPI app via create_app()
    ├── requirements.txt   # Docker dependencies
    └── Dockerfile         # Container definition
```

---

## 🏷️ Tags

`openenv` · `sql` · `code-review` · `data-engineering` · `optimization` · `reinforcement-learning`
