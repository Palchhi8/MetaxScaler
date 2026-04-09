---
title: Meeting Env
emoji: 🏢
colorFrom: blue
colorTo: indigo
sdk: docker
app_port: 8000
pinned: false
---

# 🧠 Meeting Decision Intelligence Environment

> An OpenEnv-compliant environment that evaluates AI agents for **Decision Intelligence** in real-world meeting scenarios.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://python.org)
[![OpenEnv Compatible](https://img.shields.io/badge/OpenEnv-compatible-green.svg)](https://github.com/meta-pytorch/OpenEnv)
[![License: BSD-3](https://img.shields.io/badge/license-BSD--3-lightgrey.svg)](LICENSE)

---

## 📋 Table of Contents

- [Problem Statement](#-problem-statement)
- [Why This Matters](#-why-this-matters)
- [Task Descriptions](#-task-descriptions)
- [Architecture](#-architecture)
- [Action Space](#-action-space)
- [Observation Space](#-observation-space)
- [Reward Logic](#-reward-logic)
- [Setup Instructions](#-setup-instructions)
- [Run Instructions](#-run-instructions)
- [Docker](#-docker)
- [Example Outputs](#-example-outputs)
- [Baseline Scores](#-baseline-scores)

---

## 🎯 Problem Statement

Modern organizations spend **billions of person-hours** in meetings annually, yet extracting actionable intelligence from meetings remains overwhelmingly manual. This environment benchmarks AI agents on their ability to:

1. **Understand** meeting context and participants
2. **Summarize** complex discussions accurately
3. **Extract** actionable tasks with ownership and deadlines
4. **Make decisions** under conflicting constraints (budget, deadlines, priorities)

---

## 🌍 Why This Matters

| Challenge | Real-World Impact |
|---|---|
| Meeting overload | Professionals attend 15+ meetings/week on average |
| Lost action items | 73% of action items from meetings are never completed |
| Decision fatigue | Complex trade-offs require structured analysis |
| Information silos | Key decisions get lost in unstructured transcripts |

This environment provides a **standardized benchmark** for evaluating how well AI agents can serve as intelligent meeting assistants — a problem directly applicable to enterprise productivity tools, virtual assistants, and corporate knowledge management.

---

## 📝 Task Descriptions

### 🟢 Easy — Meeting Summarization

| Property | Value |
|---|---|
| **Input** | Raw meeting transcript (Q3 Product Planning) |
| **Goal** | Extract key topics discussed |
| **Grader** | Keyword-based scoring (0.0–1.0) |
| **Scenario** | 4-person team discussing mobile redesign, API improvements, analytics dashboard |

### 🟡 Medium — Action Item Extraction

| Property | Value |
|---|---|
| **Input** | Meeting with assigned responsibilities (Sprint Retro) |
| **Goal** | Identify WHO does WHAT by WHEN |
| **Grader** | Entity matching (names + actions + context) |
| **Scenario** | 5-person team with specific tasks, deadlines, and cross-team coordination |

### 🔴 Hard — Decision Intelligence

| Property | Value |
|---|---|
| **Input** | Conflicting constraints: $150K budget vs. $280K needs |
| **Goal** | Make an optimal decision with structured reasoning |
| **Grader** | Keyword scoring + entity matching + rule-based criteria |
| **Scenario** | C-suite emergency meeting: security vulnerability vs. client retention vs. infrastructure savings |

---

## 🏗 Architecture

```
meeting_env/
├── __init__.py          # Package exports
├── models.py            # Pydantic models (Action, Observation, State)
├── env.py               # Core environment (reset, step, state)
├── tasks.py             # 3 task definitions with transcripts
├── grader.py            # Deterministic grading functions
├── app.py               # FastAPI server for HTTP access
├── inference.py         # Baseline LLM inference script
├── openenv.yaml         # OpenEnv manifest
└── requirements.txt     # Python dependencies
Dockerfile               # Container image definition
.dockerignore            # Docker build exclusions
```

### Flow

```
Agent                     Environment
  │                          │
  │──── reset() ────────────►│  Returns initial observation (Task 1)
  │◄──── observation ────────│
  │                          │
  │──── step(response) ─────►│  Grades response, returns next task
  │◄── (obs, reward, done) ──│
  │                          │
  │──── step(response) ─────►│  Grades Task 2, returns Task 3
  │◄── (obs, reward, done) ──│
  │                          │
  │──── step(response) ─────►│  Grades Task 3, done=True
  │◄── (obs, reward, done) ──│
  │                          │
  │──── state() ────────────►│  Returns episode metadata
  │◄──── MeetingState ───────│
```

---

## 🎮 Action Space

```python
class MeetingAction(BaseModel):
    response: str  # Free-text response from the agent
```

The agent submits a single text response per task. The content depends on the task:
- **Easy**: A summary of the meeting
- **Medium**: A structured list of action items
- **Hard**: A decision recommendation with reasoning

---

## 👁 Observation Space

```python
class MeetingObservation(BaseModel):
    task_id: str              # e.g., "easy_summarization"
    task_description: str     # What the agent should do
    meeting_transcript: str   # Raw meeting text
    difficulty: str           # "easy" | "medium" | "hard"
    reward: float             # Score from previous step (0.0 on reset)
    done: bool                # Whether episode is complete
    feedback: str | None      # Grading feedback
    metadata: dict            # Extra info (episode_id, task_number, etc.)
```

---

## 💰 Reward Logic

All rewards are **deterministic floats in [0.0, 1.0]** with **partial scoring**.

### Easy Task (100% keyword matching)
```
reward = (keywords_found / total_keywords)
```

### Medium Task (40% keywords + 60% entity matching)
```
reward = 0.40 × keyword_score + 0.60 × entity_score
```
Entity scoring matches `(name, action)` pairs with bonus for context.

### Hard Task (20% keywords + 30% entities + 50% decision criteria)
```
reward = 0.20 × keyword_score + 0.30 × entity_score + 0.50 × decision_score
```
Decision criteria evaluate:
- Security-first prioritization
- Risk assessment
- Revenue impact analysis
- Cost-benefit analysis
- Phased approach suggestions
- Stakeholder balance
- Reasoning quality

### Penalties
- **Empty/very short responses** (< 10 chars): reward = 0.0
- **Irrelevant responses**: Low keyword/entity match → low score automatically

---

## ⚙️ Setup Instructions

### Prerequisites
- Python 3.10+
- Docker (for containerized deployment)
- An OpenAI-compatible API key (for inference)

### Local Setup

```bash
# Clone the repository
git clone https://github.com/Palchhi8/MetaxScaler.git
cd MetaxScaler

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# Install dependencies
pip install -r meeting_env/requirements.txt

# Install the package in development mode
pip install -e .
```

### Environment Variables (for inference)

Create a `.env` file in the project root:

```env
API_BASE_URL=https://api.openai.com/v1
MODEL_NAME=gpt-4o
OPENAI_API_KEY=sk-your-key-here
```

---

## 🚀 Run Instructions

### Direct Python (no server)

```bash
# Run inference directly
python -m meeting_env.inference
```

### FastAPI Server

```bash
# Start the server
uvicorn meeting_env.app:app --host 0.0.0.0 --port 8000

# Test endpoints
curl -X POST http://localhost:8000/reset
curl -X POST http://localhost:8000/step -H "Content-Type: application/json" \
  -d '{"response": "The meeting discussed API improvements and mobile redesign."}'
curl http://localhost:8000/state
```

### Programmatic Usage

```python
from meeting_env import MeetingEnvironment, MeetingAction

env = MeetingEnvironment()
obs = env.reset()

print(f"Task: {obs.task_id}")
print(f"Description: {obs.task_description}")

action = MeetingAction(response="The meeting covered API performance, mobile redesign, and analytics dashboard.")
obs, reward, done, info = env.step(action)

print(f"Reward: {reward:.4f}")
print(f"Feedback: {info['feedback']}")
```

---

## 🐳 Docker

### Build

```bash
docker build -t meeting-env .
```

### Run (Server mode)

```bash
docker run -p 8000:8000 meeting-env
```

### Run (Inference mode)

```bash
docker run \
  -e API_BASE_URL=https://api.openai.com/v1 \
  -e MODEL_NAME=gpt-4o \
  -e OPENAI_API_KEY=sk-your-key \
  meeting-env \
  python -m meeting_env.inference
```

### Hugging Face Spaces

This environment is HF Spaces-ready. Deploy as a Docker Space:

1. Create a new Space on Hugging Face (Docker SDK)
2. Push this repository
3. The container will automatically start the FastAPI server on port 8000

---

## 📊 Example Outputs

### Easy Task — Good Response

```
[STEP] Task 1: easy_summarization (difficulty: easy)
  Response: "The Q3 planning meeting covered three main initiatives:
  1. Mobile app redesign with new wireframes focusing on navigation
     simplification and improved onboarding flow
  2. API performance improvements targeting 40% latency reduction
     through connection pooling and query optimization (3 sprints)
  3. Analytics dashboard using React with D3.js for visualizations
  Priority order: API first, then mobile, then analytics dashboard."

  Reward: 0.7500
  Feedback: Keyword coverage: 0.75 | Final score (keyword only): 0.75
```

### Hard Task — Strong Response

```
[STEP] Task 3: hard_decision (difficulty: hard)
  Reward: 0.8200
  Feedback: Keyword coverage: 0.78 | Entity matching: 0.73 |
            Decision criteria: 0.86 |
            Final score (20%kw + 30%ent + 50%dec): 0.82
```

---

## 📈 Baseline Scores

| Task | Difficulty | Random Agent | GPT-4o (baseline) |
|---|---|---|---|
| Meeting Summarization | Easy | ~0.05 | ~0.75 |
| Action Item Extraction | Medium | ~0.03 | ~0.65 |
| Decision Intelligence | Hard | ~0.02 | ~0.70 |
| **Average** | — | **~0.03** | **~0.70** |

> Scores are approximate and depend on model version and API configuration.
> A perfect score of 1.0 is achievable but requires covering all expected
> keywords, entities, and decision criteria.

---

## 🧪 Validation

```bash
# Validate OpenEnv compliance
openenv validate meeting_env/openenv.yaml

# Run Docker build
docker build -t meeting-env .

# Run inference (requires API key)
python -m meeting_env.inference

# Quick smoke test (no API key needed)
python -c "
from meeting_env import MeetingEnvironment, MeetingAction
env = MeetingEnvironment()
obs = env.reset()
assert obs.task_id == 'easy_summarization'
obs, r, d, i = env.step(MeetingAction(response='mobile redesign api performance analytics dashboard'))
assert 0.0 <= r <= 1.0
print(f'Smoke test passed! Reward: {r:.4f}')
"
```

---

## 📜 License

BSD 3-Clause License. See [LICENSE](LICENSE) for details.