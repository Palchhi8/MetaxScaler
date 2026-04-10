"""
env.py — OpenEnv-compliant environment for Meeting Decision Intelligence.

Implements the Environment interface with:
  - reset()  → returns initial MeetingObservation
  - step(action: MeetingAction) → returns MeetingObservation
  - state    → returns MeetingState

The environment cycles through 3 tasks (easy → medium → hard) in a single
episode.  Each task is SINGLE-STEP: the agent receives the observation on
reset/previous-step, submits a response, and is graded immediately.

STATE PERSISTENCE: Uses class-level state sharing so that the OpenEnv HTTP
server (which creates a new instance per request) can maintain episode state
across reset() and step() calls.
"""

from __future__ import annotations

import uuid
from typing import Any, Dict, Optional

import os as _os, sys as _sys
_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))

from models import MeetingAction, MeetingObservation, MeetingState
from tasks import get_task, get_task_count
from grader import grade_response
from openenv.core.env_server import Environment


class MeetingEnvironment(Environment):
    """OpenEnv-compliant Meeting Decision Intelligence Environment.

    Uses class-level state persistence so that stateless HTTP handlers
    (which create a new instance per request) can share episode state.
    """

    # ── Shared state across all instances (required for stateless HTTP) ──
    _shared = {
        "episode_id": "",
        "task_index": 0,
        "step_count": 0,
        "cumulative_reward": 0.0,
        "task_rewards": [],
        "done": True,
    }

    def __init__(self) -> None:
        super().__init__()
        # Load shared state into this instance
        self._episode_id: str = self._shared["episode_id"]
        self._task_index: int = self._shared["task_index"]
        self._step_count: int = self._shared["step_count"]
        self._cumulative_reward: float = self._shared["cumulative_reward"]
        self._task_rewards: list[float] = list(self._shared["task_rewards"])
        self._done: bool = self._shared["done"]

    def _persist(self) -> None:
        """Save current state to class-level storage."""
        MeetingEnvironment._shared = {
            "episode_id": self._episode_id,
            "task_index": self._task_index,
            "step_count": self._step_count,
            "cumulative_reward": self._cumulative_reward,
            "task_rewards": list(self._task_rewards),
            "done": self._done,
        }

    # ── OpenEnv interface ──────────────────────────────────────────────

    def reset(
        self,
        seed: Optional[int] = None,
        episode_id: Optional[str] = None,
        **kwargs: Any,
    ) -> MeetingObservation:
        """Initialise a new episode and return the first observation."""
        self._episode_id = episode_id or str(uuid.uuid4())
        self._task_index = 0
        self._step_count = 0
        self._cumulative_reward = 0.0
        self._task_rewards = []
        self._done = False
        self._persist()

        task = get_task(self._task_index)
        return MeetingObservation(
            task_id=task["task_id"],
            task_description=task["task_description"],
            meeting_transcript=task["meeting_transcript"],
            difficulty=task["difficulty"],
            reward=0.01,
            done=False,
            feedback=None,
            metadata={"episode_id": self._episode_id, "task_number": 1},
        )

    def step(
        self,
        action: MeetingAction,
        timeout_s: Optional[float] = None,
        **kwargs: Any,
    ) -> MeetingObservation:
        """Process the agent's action and return the next observation.

        The OpenEnv framework reads reward and done from the returned
        observation object directly (observation.reward, observation.done).
        """
        # Auto-reset if called on a fresh/done instance
        if self._done:
            self.reset()

        # Grade current task
        task = get_task(self._task_index)
        reward, feedback = grade_response(action.response, task)

        self._step_count += 1
        self._cumulative_reward += reward
        self._task_rewards.append(reward)

        # Advance to next task
        self._task_index += 1
        done = self._task_index >= get_task_count()
        self._done = done
        self._persist()

        # Build observation
        if done:
            avg_reward = self._cumulative_reward / get_task_count()
            obs = MeetingObservation(
                task_id="episode_complete",
                task_description="All tasks completed. Episode finished.",
                meeting_transcript="",
                difficulty="done",
                reward=reward,
                done=True,
                feedback=feedback,
                metadata={
                    "episode_id": self._episode_id,
                    "task_number": self._task_index,
                    "cumulative_reward": round(self._cumulative_reward, 4),
                    "average_reward": round(avg_reward, 4),
                    "task_rewards": [round(r, 4) for r in self._task_rewards],
                },
            )
        else:
            next_task = get_task(self._task_index)
            obs = MeetingObservation(
                task_id=next_task["task_id"],
                task_description=next_task["task_description"],
                meeting_transcript=next_task["meeting_transcript"],
                difficulty=next_task["difficulty"],
                reward=reward,
                done=False,
                feedback=feedback,
                metadata={
                    "episode_id": self._episode_id,
                    "task_number": self._task_index + 1,
                    "previous_task_reward": round(reward, 4),
                },
            )

        return obs

    @property
    def state(self) -> MeetingState:
        """Return current episode state / metadata."""
        return MeetingState(
            episode_id=self._episode_id or "no-episode",
            current_task_index=self._task_index,
            total_tasks=get_task_count(),
            step_count=self._step_count,
            cumulative_reward=round(self._cumulative_reward, 4),
            is_done=self._done,
            task_rewards=[round(r, 4) for r in self._task_rewards],
        )

    def close(self) -> None:
        """Clean up resources. Required by the OpenEnv HTTP server."""
        pass
