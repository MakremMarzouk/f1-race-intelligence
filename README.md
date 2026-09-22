# F1 Race Intelligence Automation

A local automation system that will retrieve completed Formula 1 race data, calculate deterministic race insights in Python, generate a fact-based AI briefing with Ollama, and deliver it through Telegram.

## Current status

Phase 1 complete: FastAPI, PostgreSQL, and n8n run locally with Docker Compose.

## Architecture

```text
n8n → FastAPI → PostgreSQL