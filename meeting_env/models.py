"""
models.py — Typed Pydantic models for the Meeting Decision Intelligence Environment.

Defines the core data structures used by the OpenEnv interface:
  - MeetingAction: what the agent submits (its response text)
  - MeetingObservation: what the environment returns (meeting transcript, task info, scores)
  - MeetingState: episode metadata for state() calls
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Action — sent by the agent
# ---------------------------------------------------------------------------

class MeetingAction(BaseModel):
    """Action submitted by the AI agent.

    Attributes:
        response: Free-text response from the agent.  Depending on the
            current task this may be a summary, extracted action items,
            or a decision recommendation.
    """
    response: str = Field(
        ...,
        description="The agent's textual response to the current meeting task.",
    )


# ---------------------------------------------------------------------------
# Observation — returned by the environment
# ---------------------------------------------------------------------------

class MeetingObservation(BaseModel):
    """Observation returned to the agent after reset() or step().

    Attributes:
        task_id: Identifier for the current task (e.g. "easy", "medium", "hard").
        task_description: Human-readable description of what the agent should do.
        meeting_transcript: The raw meeting discussion text the agent must analyse.
        difficulty: One of "easy", "medium", "hard".
        reward: Float reward in [0.0, 1.0] (0.0 on reset, scored after step).
        done: Whether the current episode has ended.
        feedback: Optional grading feedback explaining the score.
        metadata: Arbitrary extra information.
    """
    task_id: str = Field(..., description="Unique task identifier.")
    task_description: str = Field(..., description="What the agent is expected to do.")
    meeting_transcript: str = Field(..., description="Raw meeting discussion text.")
    difficulty: str = Field(..., description="Task difficulty: easy | medium | hard.")
    reward: float = Field(default=0.0, ge=0.0, le=1.0, description="Reward score.")
    done: bool = Field(default=False, description="Whether the episode is finished.")
    feedback: Optional[str] = Field(default=None, description="Grading feedback.")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Extra info.")


# ---------------------------------------------------------------------------
# State — episode metadata
# ---------------------------------------------------------------------------

class MeetingState(BaseModel):
    """Tracks episode-level metadata returned by state().

    Attributes:
        episode_id: Unique identifier for the current episode.
        current_task_index: Index of the active task (0-based).
        total_tasks: Total number of tasks in a full run.
        step_count: Number of steps taken so far in this episode.
        cumulative_reward: Sum of rewards collected in this episode.
        is_done: Whether all tasks have been completed.
        task_rewards: Per-task reward breakdown.
    """
    episode_id: str = Field(..., description="Unique episode identifier.")
    current_task_index: int = Field(default=0, description="0-based task index.")
    total_tasks: int = Field(default=3, description="Number of tasks.")
    step_count: int = Field(default=0, description="Steps taken so far.")
    cumulative_reward: float = Field(default=0.0, description="Total reward so far.")
    is_done: bool = Field(default=False, description="True when all tasks done.")
    task_rewards: List[float] = Field(default_factory=list, description="Per-task rewards.")
