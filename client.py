from openenv.core.env_client import EnvClient
from openenv.core.client_types import StepResult
from models import SQLReviewAction, SQLReviewObservation, SQLReviewState

class SQLReviewEnv(EnvClient[SQLReviewAction, SQLReviewObservation, SQLReviewState]):

    def _step_payload(self, action: SQLReviewAction) -> dict:
        return {
            "rewritten_query": action.rewritten_query,
            "explanation": action.explanation,
        }

    def _parse_result(self, payload: dict) -> StepResult:
        obs_data = payload.get("observation", {})
        return StepResult(
            observation=SQLReviewObservation(
                done=payload.get("done", False),
                reward=payload.get("reward"),
                schema_ddl=obs_data.get("schema_ddl", ""),
                original_query=obs_data.get("original_query", ""),
                sample_data=obs_data.get("sample_data", {}),
                issue_hint=obs_data.get("issue_hint", ""),
                task_description=obs_data.get("task_description", ""),
                difficulty=obs_data.get("difficulty", ""),
            ),
            reward=payload.get("reward"),
            done=payload.get("done", False),
        )

    def _parse_state(self, payload: dict) -> SQLReviewState:
        return SQLReviewState(
            episode_id=payload.get("episode_id"),
            step_count=payload.get("step_count", 0),
            scenario_id=payload.get("scenario_id", ""),
            difficulty=payload.get("difficulty", ""),
            max_steps=payload.get("max_steps", 3),
            best_score=payload.get("best_score", 0.0),
        )
