# ─────────────────────────────────────────────────────────────
# Dockerfile for Meeting Decision Intelligence Environment
# Base: python:3.10-slim
# ─────────────────────────────────────────────────────────────

FROM python:3.10-slim

# Prevent Python from buffering stdout/stderr
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Set working directory
WORKDIR /app

# Install system dependencies (minimal)
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*

# Install OpenEnv Core first
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir openenv-core>=0.2.0 huggingface_hub

# Copy requirements and install
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project
COPY . /app

# Ensure correct path for imports
ENV PYTHONPATH=/app

# Expose the server port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command: run the FastAPI server natively via openenv module standard
CMD ["uvicorn", "server.app:app", "--host", "0.0.0.0", "--port", "8000"]
