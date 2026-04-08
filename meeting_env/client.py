from typing import Dict

from openenv.core.client_types import StepResult
from openenv.core.env_server.types import State
from openenv.core import EnvClient

from .models import MeetingAction, MeetingObservation


class MeetingEnv(EnvClient[MeetingAction, MeetingObservation]):
    """Client for the Meeting Environment."""

    def _step_payload(self, action: MeetingAction) -> Dict:
        return {
            "response": action.response,
        }

    def _parse_result(self, payload: Dict) -> StepResult[MeetingObservation]:
        obs_data = payload.get("observation", {})
        observation = MeetingObservation(
            task_id=obs_data.get("task_id", ""),
            task_description=obs_data.get("task_description", ""),
            meeting_transcript=obs_data.get("meeting_transcript", ""),
            difficulty=obs_data.get("difficulty", "easy"),
            reward=obs_data.get("reward", 0.0),
            done=payload.get("done", False),
            feedback=obs_data.get("feedback"),
            metadata=obs_data.get("metadata", {}),
        )

        return StepResult(
            observation=observation,
            reward=payload.get("reward"),
            done=payload.get("done", False),
        )

    def _parse_state(self, payload: Dict) -> State:
        # We can extract the baseline State fields plus any extras you want
        return State(
            episode_id=payload.get("episode_id"),
            step_count=payload.get("step_count", 0),
        )
