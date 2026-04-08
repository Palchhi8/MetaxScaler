"""
env.py — OpenEnv-compliant environment for Meeting Decision Intelligence.

Implements the Environment interface with:
  - reset()  → returns initial MeetingObservation
  - step(action: MeetingAction) → returns (observation, reward, done, info)
  - state    → returns MeetingState

The environment cycles through 3 tasks (easy → medium → hard) in a single
episode.  Each task is SINGLE-STEP: the agent receives the observation on
reset/previous-step, submits a response, and is graded immediately.
"""

from __future__ import annotations

import uuid
from typing import Any, Dict, Tuple

from meeting_env.models import MeetingAction, MeetingObservation, MeetingState
from meeting_env.tasks import ALL_TASKS, get_task, get_task_count
from meeting_env.grader import grade_response


class MeetingEnvironment:
    """OpenEnv-compliant Meeting Decision Intelligence Environment.

    Lifecycle
    ---------
    1. Call ``reset()`` to start a new episode.  Returns the first observation.
    2. Call ``step(action)`` with the agent's response.  The environment grades
       the response, advances to the next task, and returns:
       ``(observation, reward, done, info)``.
    3. Repeat until ``done`` is ``True`` (all 3 tasks completed).
    4. Call ``reset()`` to start a new episode.

    ``state`` can be called at any time to inspect episode metadata.
    """

    def __init__(self) -> None:
        self._episode_id: str = ""
        self._task_index: int = 0
        self._step_count: int = 0
        self._cumulative_reward: float = 0.0
        self._task_rewards: list[float] = []
        self._done: bool = True  # forces reset before first step

    # ── OpenEnv interface ──────────────────────────────────────────────

    def reset(self) -> MeetingObservation:
        """Initialise a new episode and return the first observation."""
        self._episode_id = str(uuid.uuid4())
        self._task_index = 0
        self._step_count = 0
        self._cumulative_reward = 0.0
        self._task_rewards = []
        self._done = False

        task = get_task(self._task_index)
        return MeetingObservation(
            task_id=task["task_id"],
            task_description=task["task_description"],
            meeting_transcript=task["meeting_transcript"],
            difficulty=task["difficulty"],
            reward=0.0,
            done=False,
            feedback=None,
            metadata={"episode_id": self._episode_id, "task_number": 1},
        )

    def step(
        self, action: MeetingAction
    ) -> Tuple[MeetingObservation, float, bool, Dict[str, Any]]:
        """Process the agent's action and return the next observation.

        Returns:
            (observation, reward, done, info)
        """
        if self._done:
            raise RuntimeError(
                "Episode is already done. Call reset() to start a new episode."
            )

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

        # Build observation
        if done:
            # Episode complete — return summary observation
            avg_reward = self._cumulative_reward / get_task_count()
            obs = MeetingObservation(
                task_id="episode_complete",
                task_description="All tasks completed. Episode finished.",
                meeting_transcript="",
                difficulty="n/a",
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
            # Serve next task
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

        info: Dict[str, Any] = {
            "task_id": task["task_id"],
            "reward": reward,
            "feedback": feedback,
            "step": self._step_count,
        }

        return obs, reward, done, info

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
