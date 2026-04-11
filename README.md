---
title: Meeting Env
emoji: 🏢
colorFrom: blue
colorTo: indigo
sdk: docker
app_port: 8000
pinned: false
---

# Meeting Decision Intelligence Environment

This repository is configured to deploy as a Hugging Face Docker Space.

The actual environment package lives in [`meeting_env/`](meeting_env/README.md), while the Space entry point is the repository root `Dockerfile`.

## What runs on the Space

- OpenEnv-compatible FastAPI server on port `8000`
- `/reset`, `/step`, `/state`, `/schema`, and `/health` endpoints
- Docker-based build so the Space can run without extra HF-specific setup

## Local smoke test

```bash
docker build -t meeting-env .
docker run --rm -p 8000:8000 meeting-env
```

## Hugging Face setup

1. Create a new Space on Hugging Face.
2. Choose `Docker` as the SDK.
3. Push this repository to the Space.

If you want the full project documentation, see [`meeting_env/README.md`](meeting_env/README.md).