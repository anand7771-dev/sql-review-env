"""
Core environment implementation for the SQL Review Environment.

Provides reset(), step(), and state property following the OpenEnv spec.
"""

import random
import uuid
from typing import Any, Optional

from openenv.core.env_server.interfaces import Environment
from openenv.core.env_server.types import Action, Observation, State

# Use absolute imports for both in-repo and standalone installations
import sys
import os

# Ensure the project root is on the path so `models` can be imported
_project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from models import SQLReviewAction, SQLReviewObservation, SQLReviewState
from server.scenarios import load_scenarios
from server.grader import grade


class SQLReviewEnvironment(Environment):
    """
    An RL environment for training LLM agents to review and rewrite SQL queries.

    Supports concurrent sessions (each WebSocket gets its own instance).
    """

    SUPPORTS_CONCURRENT_SESSIONS = True

    def __init__(self):
        super().__init__()
        self._scenarios = load_scenarios()
        self._current = None
        self._state = SQLReviewState()
        self._best_score = 0.0

    def reset(
        self,
        seed: Optional[int] = None,
        episode_id: Optional[str] = None,
        difficulty: Optional[str] = None,
        **kwargs: Any,
    ) -> SQLReviewObservation:
        """Reset the environment with a randomly selected scenario."""
        if seed is not None:
            random.seed(seed)

        pool = self._scenarios
        if difficulty:
            pool = [s for s in pool if s["difficulty"] == difficulty]
        if not pool:
            pool = self._scenarios

        self._current = random.choice(pool)
        self._best_score = 0.0
        self._state = SQLReviewState(
            episode_id=episode_id or str(uuid.uuid4()),
            step_count=0,
            scenario_id=self._current["id"],
            difficulty=self._current["difficulty"],
            max_steps=3,
            best_score=0.0,
        )
        return self._make_obs(done=False, reward=None)

    def step(
        self,
        action: SQLReviewAction,
        timeout_s: Optional[float] = None,
        **kwargs: Any,
    ) -> SQLReviewObservation:
        """Execute one step: grade the agent's rewritten query."""
        self._state.step_count += 1

        s = self._current
        score = grade(
            schema_ddl=s["schema_ddl"],
            seed_data=s["seed_data"],
            correct_query=s["correct_query"],
            agent_query=action.rewritten_query,
            original_query=s["original_query"],
            explanation=action.explanation,
            known_issues=s["known_issues"],
        )

        self._best_score = max(self._best_score, score)
        self._state.best_score = self._best_score

        done = score >= 1.0 or self._state.step_count >= self._state.max_steps
        return self._make_obs(done=done, reward=score)

    @property
    def state(self) -> SQLReviewState:
        """Current episode state."""
        return self._state

    def _make_obs(self, done: bool, reward: Optional[float]) -> SQLReviewObservation:
        """Construct an observation from the current scenario."""
        s = self._current or {}
        return SQLReviewObservation(
            done=done,
            reward=reward,
            schema_ddl=s.get("schema_ddl", ""),
            original_query=s.get("original_query", ""),
            sample_data=s.get("seed_data", {}),
            issue_hint=s.get("issue_hint", ""),
            task_description=s.get("task_description", ""),
            difficulty=s.get("difficulty", ""),
        )
