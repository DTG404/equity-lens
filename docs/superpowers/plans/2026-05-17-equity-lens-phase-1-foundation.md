# Equity Lens Phase 1 Foundation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the first working local-first foundation for Equity Lens: backend API, frontend dashboard shell, database configuration, tested domain models, and provider boundaries.

**Architecture:** Equity Lens is a local-first research terminal. Phase 1 creates a FastAPI backend, a Next.js frontend, Docker Compose Postgres, and explicit provider interfaces so market/news/AI providers can be added without changing UI contracts.

**Tech Stack:** Python 3.12, FastAPI, Pydantic, pytest, Next.js, TypeScript, React, Vitest, Postgres via Docker Compose.

---

## File Structure

```text
equity-lens/
  README.md
  AGENTS.md
  docker-compose.yml
  .gitignore
  .env.example
  docs/superpowers/plans/2026-05-17-equity-lens-phase-1-foundation.md
  backend/
    pyproject.toml
    README.md
    app/
      __init__.py
      main.py
      core/
        __init__.py
        config.py
      domain/
        __init__.py
        models.py
      providers/
        __init__.py
        base.py
        mock_market.py
      api/
        __init__.py
        routes.py
    tests/
      test_health.py
      test_watchlist_contract.py
      test_mock_market_provider.py
  frontend/
    package.json
    tsconfig.json
    next.config.mjs
    app/
      globals.css
      layout.tsx
      page.tsx
    src/
      lib/
        api.ts
      components/
        DashboardShell.tsx
    tests/
      dashboard.test.tsx
```

## Task 1: Project Metadata and Runtime Config

**Files:**
- Create: `README.md`
- Create: `AGENTS.md`
- Create: `.gitignore`
- Create: `.env.example`
- Create: `docker-compose.yml`

- [ ] **Step 1: Write project metadata files**

Create `README.md` with project purpose, local-first warning, and quick-start commands.

Create `AGENTS.md` with test/lint/audit commands:

```markdown
# Equity Lens

Local-first stock market research terminal.

## Commands

- Backend tests: `cd backend && uv run pytest`
- Backend lint: `cd backend && uv run ruff check app tests`
- Backend typecheck: `cd backend && uv run mypy app`
- Frontend tests: `cd frontend && npm test`
- Frontend lint: `cd frontend && npm run lint`
- Frontend build: `cd frontend && npm run build`
- Dependency audit: `cd frontend && npm audit --audit-level=high`
- Secrets scan: `gitleaks detect --source . --no-git`

## Security Notes

- Never commit provider API keys.
- Keep provider secrets in backend-local environment variables.
- MVP must not execute trades.
```

Create `.gitignore` for Python, Node, env files, local DB volumes, and build artifacts.

Create `.env.example`:

```env
DATABASE_URL=postgresql://equity_lens:equity_lens@localhost:5432/equity_lens
DEEPSEEK_API_KEY=
MARKET_DATA_PROVIDER=mock
NEWS_DATA_PROVIDER=mock
QUOTE_POLL_SECONDS=60
```

Create `docker-compose.yml` with a `postgres:16` service named `equity-lens-postgres` using local credentials and a named volume.

- [ ] **Step 2: Verify metadata files exist**

Run: `test -f README.md -a -f AGENTS.md -a -f docker-compose.yml -a -f .env.example`

Expected: exit code 0.

## Task 2: Backend Foundation

**Files:**
- Create: `backend/pyproject.toml`
- Create: `backend/app/main.py`
- Create: `backend/app/core/config.py`
- Create: `backend/app/api/routes.py`
- Create: `backend/tests/test_health.py`

- [ ] **Step 1: Write failing health test**

Create `backend/tests/test_health.py`:

```python
from fastapi.testclient import TestClient

from app.main import app


def test_health_endpoint_reports_service_identity():
    client = TestClient(app)

    response = client.get('/api/health')

    assert response.status_code == 200
    assert response.json() == {
        'service': 'equity-lens-api',
        'status': 'ok',
        'mode': 'local-first',
    }
```

- [ ] **Step 2: Run health test to verify failure**

Run: `cd backend && uv run pytest tests/test_health.py -q`

Expected: FAIL because `app.main` or `/api/health` does not exist.

- [ ] **Step 3: Implement FastAPI health endpoint**

Create `backend/pyproject.toml` with dependencies: fastapi, pydantic-settings, uvicorn, pytest, httpx, ruff, mypy.

Create `backend/app/main.py`:

```python
from fastapi import FastAPI

from app.api.routes import router

app = FastAPI(title='Equity Lens API')
app.include_router(router, prefix='/api')
```

Create `backend/app/api/routes.py`:

```python
from fastapi import APIRouter

router = APIRouter()


@router.get('/health')
def health() -> dict[str, str]:
    return {
        'service': 'equity-lens-api',
        'status': 'ok',
        'mode': 'local-first',
    }
```

Create `backend/app/core/config.py` with a `Settings` class reading `DATABASE_URL`, `DEEPSEEK_API_KEY`, and polling config from environment.

- [ ] **Step 4: Run backend health test**

Run: `cd backend && uv run pytest tests/test_health.py -q`

Expected: `1 passed`.

## Task 3: Backend Domain Contracts

**Files:**
- Create: `backend/app/domain/models.py`
- Create: `backend/tests/test_watchlist_contract.py`

- [ ] **Step 1: Write failing domain tests**

