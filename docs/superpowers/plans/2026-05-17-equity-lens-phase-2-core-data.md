# Equity Lens Phase 2: Core User Data Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add persistent storage, watchlist CRUD, manual holdings, ticker/company metadata, and user settings to Equity Lens.

**Architecture:** The backend moves from in-memory demo data to SQLAlchemy-backed persistent storage. The watchlist API becomes CRUD. A holdings table tracks manual portfolio entries. Company metadata is stored locally. Settings become a key-value store. The DB connection is configured via `DATABASE_URL` env var — defaults to SQLite for local dev, Postgres for production.

**Tech Stack:** SQLAlchemy 2.0 (async), Alembic, aiosqlite (dev/testing), asyncpg (production), FastAPI dependency injection, Pydantic v2 schemas.

---

## File Structure Changes

```
backend/
  pyproject.toml                 # + sqlalchemy, alembic, aiosqlite, asyncpg
  app/
    main.py                      # + lifespan startup for DB
    core/
      db.py                      # NEW: engine, session factory, get_db dependency
      config.py                  # + DATABASE_URL defaults to sqlite
      settings_store.py          # NEW: key-value settings CRUD
    domain/
      models.py                  # unchanged (pydantic schemas kept)
      db_models.py               # NEW: SQLAlchemy ORM models
    api/
      routes.py                  # + watchlist POST/DELETE, holdings CRUD, settings
      watchlist_routes.py        # NEW: watchlist CRUD endpoints
      holdings_routes.py         # NEW: holdings CRUD endpoints
      settings_routes.py         # NEW: settings endpoints
    providers/
      base.py                    # + get_quote returns None for unknown tickers
  alembic/
    env.py                       # NEW: Alembic env
    versions/
      001_initial.py             # NEW: initial migration
  alembic.ini                    # NEW: Alembic config
  tests/
    conftest.py                  # NEW: test DB session override
    test_watchlist_crud.py       # NEW: watchlist CRUD tests
    test_holdings.py             # NEW: holdings tests
    test_settings.py             # NEW: settings tests
    test_db_models.py            # NEW: DB model tests
frontend/
  src/
    lib/
      api.ts                     # + addToWatchlist, removeFromWatchlist, fetchHoldings, addHolding
    components/
      DashboardShell.tsx         # + add-ticker form, holdings section
  tests/
    dashboard.test.tsx           # + test for new UI elements
```

## Task 1: Add Dependencies and DB Core

**Files:**
- Modify: `backend/pyproject.toml`
- Create: `backend/app/core/db.py`
- Create: `backend/tests/test_db_models.py`
- Create: `backend/app/domain/db_models.py`

- [ ] **Step 1: Add DB dependencies to pyproject.toml**

Add to `dependencies`:
```toml
    "sqlalchemy[asyncio]>=2.0",
    "alembic>=1.14",
```

Add to `[project.optional-dependencies] dev`:
```toml
    "aiosqlite>=0.20",
```

- [ ] **Step 2: Install new dependencies**

Run: `cd backend && uv sync`

Expected: dependencies installed successfully.

- [ ] **Step 3: Write failing DB model tests**

Create `backend/tests/test_db_models.py`:

```python
"""Tests for SQLAlchemy ORM models."""

import pytest
from sqlalchemy import select

from app.domain.db_models import WatchlistEntry, Holding, Setting


@pytest.mark.asyncio
async def test_watchlist_entry_round_trip(async_db_session):
    entry = WatchlistEntry(symbol='AAPL', company_name='Apple Inc.')
    async_db_session.add(entry)
    await async_db_session.commit()

    result = await async_db_session.execute(
        select(WatchlistEntry).where(WatchlistEntry.symbol == 'AAPL')
    )
    saved = result.scalar_one()
    assert saved.symbol == 'AAPL'
    assert saved.company_name == 'Apple Inc.'
    assert saved.created_at is not None


@pytest.mark.asyncio
async def test_holding_round_trip(async_db_session):
    holding = Holding(symbol='MSFT', quantity=10, average_cost=350.0)
    async_db_session.add(holding)
    await async_db_session.commit()

    result = await async_db_session.execute(
        select(Holding).where(Holding.symbol == 'MSFT')
    )
    saved = result.scalar_one()
    assert saved.symbol == 'MSFT'
    assert saved.quantity == 10
    assert saved.average_cost == 350.0


@pytest.mark.asyncio
async def test_setting_round_trip(async_db_session):
    s = Setting(key='theme', value='dark')
    async_db_session.add(s)
    await async_db_session.commit()

    result = await async_db_session.execute(
        select(Setting).where(Setting.key == 'theme')
    )
    saved = result.scalar_one()
    assert saved.key == 'theme'
    assert saved.value == 'dark'
```

- [ ] **Step 4: Run tests to verify failure**

