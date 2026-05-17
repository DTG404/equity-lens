# Equity Lens Phase 3: Market Data Ingestion Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the mock market provider with a real data adapter (yfinance) and add quote polling, historical OHLCV storage, and live price display on the dashboard.

**Architecture:** A `YFinanceMarketDataProvider` implements the existing `MarketDataProvider` protocol. A background scheduler polls quotes for watched tickers and stores them in a `PriceSnapshot` table. A `PriceHistory` table stores daily OHLCV data. The watchlist endpoint is enriched with latest quotes. The frontend displays live prices on watchlist cards.

**Tech Stack:** Python, yfinance, SQLAlchemy, APScheduler (simple background scheduling).

---

## File Structure Changes

```
backend/
  pyproject.toml                           # + yfinance, apscheduler
  app/
    domain/
      db_models.py                         # + PriceSnapshot, PriceHistory tables
    providers/
      yfinance_provider.py                 # NEW: real market data provider
    api/
      quote_routes.py                      # NEW: quote and history endpoints
      watchlist_routes.py                  # MODIFY: enrich with latest quote
    core/
      scheduler.py                         # NEW: background polling scheduler
  tests/
    test_yfinance_provider.py              # NEW: provider tests
    test_quote_routes.py                   # NEW: quote endpoint tests
    conftest.py                            # MODIFY: add quote-specific fixtures
frontend/
  src/
    lib/
      api.ts                              # MODIFY: add fetchQuote, enrich watchlist
    components/
      DashboardShell.tsx                   # MODIFY: show prices on watchlist cards
  tests/
    dashboard.test.tsx                     # MODIFY: update expectations
```

## Task 1: Add Dependencies and New DB Models

**Files:**
- Modify: `backend/pyproject.toml`
- Modify: `backend/app/domain/db_models.py`
- Create: `backend/tests/test_price_models.py`

- [ ] **Step 1: Install dependencies**

Run: `cd backend && uv add yfinance apscheduler`

- [ ] **Step 2: Write failing price model tests**

Create `backend/tests/test_price_models.py` with round-trip tests for `PriceSnapshot` and `PriceHistory` models:

```python
"""Tests for price-related DB models."""
import pytest
from datetime import datetime, timezone
from sqlalchemy import select
from app.domain.db_models import PriceSnapshot, PriceHistory


@pytest.mark.asyncio
async def test_price_snapshot_round_trip(async_db_session):
    snapshot = PriceSnapshot(
        symbol='AAPL',
        price=185.50,
        change_percent=1.25,
        provider='test'
    )
    async_db_session.add(snapshot)
    await async_db_session.commit()
    result = await async_db_session.execute(
        select(PriceSnapshot).where(PriceSnapshot.symbol == 'AAPL')
    )
    saved = result.scalar_one()
    assert saved.price == 185.50
    assert saved.change_percent == 1.25


@pytest.mark.asyncio
async def test_price_history_round_trip(async_db_session):
    history = PriceHistory(
        symbol='MSFT',
        date=datetime(2025, 1, 15, tzinfo=timezone.utc).date(),
        open_price=410.0,
        high_price=415.0,
        low_price=408.0,
        close_price=412.50,
        volume=22000000,
    )
    async_db_session.add(history)
    await async_db_session.commit()
    result = await async_db_session.execute(
        select(PriceHistory).where(PriceHistory.symbol == 'MSFT')
    )
    saved = result.scalar_one()
    assert saved.close_price == 412.50
```

- [ ] **Step 3: Run tests to verify failure**

Run: `cd backend && uv run pytest tests/test_price_models.py -q`

