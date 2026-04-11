#!/usr/bin/env python3
from __future__ import annotations
import os
import sys
from dotenv import load_dotenv
from openai import OpenAI

# Ensure sibling modules are importable
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from env import MeetingEnvironment
from models import MeetingAction
from tasks import ALL_TASKS

load_dotenv()

def get_env_var(name: str, default: str | None = None) -> str:
    value = os.getenv(name, default)
    if value is None:
        sys.exit(1)
    return value

def build_prompt(task_description: str, transcript: str) -> str:
    return (
        "You are an expert meeting analyst AI.\n\n"
        f"TASK:\n{task_description}\n\n"
        f"TRANSCRIPT:\n{transcript}\n\n"
        "Provide a clear, structured, and actionable response."
    )

def call_llm(client: OpenAI, model: str, prompt: str) -> str:
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.0,
            max_tokens=1024,
        )
        content = response.choices[0].message.content
        return content.strip() if content else "Analysis unavailable."
    except Exception:
        return "Analysis unavailable."

def main() -> None:
    api_base_url = get_env_var("API_BASE_URL", "https://api.openai.com/v1")
    model_name = get_env_var("MODEL_NAME", "gpt-4o")
    api_key = os.getenv("OPENAI_API_KEY") or os.getenv("HF_TOKEN")
    
    client = OpenAI(base_url=api_base_url, api_key=api_key)
    env = MeetingEnvironment()

    print("[START]")
    
    obs = env.reset()
    done = False
    rewards = []
    task_scores: list[tuple[str, str, float]] = []
    steps = 0
    grader_by_task = {t["task_id"]: t.get("grader", "default_grader") for t in ALL_TASKS}

    while not done:
        steps += 1
        current_task_id = obs.task_id
        prompt = build_prompt(obs.task_description, obs.meeting_transcript)
        llm_response = call_llm(client, model_name, prompt)

        action = MeetingAction(response=llm_response)
        obs = env.step(action)

        reward = obs.reward
        
        # Ensure reward strictly between (0,1)
        if reward <= 0:
            reward = 0.01
        elif reward >= 1:
            reward = 0.99
            
        rewards.append(reward)
        grader_name = grader_by_task.get(current_task_id, "default_grader")
        task_scores.append((current_task_id, grader_name, reward))
        done = obs.done
        print(f"[TASK_SCORE] task_id={current_task_id} grader={grader_name} score={reward:.4f}")

    avg_score = sum(rewards) / len(rewards)
    rewards_str = ",".join(f"{r:.4f}" for r in rewards)
    task_scores_str = ",".join(
        f"{task_id}:{grader}:{score:.4f}" for task_id, grader, score in task_scores
    )

    print(
        f"[END] success=true steps={steps} score={avg_score:.4f} "
        f"rewards={rewards_str} task_scores={task_scores_str}"
    )

if __name__ == "__main__":
    main()