Run: `cd backend && uv run pytest tests/test_db_models.py -q`

Expected: FAIL with ImportError because modules don't exist yet.

- [ ] **Step 5: Create SQLAlchemy ORM models**

Create `backend/app/domain/db_models.py`:

```python
"""SQLAlchemy ORM models for persistent storage."""

from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, Integer, String, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class WatchlistEntry(Base):
    __tablename__ = 'watchlist_entries'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    symbol: Mapped[str] = mapped_column(String(10), unique=True, nullable=False, index=True)
    company_name: Mapped[str] = mapped_column(String(255), default='')
    notes: Mapped[str] = mapped_column(String(1000), default='')
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class Holding(Base):
    __tablename__ = 'holdings'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    symbol: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    quantity: Mapped[float] = mapped_column(Float, nullable=False)
    average_cost: Mapped[float] = mapped_column(Float, nullable=False)
    notes: Mapped[str] = mapped_column(String(1000), default='')
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class CompanyInfo(Base):
    __tablename__ = 'company_info'

    symbol: Mapped[str] = mapped_column(String(10), primary_key=True)
    company_name: Mapped[str] = mapped_column(String(255), default='')
    sector: Mapped[str] = mapped_column(String(100), default='')
    industry: Mapped[str] = mapped_column(String(100), default='')
    description: Mapped[str] = mapped_column(String(5000), default='')
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class Setting(Base):
    __tablename__ = 'settings'

    key: Mapped[str] = mapped_column(String(100), primary_key=True)
    value: Mapped[str] = mapped_column(String(1000), default='')
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
```

- [ ] **Step 6: Create DB core module**

Create `backend/app/core/db.py`:

```python
"""Database engine, session factory, and FastAPI dependency."""

from collections.abc import AsyncGenerator
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings as app_settings
from app.domain.db_models import Base

_engine: Any = None
_async_session_factory: async_sessionmaker[AsyncSession] | None = None


def get_db_url() -> str:
    """Return the database URL, converting common schemes for async access."""
    url = app_settings.database_url
    if url.startswith('sqlite:///'):
        return url.replace('sqlite:///', 'sqlite+aiosqlite:///', 1)
    if url.startswith('postgresql://'):
        return url.replace('postgresql://', 'postgresql+asyncpg://', 1)
    if url.startswith('postgres://'):
        return url.replace('postgres://', 'postgresql+asyncpg://', 1)
    return url


async def init_db() -> None:
    """Create engine, run migrations or create tables."""
    global _engine, _async_session_factory
    url = get_db_url()
    _engine = create_async_engine(url, echo=False)
    _async_session_factory = async_sessionmaker(
        _engine, class_=AsyncSession, expire_on_commit=False
    )
    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db() -> None:
    """Dispose the engine."""
    global _engine
    if _engine is not None:
        await _engine.dispose()
        _engine = None


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency that yields a session."""
    if _async_session_factory is None:
        await init_db()
    assert _async_session_factory is not None
    async with _async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
```

- [ ] **Step 7: Create test fixtures (conftest.py)**

Create `backend/tests/conftest.py`:

```python
"""Test fixtures for async DB testing."""

from collections.abc import AsyncGenerator
from typing import Any

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.domain.db_models import Base

TEST_DB_URL = 'sqlite+aiosqlite://'


@pytest.fixture(scope='session')
def _engine() -> Any:
    engine = create_async_engine(TEST_DB_URL, echo=False)
    return engine


@pytest_asyncio.fixture(autouse=True)
async def _create_tables(_engine: Any) -> AsyncGenerator[None, None]:
    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def async_db_session(_engine: Any) -> AsyncGenerator[AsyncSession, None]:
    factory = async_sessionmaker(_engine, class_=AsyncSession, expire_on_commit=False)
    async with factory() as session:
        yield session
```

- [ ] **Step 8: Update main.py with lifespan**

Modify `backend/app/main.py`:

```python
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes import router
from app.core.db import close_db, init_db


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None, None]:
    await init_db()
    yield
    await close_db()


app = FastAPI(title='Equity Lens API', lifespan=lifespan)
app.include_router(router, prefix='/api')
```

- [ ] **Step 9: Run tests to verify they pass**

Run: `cd backend && uv run pytest tests/test_db_models.py -q`

Expected: all tests pass.

## Task 2: Watchlist CRUD API

**Files:**
- Create: `backend/app/api/watchlist_routes.py`
- Create: `backend/tests/test_watchlist_crud.py`
- Modify: `backend/app/api/routes.py` (remove demo hardcoded watchlist)

- [ ] **Step 1: Write failing watchlist CRUD tests**

Create `backend/tests/test_watchlist_crud.py`:

