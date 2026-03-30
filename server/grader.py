"""
Deterministic grader for the SQL Review Environment.

Scoring breakdown (total 0.0 – 1.0):
  - Correctness       (0.45): result-set comparison via in-memory SQLite
  - Plan improvement   (0.15): EXPLAIN QUERY PLAN comparison
  - Structural quality (0.15): detects removal of anti-patterns (SELECT *, DISTINCT, subquery nesting)
  - Explanation quality(0.25): keyword recall against known_issues
"""

import re
import sqlite3
from typing import Dict, List, Optional


def grade(
    schema_ddl: str,
    seed_data: Dict[str, List[dict]],
    correct_query: str,
    agent_query: str,
    original_query: str,
    explanation: Optional[str],
    known_issues: List[str],
) -> float:
    """
    Grade an agent's rewritten SQL query against the correct query.

    Returns a float in [0.0, 1.0].
    """
    correctness = _score_correctness(schema_ddl, seed_data, correct_query, agent_query)
    plan_score = _score_plan(schema_ddl, seed_data, original_query, agent_query)
    struct_score = _score_structure(original_query, agent_query, correct_query)
    expl_score = _score_explanation(explanation, known_issues)

    total = correctness + plan_score + struct_score + expl_score
    return round(min(1.0, total), 4)


# ── helpers ──────────────────────────────────────────────────────────────────


def _build_db(schema_ddl: str, seed_data: Dict[str, List[dict]]) -> sqlite3.Connection:
    """Create an in-memory SQLite database populated with schema + seed data."""
    conn = sqlite3.connect(":memory:")
    conn.executescript(schema_ddl)

    for table_name, rows in seed_data.items():
        if not rows:
            continue
        columns = list(rows[0].keys())
        placeholders = ", ".join(["?"] * len(columns))
        col_str = ", ".join(columns)
        sql = f"INSERT INTO {table_name} ({col_str}) VALUES ({placeholders})"
        for row in rows:
            conn.execute(sql, [row[c] for c in columns])
    conn.commit()
    return conn


def _run_query(conn: sqlite3.Connection, query: str):
    """Execute a query and return (rows, columns, error_msg)."""
    try:
        cur = conn.execute(query)
        rows = cur.fetchall()
        cols = [desc[0] for desc in cur.description] if cur.description else []
        return rows, cols, None
    except Exception as e:
        return None, None, str(e)


def _score_correctness(
    schema_ddl: str,
    seed_data: Dict[str, List[dict]],
    correct_query: str,
    agent_query: str,
) -> float:
    """Compare agent result set to the expected one (weight: 0.45)."""
    conn = _build_db(schema_ddl, seed_data)
    try:
        expected_rows, expected_cols, err1 = _run_query(conn, correct_query)
        if err1:
            return 0.0

        agent_rows, agent_cols, err2 = _run_query(conn, agent_query)
        if err2:
            # Agent query raised an exception → 0 points
            return 0.0

        # Exact match (order-independent)
        if sorted(expected_rows) == sorted(agent_rows):
            return 0.45

        # Partial credit: same row count and similar values
        if len(expected_rows) == len(agent_rows):
            # Check how many rows match
            expected_sorted = sorted(expected_rows)
            agent_sorted = sorted(agent_rows)
            matching = sum(1 for a, b in zip(expected_sorted, agent_sorted) if a == b)
            ratio = matching / len(expected_rows) if expected_rows else 0
            return round(0.15 + ratio * 0.20, 4)  # 0.15 to 0.35 based on match ratio

        # Some rows match but counts differ
        if expected_rows and agent_rows:
            expected_set = set(expected_rows)
            agent_set = set(agent_rows)
            overlap = len(expected_set & agent_set)
            if overlap > 0:
                return round(0.10 * (overlap / len(expected_set)), 4)

        return 0.0
    finally:
        conn.close()


