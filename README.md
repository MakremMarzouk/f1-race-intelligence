# F1 Race Intelligence Automation

A local automation system that retrieves completed Formula 1 race data, calculates deterministic race insights in Python, generates a fact-based AI briefing with Ollama, and delivers it through Telegram.

## Current status

Phase 5 complete: the latest completed race can be selected dynamically and ingested through n8n. Race results are stored in PostgreSQL.

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
| `GET` | `/races/latest-completed` | Finds the latest completed race for the current year; an optional `year` query parameter selects a season. |
| `GET` | `/races/{year}/{round_number}/results` | Retrieves and normalizes completed race results through FastF1. |
| `GET` | `/races/{year}/{round_number}/analysis` | Returns deterministic race facts: winner, podium, position changes, biggest mover, fastest lap, DNFs, and points. |
| `POST` | `/races/{year}/{round_number}/ingest` | Retrieves and persists race results. Repeated calls for the same season and round do not create duplicate records. |

FastF1 provider downloads are cached locally in `f1_cache/`. The cache is ignored by Git and mounted into the API container so it survives container rebuilds.

The manual n8n workflow in `workflows/f1_race_workflow.json` looks up the latest completed race, builds its ingestion URL from the returned year and round, and validates the API response. It can be run from the n8n editor with **Execute workflow**.

Race calculations are isolated in `RaceAnalysisService`. This service receives normalized dictionaries, makes no network calls, and never uses AI.

Race persistence is isolated in `RacePersistenceService`. It stores races, drivers, and race results in PostgreSQL, while `automation_runs` is reserved for workflow tracking in a later phase.

Race results remain available when FastF1 cannot load lap timing; in that case `fastest_lap_ms` is `null`.

## Run tests

```bash
source .venv/bin/activate
python -m pytest -q
```

## Project scope

The project intentionally has no frontend, prediction system, or live telemetry analysis. Deterministic Python logic calculates facts; AI explains only validated facts; n8n orchestrates the workflow.
