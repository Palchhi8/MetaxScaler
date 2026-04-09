#!/usr/bin/env python3
"""
inference.py — Baseline inference script for the Meeting Decision Intelligence
Environment.

Uses the OpenAI Python client to call an LLM and interact with the
environment through a reset → step loop.

Environment variables (required):
    API_BASE_URL   — Base URL of the LLM API (e.g. http://localhost:8000/v1)
    MODEL_NAME     — Model identifier (e.g. gpt-4o)
    OPENAI_API_KEY — API key for authentication

Logging format:
    [START]  — printed at the beginning
    [STEP]   — printed for each task step
    [END]    — printed at the end with the final score
"""

from __future__ import annotations

import os
import sys
import time

from dotenv import load_dotenv
from openai import OpenAI

# ── Import the environment directly (no server needed for local runs) ──
from env import MeetingEnvironment
from models import MeetingAction

# Load .env if present
load_dotenv()


def get_env_var(name: str, default: str | None = None) -> str:
    """Read an environment variable or exit with helpful message."""
    value = os.getenv(name, default)
    if value is None:
        print(f"[ERROR] Environment variable {name} is not set.", file=sys.stderr)
        sys.exit(1)
    return value


def build_prompt(task_description: str, transcript: str) -> str:
    """Build a system+user prompt for the LLM."""
    return (
        "You are an expert meeting analyst AI. You will be given a meeting "
        "transcript and a specific task to perform.\n\n"
        "TASK:\n"
        f"{task_description}\n\n"
        "MEETING TRANSCRIPT:\n"
        f"{transcript}\n\n"
        "Provide a thorough, detailed response. Be specific and reference "
        "names, dates, and details from the transcript."
    )


def call_llm(client: OpenAI, model: str, prompt: str) -> str:
    """Call the LLM API and return the response text."""
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful meeting analysis assistant."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.0,  # Deterministic for reproducibility
            max_tokens=2048,
        )
        content = response.choices[0].message.content
        return content.strip() if content else ""
    except Exception as exc:
        print(f"[ERROR] LLM API call failed: {exc}", file=sys.stderr)
        return ""


def main() -> None:
    """Run the full inference loop: reset → step × 3 → report scores."""

    # ── Configuration ──────────────────────────────────────────────────
    api_base_url = get_env_var("API_BASE_URL", "https://api.openai.com/v1")
    model_name = get_env_var("MODEL_NAME", "gpt-4o")
    api_key = get_env_var("OPENAI_API_KEY")

    client = OpenAI(base_url=api_base_url, api_key=api_key)

    # ── Environment ────────────────────────────────────────────────────
    env = MeetingEnvironment()

    print("[START]")
    print(f"  Model: {model_name}")
    print(f"  API: {api_base_url}")
    print()

    start_time = time.time()

    # ── Reset ──────────────────────────────────────────────────────────
    obs = env.reset()
    done = False
    step_num = 0
    total_reward = 0.0
    task_results: list[dict] = []

    # ── Step loop ──────────────────────────────────────────────────────
    while not done:
        step_num += 1
        print(f"[STEP] Task {step_num}: {obs.task_id} (difficulty: {obs.difficulty})")

        # Build prompt & call LLM
        prompt = build_prompt(obs.task_description, obs.meeting_transcript)
        llm_response = call_llm(client, model_name, prompt)

        if not llm_response:
            print("  ⚠ Empty response from LLM — submitting placeholder.")
            llm_response = "No response generated."

        # Submit to environment
        action = MeetingAction(response=llm_response)
        obs, reward, done, info = env.step(action)

        total_reward += reward
        task_results.append({
            "task": info.get("task_id", f"task_{step_num}"),
            "reward": round(reward, 4),
            "feedback": info.get("feedback", ""),
        })

        print(f"  Reward: {reward:.4f}")
        print(f"  Feedback: {info.get('feedback', 'N/A')}")
        print()

    # ── Final report ───────────────────────────────────────────────────
    elapsed = time.time() - start_time
    avg_reward = total_reward / step_num if step_num else 0.0

    print("=" * 60)
    print("[END]")
    print(f"  Tasks completed: {step_num}")
    print(f"  Total reward:    {total_reward:.4f}")
    print(f"  Average reward:  {avg_reward:.4f}")
    print(f"  Time elapsed:    {elapsed:.1f}s")
    print()
    print("  Per-task breakdown:")
    for result in task_results:
        print(f"    {result['task']:30s}  reward={result['reward']:.4f}")
    print("=" * 60)

    # Return state for verification
    state = env.state
    print(f"\n  Episode ID: {state.episode_id}")
    print(f"  Is Done:    {state.is_done}")
    print(f"  Final Score: {avg_reward:.4f}")


if __name__ == "__main__":
    main()
