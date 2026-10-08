# Project Progress

## Phase 1 — Infrastructure

- [x] Created an independent Git repository
- [x] Created the FastAPI project structure
- [x] Implemented and tested `GET /health`
- [x] Dockerized the FastAPI application
- [x] Added PostgreSQL through Docker Compose
- [x] Added n8n through Docker Compose
- [x] Protected local secrets with `.env` and `.gitignore`
- [x] Added the first automated API test
- [x] Commit Phase 1

## Phase 2 — F1 Data

- [x] Installed FastF1
- [x] Added a persistent local FastF1 cache
- [x] Created `app/services/f1_service.py`
- [x] Retrieved and normalized completed race results
- [x] Added `GET /races/{year}/{round_number}/results`
- [x] Verified the endpoint through Docker
- [x] Added a provider-service unit test
- [x] Commit Phase 2

## Phase 3 — Race Intelligence

- [x] Loaded the valid per-driver fastest lap from FastF1 lap data
- [x] Created `app/services/analysis_service.py`
- [x] Calculated winner, podium, and position changes
- [x] Calculated biggest mover and fastest lap
- [x] Calculated DNFs, driver points, and constructor points
- [x] Added `GET /races/{year}/{round_number}/analysis`
- [x] Tested analysis with classified and DNF race examples
- [x] Added deterministic analysis unit tests
- [x] Commit Phase 3

## Phase 4 — Persistence

- [x] Added SQLAlchemy and PostgreSQL configuration
- [x] Created `races`, `drivers`, `race_results`, and `automation_runs` tables
- [x] Added automatic table creation when FastAPI starts
- [x] Created `RacePersistenceService`
- [x] Added `POST /races/{year}/{round_number}/ingest`
- [x] Added persistence and duplicate-ingestion tests
- [x] Verified live ingestion into PostgreSQL
- [x] Verified duplicate prevention with a second ingestion request
- [x] Commit Phase 4

## Phase 5 — n8n Orchestration

- [x] Add `GET /races/latest-completed` with optional season selection
- [x] Select the latest completed race dynamically from the FastF1 schedule
- [x] Continue race ingestion when optional lap timing data is unavailable
- [x] Add an n8n manual workflow that looks up and ingests the selected race
- [x] Validate the ingestion response and route lookup failures to Stop and Error
- [x] Export the n8n workflow to `workflows/f1_race_workflow.json`
- [x] Add tests for latest-race selection and missing lap timing
- [x] Verify a live dynamic ingestion through n8n
- [x] Add retry and failure handling to the ingestion node
- [x] Commit Phase 5

## Phase 6 — AI Race Briefing

- [x] Configure the local Ollama URL and `llama3.2` model
- [x] Create `OllamaBriefingService` using grounded, concise instructions
- [x] Add `GET /races/{year}/{round_number}/briefing`
- [x] Add a mocked service test so tests do not call Ollama
- [x] Extend the n8n workflow to request a briefing for the selected race
- [x] Preserve the generated briefing in the workflow success output
- [x] Verify a live 2026 race briefing through FastAPI and n8n
- [x] Run the test suite (8 passed)
- [x] Commit Phase 6

## Phase 7 — Telegram Delivery

- [x] Create a Telegram bot and configure its token as an n8n credential
- [x] Send the generated briefing to the user's Telegram chat after successful workflow completion
- [x] Export the updated workflow to `workflows/f1_race_workflow.json`
- [x] Verify an end-to-end Telegram delivery
- [x] Run the test suite (8 passed, 2 dependency deprecation warnings)

## Phase 8 — Review and polish

- [x] Document Ollama setup and model availability in the README
- [x] Set explicit three-attempt retries for race lookup, ingestion, briefing, and Telegram delivery
- [x] Review Telegram retry behavior and export a chat ID placeholder instead of a personal ID
- [x] Document that local services are not configured for public internet exposure
