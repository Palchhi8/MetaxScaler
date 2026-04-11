ch
# MetaxScaler - Meeting Decision Intelligence Environment 🏢

[![OpenEnv](https://img.shields.io/badge/OpenEnv-compliant-blue.svg)](https://github.com/meta-pytorch/OpenEnv)

**AI agent benchmark for meeting analysis and decision-making.**

## 🚀 Quick Start

1. **Setup API Key** (OpenAI or HF):
   ```
   echo OPENAI_API_KEY=sk-... > .env
   ```

2. **Test Inference**:
   ```
   python inference.py
   ```
   Expected: 4 tasks → [TASK_SCORE]s → [END] success=true score=~0.05+ (gpt-4o-mini)

3. **Run Server**:
   ```
   cd meeting_env
   uv sync
   uvicorn server.app:app --host 0.0.0.0 --port 8000
   ```
   Test: `curl http://localhost:8000/health`

4. **Docker**:
   ```
   docker build -t metaxscaler .
   docker run -p 8000:8000 metaxscaler
   ```

## 📋 Tasks (OpenEnv)

| ID | Difficulty | Grader | Description |
|----|------------|--------|-------------|
| easy_summarization | easy | keyword_grader | Meeting summary |
| medium_action_items | medium | entity_grader | Action items extraction |
| hard_decision | hard | decision_grader | Conflict resolution |
| executive_triage | extreme | triage_grader | Sentiment/priority |

## 🔧 Dependencies

```
uv sync  # meeting_env/pyproject.toml
# or pip install -r meeting_env/requirements.txt
```

**Required:** OpenAI API key (.env).

## 📖 Structure

```
.
├── inference.py      # Local eval
├── meeting_env/      # OpenEnv package
│   ├── openenv.yaml  # Manifest
│   ├── env.py        # Environment
│   ├── grader.py     # Graders
│   ├── models.py     # Pydantic models
│   ├── tasks.py      # Tasks data
│   └── server/app.py # FastAPI
├── Dockerfile
└── .gitignore (.env safe)
```

## 🎯 Scores & Validation

Local: Passes phase -2 (inference complete).
Server: Ready for OpenEnv validation (deploy Space/Docker).

Improve scores: Use gpt-4o, custom prompts.

## Deploy (HF Space)

1. Fork/push to HF Space (Docker SDK).
2. Auto-deploys server:8000.

**License:** BSD-3-Clause
