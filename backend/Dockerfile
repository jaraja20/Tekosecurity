# TEKOSECURE Backend — production container image for on-prem deploy.
# Build:  docker build -t tekosecure-backend:latest .
# Run:    docker run --env-file .env -p 8000:8000 -v $PWD/logs:/app/logs tekosecure-backend

FROM python:3.11-slim

# System deps for paramiko / cryptography
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libssl-dev libffi-dev curl \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Ensure log dir exists at build time (server also mkdirs at runtime)
RUN mkdir -p /app/logs

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8000

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=15s \
  CMD curl -fsSL http://localhost:8000/api/health || exit 1

CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]