Create tests covering ticker normalization and watchlist item shape:

```python
from app.domain.models import TickerSymbol, WatchlistItem


def test_ticker_symbol_normalizes_to_uppercase():
    symbol = TickerSymbol(value='aapl')
    assert symbol.value == 'AAPL'


def test_ticker_symbol_rejects_invalid_symbols():
    try:
        TickerSymbol(value='../AAPL')
    except ValueError as exc:
        assert 'ticker' in str(exc).lower()
    else:
        raise AssertionError('Expected invalid ticker to raise ValueError')


def test_watchlist_item_exposes_prediction_summary_fields():
    item = WatchlistItem(symbol='MSFT', company_name='Microsoft Corp')
    assert item.symbol == 'MSFT'
    assert item.company_name == 'Microsoft Corp'
    assert item.signal == 'unrated'
    assert item.confidence == 0.0
```

- [ ] **Step 2: Run domain tests to verify failure**

Run: `cd backend && uv run pytest tests/test_watchlist_contract.py -q`

Expected: FAIL because domain models do not exist.

- [ ] **Step 3: Implement domain models**

Create Pydantic models:

- `TickerSymbol` validates 1-10 uppercase alphanumeric/dot/dash ticker strings.
- `WatchlistItem` stores symbol, optional company name, signal default `unrated`, confidence default `0.0`.

- [ ] **Step 4: Run domain tests**

Run: `cd backend && uv run pytest tests/test_watchlist_contract.py -q`

Expected: `3 passed`.

## Task 4: Market Provider Boundary

**Files:**
- Create: `backend/app/providers/base.py`
- Create: `backend/app/providers/mock_market.py`
- Create: `backend/tests/test_mock_market_provider.py`

- [ ] **Step 1: Write failing provider tests**

Create tests asserting a mock provider returns a quote for a normalized ticker and rejects invalid tickers.

- [ ] **Step 2: Run provider tests to verify failure**

Run: `cd backend && uv run pytest tests/test_mock_market_provider.py -q`

Expected: FAIL because provider modules do not exist.

- [ ] **Step 3: Implement provider protocol and mock provider**

Create:

- `Quote` Pydantic model with symbol, price, change_percent, provider.
- `MarketDataProvider` Protocol with `get_quote(symbol: TickerSymbol) -> Quote`.
- `MockMarketDataProvider` returning deterministic quote data for MVP UI.

- [ ] **Step 4: Run provider tests**

Run: `cd backend && uv run pytest tests/test_mock_market_provider.py -q`

Expected: provider tests pass.

## Task 5: Watchlist API Slice

**Files:**
- Modify: `backend/app/api/routes.py`
- Create: `backend/tests/test_watchlist_api.py`

- [ ] **Step 1: Write failing API tests**

Test `GET /api/watchlist` returns default demo watchlist with symbols, signal, confidence, and quote fields.

- [ ] **Step 2: Run API tests to verify failure**

Run: `cd backend && uv run pytest tests/test_watchlist_api.py -q`

Expected: FAIL because endpoint does not exist.

- [ ] **Step 3: Implement `/api/watchlist`**

Return deterministic local-first demo data for AAPL, MSFT, and NVDA using the mock provider.

- [ ] **Step 4: Run API tests**

Run: `cd backend && uv run pytest tests/test_watchlist_api.py -q`

Expected: watchlist API tests pass.

## Task 6: Frontend Foundation

**Files:**
- Create: `frontend/package.json`
- Create: `frontend/tsconfig.json`
- Create: `frontend/next.config.mjs`
- Create: `frontend/app/layout.tsx`
- Create: `frontend/app/page.tsx`
- Create: `frontend/app/globals.css`
- Create: `frontend/src/lib/api.ts`
- Create: `frontend/src/components/DashboardShell.tsx`
- Create: `frontend/tests/dashboard.test.tsx`

- [ ] **Step 1: Write failing frontend test**

Create a Vitest/Testing Library test that renders the dashboard shell and expects the text `Equity Lens`, `Watchlist`, and `Local-first research terminal`.

- [ ] **Step 2: Run frontend test to verify failure**

Run: `cd frontend && npm test -- --run`

Expected: FAIL because frontend components do not exist.

- [ ] **Step 3: Implement Next.js dashboard shell**

Create a dark-mode dashboard shell with:

- app title `Equity Lens`
- subtitle `Local-first research terminal`
- watchlist cards
- alert placeholder panel
- research queue placeholder panel
- safety disclaimer

- [ ] **Step 4: Run frontend test**

Run: `cd frontend && npm test -- --run`

Expected: frontend test passes.

## Task 7: Final Verification

**Files:** all created files.

- [ ] **Step 1: Run backend tests**

Run: `cd backend && uv run pytest -q`

Expected: all backend tests pass.

- [ ] **Step 2: Run backend lint**

Run: `cd backend && uv run ruff check app tests`

Expected: no lint errors.

- [ ] **Step 3: Run frontend tests**

Run: `cd frontend && npm test -- --run`

Expected: all frontend tests pass.

- [ ] **Step 4: Run frontend build**

Run: `cd frontend && npm run build`

Expected: production build succeeds.

- [ ] **Step 5: Confirm project files exist**

Run: `test -f README.md -a -f backend/app/main.py -a -f frontend/app/page.tsx -a -f docker-compose.yml`

Expected: exit code 0.
