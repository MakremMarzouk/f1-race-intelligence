# F1 Race Intelligence Automation

A local automation system that retrieves completed Formula 1 race data, calculates deterministic race insights in Python, generates a fact-based AI briefing with Ollama, and delivers it through Telegram.

## Current status

V1 complete: n8n selects the latest race with classified results, ingests it, requests a concise local Ollama briefing based on Python's race analysis, and sends it to a Telegram chat.

## Architecture

```text
n8n → FastAPI → FastF1
 │     ├──────→ Ollama
 │     └──────→ PostgreSQL
 └────────────→ Telegram
```

Python will calculate race facts. AI will only explain validated facts. n8n will orchestrate the workflow.

## Run locally

1. Install and open [Ollama for macOS](https://ollama.com/download), if needed.

2. Download the model configured by default in this project:

   ```bash
   ollama pull llama3.2
   ollama list
   ```

   Keep Ollama running while using the app. The Dockerized API reaches Ollama on your Mac through `host.docker.internal:11434`.

3. Copy the environment template:

   ```bash
   cp .env.example .env
   ```

4. Set a URL-safe alphanumeric PostgreSQL password and a random n8n encryption key in `.env`.

5. Start the Docker services:

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
| `GET` | `/races/latest-completed` | Finds the most recent race with classified results for the current year; an optional `year` query parameter selects a season. |
| `GET` | `/races/{year}/{round_number}/results` | Retrieves and normalizes completed race results through FastF1. |
| `GET` | `/races/{year}/{round_number}/analysis` | Returns deterministic race facts: winner, podium, position changes, biggest mover, fastest lap, DNFs, and points. |
| `GET` | `/races/{year}/{round_number}/briefing` | Uses the local Ollama model to write a concise briefing from the race analysis. |
| `POST` | `/races/{year}/{round_number}/ingest` | Retrieves and persists race results. Repeated calls for the same season and round do not create duplicate records. |

FastF1 provider downloads are cached locally in `f1_cache/`. The cache is ignored by Git and mounted into the API container so it survives container rebuilds.

The manual n8n workflow in `workflows/f1_race_workflow.json` looks up the latest race with classified results, ingests it, requests a briefing using the returned year and round, validates the API response, and sends the briefing to Telegram after success. It can be run from the n8n editor with **Execute workflow**. n8n calls FastAPI over the internal Compose network as `http://api:8000`; the browser and host tools use `http://localhost:8000`. The Telegram token is stored as an n8n credential, not in the project files. The exported workflow uses `REPLACE_WITH_YOUR_TELEGRAM_CHAT_ID`; replace that placeholder in your local n8n workflow. When importing it into another n8n instance, select or recreate the Telegram credential there.

This Compose setup is for local development: its service ports bind to `127.0.0.1`, and the API has no authentication. Do not expose these services directly to the public internet.

Race calculations are isolated in `RaceAnalysisService`. This service receives normalized dictionaries, makes no network calls, and never uses AI.

Race persistence is isolated in `RacePersistenceService`. It stores races, drivers, and race results in PostgreSQL, while `automation_runs` is reserved for workflow tracking in a later phase.

`OllamaBriefingService` sends deterministic race analysis to the local `llama3.2` model. It asks the model to explain supplied facts without inventing causes, statistics, or predictions.

Race results remain available when FastF1 cannot load lap timing; in that case `fastest_lap_ms` is `null`.

## Run tests

```bash
source .venv/bin/activate
python -m pytest -q
```

## Project scope

The project intentionally has no frontend, prediction system, or live telemetry analysis. Deterministic Python logic calculates facts; AI explains only validated facts; n8n orchestrates the workflow.
