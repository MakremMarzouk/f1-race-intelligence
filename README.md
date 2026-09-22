# F1 Race Intelligence Automation

A local automation system that retrieves completed Formula 1 race data, calculates deterministic race insights in Python, generates a fact-based AI briefing with Ollama, and delivers it through Telegram.

## Current status

Phase 2 complete: FastF1 race-result retrieval is available through the FastAPI service. PostgreSQL and n8n run locally through Docker Compose.

## Architecture

```text
n8n → FastAPI → FastF1
       │
       └──────→ PostgreSQL
```

Python will calculate race facts. AI will only explain validated facts. n8n will orchestrate the workflow.

## Run locally

1. Copy the environment template:

   ```bash
   cp .env.example .env
   ```

2. Set a local PostgreSQL password and random n8n encryption key in `.env`.

3. Start the services:

   ```bash
   docker compose up --build -d
   ```

## Local services

- FastAPI health: http://localhost:8000/health
- FastAPI documentation: http://localhost:8000/docs
- n8n: http://localhost:5678
- PostgreSQL: `localhost:5434`

## API endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Confirms the API is running. |
| `GET` | `/races/{year}/{round_number}/results` | Retrieves and normalizes completed race results through FastF1. |

FastF1 provider downloads are cached locally in `f1_cache/`. The cache is ignored by Git and mounted into the API container so it survives container rebuilds.

## Run tests

```bash
source .venv/bin/activate
python -m pytest -q
```

## Project scope

The project intentionally has no frontend, prediction system, or live telemetry analysis. Deterministic Python logic calculates facts; AI explains only validated facts; n8n orchestrates the workflow.