```python
"""Tests for watchlist CRUD endpoints."""
from httpx import AsyncClient, ASGITransport
import pytest

from app.main import app


@pytest.fixture
async def client() -> AsyncClient:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url='http://test') as ac:
        yield ac


@pytest.mark.asyncio
async def test_add_watchlist_entry(client: AsyncClient):
    response = await client.post('/api/watchlist', json={
        'symbol': 'AAPL',
        'company_name': 'Apple Inc.'
    })
    assert response.status_code == 200
    data = response.json()
    assert data['symbol'] == 'AAPL'
    assert data['company_name'] == 'Apple Inc.'


@pytest.mark.asyncio
async def test_list_watchlist_returns_added_entries(client: AsyncClient):
    await client.post('/api/watchlist', json={'symbol': 'MSFT', 'company_name': 'Microsoft Corp'})

    response = await client.get('/api/watchlist')
    assert response.status_code == 200
    data = response.json()
    symbols = [item['symbol'] for item in data]
    assert 'MSFT' in symbols


@pytest.mark.asyncio
async def test_delete_watchlist_entry(client: AsyncClient):
    await client.post('/api/watchlist', json={'symbol': 'NVDA', 'company_name': 'NVIDIA Corp'})

    response = await client.delete('/api/watchlist/NVDA')
    assert response.status_code == 200

    response = await client.get('/api/watchlist')
    symbols = [item['symbol'] for item in response.json()]
    assert 'NVDA' not in symbols


@pytest.mark.asyncio
async def test_add_duplicate_symbol_returns_error(client: AsyncClient):
    await client.post('/api/watchlist', json={'symbol': 'AAPL'})
    response = await client.post('/api/watchlist', json={'symbol': 'AAPL'})
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_add_invalid_ticker_returns_error(client: AsyncClient):
    response = await client.post('/api/watchlist', json={'symbol': '../INVALID'})
    assert response.status_code == 422
```

- [ ] **Step 2: Run tests to verify failure**

Run: `cd backend && uv run pytest tests/test_watchlist_crud.py -q`

Expected: FAIL because endpoints don't exist.

- [ ] **Step 3: Create watchlist routes**

Create `backend/app/api/watchlist_routes.py`:

```python
"""Watchlist CRUD endpoints."""
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_session
from app.domain.db_models import WatchlistEntry
from app.domain.models import TickerSymbol

router = APIRouter(prefix='/watchlist', tags=['watchlist'])


class WatchlistCreateRequest(BaseModel):
    symbol: str
    company_name: str = ''


class WatchlistResponse(BaseModel):
    symbol: str
    company_name: str


@router.get('')
async def list_watchlist(
    session: AsyncSession = Depends(get_session),
) -> list[dict[str, Any]]:
    result = await session.execute(select(WatchlistEntry).order_by(WatchlistEntry.created_at))
    entries = result.scalars().all()
    return [{'symbol': e.symbol, 'company_name': e.company_name} for e in entries]


@router.post('')
async def add_to_watchlist(
    body: WatchlistCreateRequest,
    session: AsyncSession = Depends(get_session),
) -> dict[str, str]:
    # Validate ticker
    TickerSymbol(value=body.symbol)

    # Check duplicate
    existing = await session.execute(
        select(WatchlistEntry).where(WatchlistEntry.symbol == body.symbol.upper())
    )
    if existing.scalar_one_or_none() is not None:
        raise HTTPException(status_code=409, detail=f'{body.symbol.upper()} already in watchlist')

    entry = WatchlistEntry(symbol=body.symbol.upper(), company_name=body.company_name)
    session.add(entry)
    await session.flush()
    return {'symbol': entry.symbol, 'company_name': entry.company_name}


@router.delete('/{symbol}')
async def remove_from_watchlist(
    symbol: str,
    session: AsyncSession = Depends(get_session),
) -> dict[str, str]:
    result = await session.execute(
        select(WatchlistEntry).where(WatchlistEntry.symbol == symbol.upper())
    )
    entry = result.scalar_one_or_none()
    if entry is None:
        raise HTTPException(status_code=404, detail=f'{symbol.upper()} not in watchlist')
    await session.delete(entry)
    return {'status': 'removed', 'symbol': symbol.upper()}
```

- [ ] **Step 4: Register watchlist router in routes.py**

Replace `backend/app/api/routes.py` with:

```python
from fastapi import APIRouter

from app.api.watchlist_routes import router as watchlist_router
from app.providers.mock_market import MockMarketDataProvider

router = APIRouter()
router.include_router(watchlist_router)

_provider = MockMarketDataProvider()


@router.get('/health')
def health() -> dict[str, str]:
    return {
        'service': 'equity-lens-api',
        'status': 'ok',
        'mode': 'local-first',
    }
```

- [ ] **Step 5: Run tests**

Run: `cd backend && uv run pytest tests/test_watchlist_crud.py -q`

Expected: all tests pass.

## Task 3: Holdings CRUD API

