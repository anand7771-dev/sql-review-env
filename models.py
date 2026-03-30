"""
Pydantic models for the SQL Review Environment.

Defines the Action, Observation, and State types used by the environment.
"""

from typing import Dict, List, Optional

from openenv.core.env_server.types import Action, Observation, State


class SQLReviewAction(Action):
    """Action submitted by the agent: a rewritten SQL query with optional explanation."""

    rewritten_query: str
    explanation: Optional[str] = ""


class SQLReviewObservation(Observation):
    """Observation returned to the agent after reset or step.

    Inherits `done: bool` and `reward: Optional[float]` from Observation.
    """

    schema_ddl: str = ""
    original_query: str = ""
    sample_data: Dict[str, List] = {}
    issue_hint: str = ""
    task_description: str = ""
    difficulty: str = ""  # "easy" | "medium" | "hard"


class SQLReviewState(State):
    """Internal episode state.

    Inherits `episode_id` and `step_count` from State.
    """

    scenario_id: str = ""
    difficulty: str = ""
    max_steps: int = 3
    best_score: float = 0.0
