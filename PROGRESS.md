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
- [ ] Commit Phase 3

## Next: Phase 4 — Persistence

- Add SQLAlchemy models for races, drivers, race results, and automation runs
- Persist analyzed race data
- Prevent duplicate race ingestion
