# Equity Lens

**Local-first personal stock research terminal.**

Equity Lens is a local-first application for researching US equities. It is not a trading platform — it does not execute trades, connect to brokerage APIs, or provide financial advice.

## Quick Start

```bash
# Start Postgres
docker compose up -d

# Backend
cd backend
uv sync
uv run pytest
uv run uvicorn app.main:app --reload

# Frontend
cd frontend
npm install
npm test
npm run dev
```

## Architecture

- **Backend:** FastAPI + Pydantic + Postgres
- **Frontend:** Next.js + TypeScript + React
- **Providers:** Market data, news, and AI analysis through pluggable provider interfaces
- **Database:** Postgres 16 via Docker Compose

## Safety

- All data stays local unless explicitly exported.
- No trade execution capability.
- API keys for data providers live in backend environment, not frontend.