**Files:**
- Create: `backend/app/api/holdings_routes.py`
- Create: `backend/tests/test_holdings.py`

- [ ] **Step 1: Write failing holdings tests**

Create `backend/tests/test_holdings.py` with tests for:
- add holding
- list holdings
- update holding
- delete holding
- invalid symbol returns 422

- [ ] **Step 2: Run tests to verify failure**

Run: `cd backend && uv run pytest tests/test_holdings.py -q`

Expected: FAIL.

- [ ] **Step 3: Create holdings routes**

Create `backend/app/api/holdings_routes.py` with CRUD endpoints for `Holding` model:
- GET /holdings — list all
- POST /holdings — add
- PUT /holdings/{id} — update quantity/cost
- DELETE /holdings/{id} — remove

Register the router in `routes.py`.

- [ ] **Step 4: Run tests**

Run: `cd backend && uv run pytest tests/test_holdings.py -q`

Expected: all pass.

## Task 4: Settings API

**Files:**
- Create: `backend/app/api/settings_routes.py`
- Create: `backend/tests/test_settings.py`

- [ ] **Step 1: Write failing settings tests**

Create `backend/tests/test_settings.py` with tests for:
- GET /settings returns key-value pairs
- PUT /settings updates a value
- GET /settings/{key} returns single value
- PUT /settings with empty key returns 422

- [ ] **Step 2: Run tests to verify failure**

Run: `cd backend && uv run pytest tests/test_settings.py -q`

Expected: FAIL.

- [ ] **Step 3: Create settings routes**

Create `backend/app/api/settings_routes.py` with endpoints:
- GET /settings — list all
- GET /settings/{key} — get one
- PUT /settings — create or update key-value

Register in `routes.py`.

- [ ] **Step 4: Run tests**

Run: `cd backend && uv run pytest tests/test_settings.py -q`

Expected: all pass.

## Task 5: Frontend Watchlist Management + Holdings Display

**Files:**
- Modify: `frontend/src/lib/api.ts`
- Modify: `frontend/src/components/DashboardShell.tsx`
- Modify: `frontend/tests/dashboard.test.tsx`

- [ ] **Step 1: Add API client functions**

Add to `frontend/src/lib/api.ts`:

```typescript
export interface HoldingItem {
  id: number;
  symbol: string;
  quantity: number;
  average_cost: number;
  notes: string;
}

export async function addToWatchlist(symbol: string, companyName?: string): Promise<void> {
  const response = await fetch(`${API_BASE}/api/watchlist`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ symbol, company_name: companyName ?? '' }),
  });
  if (!response.ok) {
    const err = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(err.detail || 'Failed to add to watchlist');
  }
}

export async function removeFromWatchlist(symbol: string): Promise<void> {
  const response = await fetch(`${API_BASE}/api/watchlist/${symbol}`, { method: 'DELETE' });
  if (!response.ok) throw new Error('Failed to remove from watchlist');
}

export async function fetchHoldings(): Promise<HoldingItem[]> {
  const response = await fetch(`${API_BASE}/api/holdings`);
  if (!response.ok) throw new Error('Failed to fetch holdings');
  return response.json() as Promise<HoldingItem[]>;
}

export async function addHolding(symbol: string, quantity: number, averageCost: number): Promise<void> {
  const response = await fetch(`${API_BASE}/api/holdings`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ symbol, quantity, average_cost: averageCost }),
  });
  if (!response.ok) throw new Error('Failed to add holding');
}
```

- [ ] **Step 2: Write failing frontend tests**

Update `frontend/tests/dashboard.test.tsx` with a test for add-ticker form and holdings section.

- [ ] **Step 3: Update DashboardShell.tsx**

Add:
- "Add Ticker" form (text input + button) at top of watchlist section
- Holdings section in the right sidebar
- Remove button on watchlist cards

- [ ] **Step 4: Run frontend tests**

Run: `cd frontend && npm test -- --run`

Expected: all tests pass.

- [ ] **Step 5: Run frontend build**

Run: `cd frontend && npm run build`

Expected: build succeeds.

## Task 6: Final Verification

- [ ] **Step 1: Run all backend tests**

Run: `cd backend && uv run pytest -q`

Expected: all pass.

- [ ] **Step 2: Run backend lint**

Run: `cd backend && uv run ruff check app tests`

Expected: all checks passed.

- [ ] **Step 3: Run backend typecheck**

Run: `cd backend && uv run mypy app`

Expected: no issues found.

- [ ] **Step 4: Run all frontend checks**

Run: `cd frontend && npm test -- --run && npm run lint && npm run build`

Expected: all pass.

- [ ] **Step 5: Run gitleaks**

Run: `cd /home/digitalghost/projects/equity-lens && gitleaks detect --source . --no-git --config .gitleaks.toml`

Expected: no leaks found.