def _score_plan(
    schema_ddl: str,
    seed_data: Dict[str, List[dict]],
    original_query: str,
    agent_query: str,
) -> float:
    """Compare EXPLAIN QUERY PLAN of original vs agent query (weight: 0.15)."""
    conn = _build_db(schema_ddl, seed_data)
    try:
        orig_plan = _get_plan(conn, original_query)
        agent_plan = _get_plan(conn, agent_query)

        if orig_plan is None or agent_plan is None:
            return 0.0

        # If agent plan uses SEARCH (index) where original used SCAN (full table)
        if "SEARCH" in agent_plan and "SCAN" in orig_plan:
            return 0.15

        # If agent plan has fewer total steps
        orig_steps = orig_plan.count("\n") + 1
        agent_steps = agent_plan.count("\n") + 1
        if agent_steps < orig_steps:
            return 0.10

        return 0.0
    finally:
        conn.close()


def _get_plan(conn: sqlite3.Connection, query: str) -> Optional[str]:
    """Run EXPLAIN QUERY PLAN and return the plan text."""
    try:
        cur = conn.execute(f"EXPLAIN QUERY PLAN {query}")
        rows = cur.fetchall()
        return "\n".join(str(r) for r in rows)
    except Exception:
        return None


def _score_structure(
    original_query: str,
    agent_query: str,
    correct_query: str,
) -> float:
    """
    Score structural improvements in the agent's query (weight: 0.15).

    Detects removal of known anti-patterns:
    - SELECT * → specific columns
    - Unnecessary DISTINCT removed
    - Subquery nesting removed/simplified
    - OR chains → IN clause
    - Correlated subquery → JOIN or CTE
    """
    score = 0.0
    orig_upper = original_query.upper()
    agent_upper = agent_query.upper()
    correct_upper = correct_query.upper()

    # Detect SELECT * removal
    if "SELECT *" in orig_upper and "SELECT *" not in agent_upper:
        score += 0.05

    # Detect DISTINCT removal
    if "DISTINCT" in orig_upper and "DISTINCT" not in agent_upper:
        score += 0.05

    # Detect subquery simplification (fewer nested SELECT)
    orig_subqueries = orig_upper.count("SELECT") - 1  # minus the main SELECT
    agent_subqueries = agent_upper.count("SELECT") - 1
    if orig_subqueries > 0 and agent_subqueries < orig_subqueries:
        score += 0.05

    # Detect OR → IN replacement
    orig_or_count = len(re.findall(r'\bOR\b', orig_upper))
    agent_or_count = len(re.findall(r'\bOR\b', agent_upper))
    if orig_or_count >= 2 and agent_or_count < orig_or_count and "IN" in agent_upper:
        score += 0.05

    # Detect CTE usage for complex rewrites
    if "WITH" not in orig_upper and "WITH" in agent_upper and "WITH" in correct_upper:
        score += 0.05

    # Detect correlated subquery → JOIN conversion
    if "WHERE" in orig_upper and orig_subqueries > 0 and "JOIN" in agent_upper:
        if agent_subqueries < orig_subqueries:
            score += 0.05

    # Detect HAVING → WHERE correction
    if "HAVING" in orig_upper and "WHERE" in agent_upper:
        if "HAVING" not in agent_upper or \
           (agent_upper.count("HAVING") < orig_upper.count("HAVING")):
            score += 0.05

    # Similarity to correct query bonus
    if _normalize_sql(agent_query) == _normalize_sql(correct_query):
        score += 0.05

    return min(0.15, round(score, 4))


def _normalize_sql(sql: str) -> str:
    """Normalize SQL for comparison: lowercase, collapse whitespace."""
    return re.sub(r'\s+', ' ', sql.strip().lower().rstrip(';'))


def _score_explanation(
    explanation: Optional[str],
    known_issues: List[str],
) -> float:
    """Score explanation quality based on keyword recall (weight: 0.25)."""
    if not explanation or not known_issues:
        return 0.0

    explanation_lower = explanation.lower()
    matched = sum(1 for kw in known_issues if kw.lower() in explanation_lower)
    recall = matched / len(known_issues)
    return round(recall * 0.25, 4)
