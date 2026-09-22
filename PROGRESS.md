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
- [ ] Commit Phase 2

## Next: Phase 3 — Race Intelligence

- Calculate deterministic race insights
- Add tests for every calculation
- Keep AI and n8n out of the calculation layer