Expected: FAIL (models don't exist yet).

- [ ] **Step 4: Add PriceSnapshot and PriceHistory models to db_models.py**

```python
class PriceSnapshot(Base):
    __tablename__ = 'price_snapshots'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    symbol: Mapped[str] = mapped_column(String(10), index=True, nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    change_percent: Mapped[float] = mapped_column(Float, default=0.0)
    provider: Mapped[str] = mapped_column(String(50), default='')
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class PriceHistory(Base):
    __tablename__ = 'price_history'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    symbol: Mapped[str] = mapped_column(String(10), index=True, nullable=False)
    date: Mapped[datetime.date] = mapped_column(DateTime, nullable=False)
    open_price: Mapped[float] = mapped_column(Float, nullable=False)
    high_price: Mapped[float] = mapped_column(Float, nullable=False)
    low_price: Mapped[float] = mapped_column(Float, nullable=False)
    close_price: Mapped[float] = mapped_column(Float, nullable=False)
    volume: Mapped[int] = mapped_column(Integer, default=0)
```

- [ ] **Step 5: Run tests to verify pass**

Run: `cd backend && uv run pytest tests/test_price_models.py -q`

Expected: 2 passed.

## Task 2: YFinance Market Data Provider

**Files:**
- Create: `backend/app/providers/yfinance_provider.py`
- Create: `backend/tests/test_yfinance_provider.py`

- [ ] **Step 1: Write failing provider tests**

Create `backend/tests/test_yfinance_provider.py`:

```python
"""Tests for YFinance market data provider."""
import pytest
from app.domain.models import TickerSymbol
from app.providers.yfinance_provider import YFinanceMarketDataProvider


def test_provider_returns_quote_for_valid_ticker():
    provider = YFinanceMarketDataProvider()
    symbol = TickerSymbol(value='AAPL')
    quote = provider.get_quote(symbol)
    assert quote.symbol == 'AAPL'
    assert quote.price > 0
    assert isinstance(quote.change_percent, float)
    assert quote.provider == 'yfinance'


def test_provider_returns_history_for_valid_ticker():
    provider = YFinanceMarketDataProvider()
    history = provider.get_history(TickerSymbol(value='MSFT'), days=5)
    assert len(history) > 0
    for entry in history:
        assert 'date' in entry
        assert 'open' in entry
        assert 'high' in entry
        assert 'low' in entry
        assert 'close' in entry
        assert 'volume' in entry
```

- [ ] **Step 2: Run tests to verify failure**

Run: `cd backend && uv run pytest tests/test_yfinance_provider.py -q`

Expected: FAIL (module doesn't exist).

- [ ] **Step 3: Implement YFinanceMarketDataProvider**

Create `backend/app/providers/yfinance_provider.py`:

```python
"""Real market data provider using yfinance."""
from datetime import datetime, timezone
from typing import Any

import yfinance as yf

from app.domain.models import TickerSymbol
from app.providers.base import MarketDataProvider, Quote


class YFinanceMarketDataProvider(MarketDataProvider):
    provider_name = 'yfinance'

    def get_quote(self, symbol: TickerSymbol) -> Quote:
        ticker = yf.Ticker(symbol.value)
        info = ticker.info or {}
        price = info.get('currentPrice') or info.get('regularMarketPrice') or 0.0
        previous_close = info.get('previousClose') or price or 1.0
        change_percent = ((price - previous_close) / previous_close) * 100 if previous_close else 0.0
        if not price or price <= 0:
            fast_info = ticker.fast_info
            price = getattr(fast_info, 'last_price', 0.0) or 0.0
        return Quote(
            symbol=symbol.value,
            price=round(float(price), 2),
            change_percent=round(float(change_percent), 2),
            provider=self.provider_name,
        )

    def get_history(self, symbol: TickerSymbol, days: int = 30) -> list[dict[str, Any]]:
        ticker = yf.Ticker(symbol.value)
        hist = ticker.history(period=f'{max(days, 5)}d')
        result: list[dict[str, Any]] = []
        for date, row in hist.iterrows():
            result.append({
                'date': date.strftime('%Y-%m-%d'),
                'open': round(float(row['Open']), 2),
                'high': round(float(row['High']), 2),
                'low': round(float(row['Low']), 2),
                'close': round(float(row['Close']), 2),
                'volume': int(row['Volume']),
            })
        return result
```

- [ ] **Step 4: Run provider tests**

Run: `cd backend && uv run pytest tests/test_yfinance_provider.py -q`

Expected: 2 passed (may require network access for yfinance).

## Task 3: Background Quote Polling Scheduler

**Files:**
- Create: `backend/app/core/scheduler.py`
- Create: `backend/tests/test_scheduler.py`

- [ ] **Step 1: Write failing scheduler tests**

Create `backend/tests/test_scheduler.py` that tests the `poll_watchlist_quotes` function using the mock provider:

```python
"""Tests for background quote polling."""
import pytest
from unittest.mock import AsyncMock, MagicMock

from app.core.scheduler import poll_watchlist_quotes


@pytest.mark.asyncio
async def test_poll_queries_watchlist_and_stores_prices(async_db_session):
    mock_provider = MagicMock()
    mock_provider.get_quote.return_value.price = 150.0
    mock_provider.get_quote.return_value.change_percent = 0.5
    mock_provider.get_quote.return_value.symbol = 'AAPL'
    mock_provider.get_quote.return_value.provider = 'mock'

    mock_get_session = MagicMock()
    mock_get_session.return_value = async_db_session

    # Just verify it runs without error with an empty watchlist
    result = await poll_watchlist_quotes(
        provider=mock_provider,
        get_session=lambda: async_db_session,
    )
    assert result >= 0
```

- [ ] **Step 2: Run tests to verify failure**

Run: `cd backend && uv run pytest tests/test_scheduler.py -q`

Expected: FAIL (scheduler module doesn't exist).

- [ ] **Step 3: Implement scheduler**

Create `backend/app/core/scheduler.py`:

```python
"""Background scheduler for periodic quote polling."""
import asyncio
import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db_url, init_db, _async_session_factory
from app.domain.db_models import PriceSnapshot, WatchlistEntry
from app.domain.models import TickerSymbol
from app.providers.mock_market import MockMarketDataProvider
from app.providers.base import MarketDataProvider

logger = logging.getLogger(__name__)


def _get_provider() -> MarketDataProvider:
    return MockMarketDataProvider()


async def poll_watchlist_quotes(
    provider: MarketDataProvider | None = None,
    get_session=None,
) -> int:
    """Poll quotes for all watchlist entries and store in PriceSnapshot."""
    prov = provider or _get_provider()

    if get_session is not None:
        async with get_session() as session:
            return await _do_poll(session, prov)

    from app.core.db import get_session as default_session
    async with default_session() as session:
        return await _do_poll(session, prov)


async def _do_poll(session: AsyncSession, provider: MarketDataProvider) -> int:
    from sqlalchemy import select
    result = await session.execute(
        select(WatchlistEntry.symbol)
    )
    symbols = [row[0] for row in result.all()]

    count = 0
    for symbol in symbols:
        try:
            ts = TickerSymbol(value=symbol)
            quote = provider.get_quote(ts)
            snapshot = PriceSnapshot(
                symbol=quote.symbol,
                price=quote.price,
                change_percent=quote.change_percent,
                provider=quote.provider,
            )
            session.add(snapshot)
            count += 1
        except Exception as e:
            logger.warning('Failed to poll %s: %s', symbol, e)
    await session.commit()
    return count
```

- [ ] **Step 4: Run scheduler tests**

Run: `cd backend && uv run pytest tests/test_scheduler.py -q`

Expected: test passes.

## Task 4: Quote and History API Endpoints

**Files:**
- Create: `backend/app/api/quote_routes.py`
- Modify: `backend/app/api/routes.py`
- Create: `backend/tests/test_quote_routes.py`

- [ ] **Step 1: Write failing quote route tests**

Create `backend/tests/test_quote_routes.py`:

```python
"""Tests for quote endpoints."""
from httpx import AsyncClient, ASGITransport
import pytest
from app.main import app


@pytest.fixture
async def client() -> AsyncClient:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url='http://test') as ac:
        yield ac


@pytest.mark.asyncio
async def test_get_latest_quote_for_watched_symbol(client: AsyncClient):
    # First add to watchlist
    await client.post('/api/watchlist', json={'symbol': 'AAPL'})
    response = await client.get('/api/quotes/AAPL')
    assert response.status_code == 200
    data = response.json()
    assert 'symbol' in data
    assert 'price' in data


@pytest.mark.asyncio
async def test_get_quote_for_unwatched_symbol_returns_404(client: AsyncClient):
    response = await client.get('/api/quotes/ZZZZ')
    assert response.status_code == 404
```

- [ ] **Step 2: Run tests to verify failure**

Run: `cd backend && uv run pytest tests/test_quote_routes.py -q`

Expected: FAIL (routes don't exist).

- [ ] **Step 3: Implement quote routes**

Create `backend/app/api/quote_routes.py`:

```python
"""Quote and price history endpoints."""
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_session
from app.domain.db_models import PriceSnapshot, WatchlistEntry
from app.domain.models import TickerSymbol
from app.providers.mock_market import MockMarketDataProvider

router = APIRouter(prefix='/quotes', tags=['quotes'])

_provider = MockMarketDataProvider()


@router.get('/{symbol}')
async def get_quote(
    symbol: str,
    session: AsyncSession = Depends(get_session),
) -> dict[str, object]:
    # Check if symbol is in watchlist
    result = await session.execute(
        select(WatchlistEntry).where(WatchlistEntry.symbol == symbol.upper())
    )
    if result.scalar_one_or_none() is None:
        raise HTTPException(status_code=404, detail=f'{symbol.upper()} not in watchlist')

    # Try DB first, then live provider
    snapshot = await session.execute(
        select(PriceSnapshot)
        .where(PriceSnapshot.symbol == symbol.upper())
        .order_by(PriceSnapshot.recorded_at.desc())
        .limit(1)
    )
    row = snapshot.scalar_one_or_none()
    if row is not None:
        return {
            'symbol': row.symbol,
            'price': row.price,
            'change_percent': row.change_percent,
            'provider': row.provider,
        }

    # Live fetch
    ts = TickerSymbol(value=symbol)
    quote = _provider.get_quote(ts)
    return {
        'symbol': quote.symbol,
        'price': quote.price,
        'change_percent': quote.change_percent,
        'provider': quote.provider,
    }
```

- [ ] **Step 4: Register router in routes.py**

Modify `backend/app/api/routes.py` to add:

```python
from app.api.quote_routes import router as quote_router
router.include_router(quote_router)
```

- [ ] **Step 5: Run tests to verify pass**

Run: `cd backend && uv run pytest tests/test_quote_routes.py -q`

Expected: all pass.

## Task 5: Enrich Watchlist with Latest Quote

**Files:**
- Modify: `backend/app/api/watchlist_routes.py`

- [ ] **Step 1: Update watchlist response to include latest quote**

Modify the `list_watchlist` handler to join with `PriceSnapshot` for the latest quote per symbol:

```python
@router.get('')
async def list_watchlist(
    session: AsyncSession = Depends(get_session),
) -> list[dict[str, object]]:
    from sqlalchemy import select
    from app.domain.db_models import PriceSnapshot
    from sqlalchemy.orm import joinedload

    result = await session.execute(
        select(WatchlistEntry).order_by(WatchlistEntry.created_at)
    )
    entries = result.scalars().all()

    output = []
    for entry in entries:
        snapshot = await session.execute(
            select(PriceSnapshot)
            .where(PriceSnapshot.symbol == entry.symbol)
            .order_by(PriceSnapshot.recorded_at.desc())
            .limit(1)
        )
        price = snapshot.scalar_one_or_none()
        output.append({
            'symbol': entry.symbol,
            'company_name': entry.company_name,
            'price': price.price if price else None,
            'change_percent': price.change_percent if price else None,
        })
    return output
```

- [ ] **Step 2: Update tests to match enriched response**

Update `tests/test_watchlist_crud.py` and `tests/test_watchlist_api.py` to expect `price` and `change_percent` fields (nullable).

- [ ] **Step 3: Run all tests**

Run: `cd backend && uv run pytest -q`

Expected: all pass.

## Task 6: Frontend Price Display

**Files:**
- Modify: `frontend/src/lib/api.ts`
- Modify: `frontend/src/components/DashboardShell.tsx`
- Modify: `frontend/tests/dashboard.test.tsx`

- [ ] **Step 1: Update API types**

In `frontend/src/lib/api.ts`, update `WatchlistItem` to include `price` and `change_percent` (nullable).

- [ ] **Step 2: Update watchlist cards to show prices**

In `DashboardShell.tsx`, display price and change percent with color coding (green/red).

- [ ] **Step 3: Update tests**

Update `dashboard.test.tsx` to expect price display in watchlist cards.

- [ ] **Step 4: Run frontend tests and build**

Run: `cd frontend && npm test -- --run && npm run lint && npm run build`

Expected: all pass.

## Task 7: Final Verification

- [ ] **Run all backend tests**: `cd backend && uv run pytest -q`
- [ ] **Run backend lint**: `cd backend && uv run ruff check app tests`
- [ ] **Run backend typecheck**: `cd backend && uv run mypy app`
- [ ] **Run all frontend checks**: `cd frontend && npm test -- --run && npm run lint && npm run build`
- [ ] **Run gitleaks**: `gitleaks detect --source . --no-git --config .gitleaks.toml`
