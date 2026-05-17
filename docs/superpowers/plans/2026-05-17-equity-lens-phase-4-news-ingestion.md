# Equity Lens Phase 4: News Ingestion Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add financial news ingestion, storage, and display for watched tickers.

**Architecture:** A `NewsArticle` DB model stores fetched news. `YFinanceNewsProvider` uses yfinance's `ticker.news` (no API key needed). A news ingestion scheduler polls for watchlist tickers and stores deduplicated articles. News API endpoints serve per-ticker and aggregated feeds. The frontend displays recent news in the dashboard.

**Tech Stack:** Python, yfinance (already installed), SQLAlchemy, FastAPI, Next.js.

---

## File Structure Changes

```
backend/
  app/
    domain/
      db_models.py                         # + NewsArticle model
    providers/
      news_base.py                         # NEW: NewsProvider protocol
      yfinance_news.py                     # NEW: yfinance news provider
    api/
      news_routes.py                       # NEW: news API endpoints
      watchlist_routes.py                  # MODIFY: include latest news count
    core/
      scheduler.py                         # MODIFY: add poll_watchlist_news
  tests/
    test_news_models.py                    # NEW: DB model tests
    test_news_provider.py                  # NEW: provider tests
    test_news_routes.py                    # NEW: API endpoint tests
frontend/
  src/
    lib/
      api.ts                              # MODIFY: add fetchNews type/function
    components/
      DashboardShell.tsx                   # MODIFY: add news feed to watchlist cards
  tests/
    dashboard.test.tsx                     # MODIFY: update expectations
```

## Task 1: NewsArticle DB Model

**Files:**
- Modify: `backend/app/domain/db_models.py`
- Create: `backend/tests/test_news_models.py`

- [ ] **Step 1: Write failing news model test**

Create `backend/tests/test_news_models.py`:

```python
"""Tests for NewsArticle model."""
import pytest
from datetime import datetime, timezone
from sqlalchemy import select
from app.domain.db_models import NewsArticle


@pytest.mark.asyncio
async def test_news_article_round_trip(async_db_session):
    article = NewsArticle(
        symbol='AAPL',
        title='Apple reports record quarterly results',
        url='https://example.com/apple-earnings',
        source='Yahoo Finance',
        summary='Apple reported strong Q2 earnings...',
        published_at=datetime(2025, 3, 15, tzinfo=timezone.utc),
    )
    async_db_session.add(article)
    await async_db_session.commit()

    result = await async_db_session.execute(
        select(NewsArticle).where(NewsArticle.symbol == 'AAPL')
    )
    saved = result.scalar_one()
    assert saved.title == 'Apple reports record quarterly results'
    assert saved.url == 'https://example.com/apple-earnings'


@pytest.mark.asyncio
async def test_news_article_deduplicates_by_url(async_db_session):
    article1 = NewsArticle(
        symbol='AAPL',
        title='First',
        url='https://example.com/same',
        published_at=datetime(2025, 3, 15, tzinfo=timezone.utc),
    )
    article2 = NewsArticle(
        symbol='AAPL',
        title='Second',
        url='https://example.com/same',
        published_at=datetime(2025, 3, 15, tzinfo=timezone.utc),
    )
    async_db_session.add(article1)
    await async_db_session.commit()

    # Verify URL uniqueness constraint
    async_db_session.add(article2)
    with pytest.raises(Exception):
        await async_db_session.commit()
    await async_db_session.rollback()
```

- [ ] **Step 2: Run tests to verify failure**

Run: `cd backend && uv run pytest tests/test_news_models.py -q`

Expected: FAIL (NewsArticle model doesn't exist).

- [ ] **Step 3: Add NewsArticle to db_models.py**

Add after the existing models:

```python
class NewsArticle(Base):
    __tablename__ = 'news_articles'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    symbol: Mapped[str] = mapped_column(String(10), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    url: Mapped[str] = mapped_column(String(2048), unique=True, nullable=False)
    source: Mapped[str] = mapped_column(String(100), default='')
    summary: Mapped[str] = mapped_column(String(5000), default='')
    sentiment: Mapped[float] = mapped_column(Float, default=0.0)
    relevance_score: Mapped[float] = mapped_column(Float, default=0.0)
    event_type: Mapped[str] = mapped_column(String(50), default='')
    published_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
```

- [ ] **Step 4: Run tests to verify pass**

Run: `cd backend && uv run pytest tests/test_news_models.py -q`

Expected: 2 passed.

## Task 2: News Provider Protocol and YFinance Implementation

**Files:**
- Create: `backend/app/providers/news_base.py`
- Create: `backend/app/providers/yfinance_news.py`
- Create: `backend/tests/test_news_provider.py`

- [ ] **Step 1: Write failing news provider tests**

Create `backend/tests/test_news_provider.py`:

```python
"""Tests for news providers."""
import pytest
from app.domain.models import TickerSymbol
from app.providers.yfinance_news import YFinanceNewsProvider


def test_yfinance_news_returns_articles_for_ticker():
    provider = YFinanceNewsProvider()
    articles = provider.fetch_news(TickerSymbol(value='AAPL'), max_results=3)
    assert len(articles) > 0
    for article in articles:
        assert 'title' in article
        assert 'url' in article
        assert 'source' in article
        assert 'published_at' in article
```

- [ ] **Step 2: Run tests to verify failure**

Run: `cd backend && uv run pytest tests/test_news_provider.py -q`

Expected: FAIL (modules don't exist).

- [ ] **Step 3: Create news provider protocol**

Create `backend/app/providers/news_base.py`:

```python
"""News provider protocol and data model."""
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Protocol

from app.domain.models import TickerSymbol


@dataclass
class NewsItem:
    title: str
    url: str
    source: str
    summary: str
    published_at: datetime


class NewsProvider(Protocol):
    def fetch_news(self, symbol: TickerSymbol, max_results: int = 10) -> list[dict[str, Any]]: ...
```

- [ ] **Step 4: Create yfinance news provider**

Create `backend/app/providers/yfinance_news.py`:

```python
"""News provider using yfinance ticker news."""
from datetime import datetime, timezone
from typing import Any

import yfinance as yf

from app.domain.models import TickerSymbol


class YFinanceNewsProvider:
    provider_name = 'yfinance'

    def fetch_news(self, symbol: TickerSymbol, max_results: int = 10) -> list[dict[str, Any]]:
        ticker = yf.Ticker(symbol.value)
        news = getattr(ticker, 'news', []) or []
        results: list[dict[str, Any]] = []
        for item in news[:max_results]:
            content = item.get('content', item)
            title = content.get('title', '')
            url = content.get('canonicalUrl', {}).get('url', '') if isinstance(content.get('canonicalUrl'), dict) else content.get('link', '')
            source = content.get('provider', {}).get('displayName', 'Yahoo Finance') if isinstance(content.get('provider'), dict) else 'Yahoo Finance'
            summary = content.get('summary', '') or content.get('description', '') or ''
            pub_time = content.get('pubDate', 0)
            if isinstance(pub_time, (int, float)):
                published_at = datetime.fromtimestamp(pub_time, tz=timezone.utc)
            else:
                published_at = datetime.now(timezone.utc)

            if title and url:
                results.append({
                    'title': title,
                    'url': url,
                    'source': source,
                    'summary': summary,
                    'published_at': published_at,
                })
        return results
```

- [ ] **Step 5: Run provider tests**

Run: `cd backend && uv run pytest tests/test_news_provider.py -q`

Expected: test passes (may require network for yfinance).

## Task 3: News Ingestion Scheduler

**Files:**
- Modify: `backend/app/core/scheduler.py`
- Create: `backend/tests/test_news_scheduler.py`

- [ ] **Step 1: Write failing news scheduler test**

Create `backend/tests/test_news_scheduler.py`:

```python
"""Tests for news ingestion scheduler."""
import pytest
from app.core.scheduler import poll_watchlist_news


@pytest.mark.asyncio
async def test_poll_news_returns_zero_for_empty_watchlist(async_db_session):
    result = await poll_watchlist_news(get_session=lambda: async_db_session)
    assert result == 0
```

- [ ] **Step 2: Run tests to verify failure**

Run: `cd backend && uv run pytest tests/test_news_scheduler.py -q`

Expected: FAIL (poll_watchlist_news doesn't exist).

- [ ] **Step 3: Add news polling to scheduler.py**

Add to `backend/app/core/scheduler.py`:

```python
async def poll_watchlist_news(
    get_session=None,
) -> int:
    """Fetch news for all watchlist entries and store new articles."""
    from app.providers.yfinance_news import YFinanceNewsProvider
    from app.domain.db_models import NewsArticle

    provider = YFinanceNewsProvider()

    if get_session is not None:
        session = get_session()
        return await _do_poll_news(session, provider)

    from app.core.db import _async_session_factory
    if _async_session_factory is None:
        from app.core.db import init_db
        await init_db()
    assert _async_session_factory is not None
    async with _async_session_factory() as session:
        return await _do_poll_news(session, provider)


async def _do_poll_news(session, provider) -> int:
    from app.domain.models import TickerSymbol
    from app.domain.db_models import NewsArticle

    result = await session.execute(
        select(WatchlistEntry.symbol)
    )
    symbols = [row[0] for row in result.all()]

    count = 0
    for symbol in symbols:
        try:
            ts = TickerSymbol(value=symbol)
            articles = provider.fetch_news(ts, max_results=5)
            for article in articles:
                existing = await session.execute(
                    select(NewsArticle).where(NewsArticle.url == article['url'])
                )
                if existing.scalar_one_or_none() is not None:
                    continue
                news_item = NewsArticle(
                    symbol=symbol,
                    title=article['title'],
                    url=article['url'],
                    source=article['source'],
                    summary=article['summary'],
                    published_at=article['published_at'],
                )
                session.add(news_item)
                count += 1
        except Exception as e:
            import logging
            logging.getLogger(__name__).warning('Failed to fetch news for %s: %s', symbol, e)
    await session.commit()
    return count
```

- [ ] **Step 4: Run news scheduler tests**

Run: `cd backend && uv run pytest tests/test_news_scheduler.py -q`

Expected: test passes.

## Task 4: News API Endpoints

**Files:**
- Create: `backend/app/api/news_routes.py`
- Modify: `backend/app/api/routes.py`
- Create: `backend/tests/test_news_routes.py`

- [ ] **Step 1: Write failing news route test**

Create `backend/tests/test_news_routes.py`:

```python
"""Tests for news API endpoints."""
from httpx import AsyncClient, ASGITransport
import pytest
from app.main import app


@pytest.fixture
async def client() -> AsyncClient:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url='http://test') as ac:
        yield ac


@pytest.mark.asyncio
async def test_get_news_for_watched_symbol(client: AsyncClient):
    await client.post('/api/watchlist', json={'symbol': 'AAPL'})
    response = await client.get('/api/news/AAPL')
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_get_news_for_unwatched_symbol_returns_404(client: AsyncClient):
    response = await client.get('/api/news/ZZZZ')
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_aggregated_news(client: AsyncClient):
    await client.post('/api/watchlist', json={'symbol': 'AAPL'})
    response = await client.get('/api/news')
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
```

- [ ] **Step 2: Run tests to verify failure**

Run: `cd backend && uv run pytest tests/test_news_routes.py -q`

Expected: 2 pass (404 for unwatched), 1 fails (route missing).

- [ ] **Step 3: Create news routes**

Create `backend/app/api/news_routes.py`:

```python
"""News API endpoints."""
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_session
from app.domain.db_models import NewsArticle, WatchlistEntry

router = APIRouter(prefix='/news', tags=['news'])


@router.get('')
async def get_all_news(
    session: AsyncSession = Depends(get_session),
) -> list[dict[str, Any]]:
    result = await session.execute(
        select(NewsArticle).order_by(NewsArticle.published_at.desc()).limit(50)
    )
    return [_article_to_dict(a) for a in result.scalars().all()]


@router.get('/{symbol}')
async def get_symbol_news(
    symbol: str,
    session: AsyncSession = Depends(get_session),
) -> list[dict[str, Any]]:
    sym = symbol.upper()
    entry = await session.execute(
        select(WatchlistEntry).where(WatchlistEntry.symbol == sym)
    )
    if entry.scalar_one_or_none() is None:
        raise HTTPException(status_code=404, detail=f'{sym} not in watchlist')

    result = await session.execute(
        select(NewsArticle)
        .where(NewsArticle.symbol == sym)
        .order_by(NewsArticle.published_at.desc())
        .limit(25)
    )
    return [_article_to_dict(a) for a in result.scalars().all()]


def _article_to_dict(a: NewsArticle) -> dict[str, Any]:
    return {
        'id': a.id,
        'symbol': a.symbol,
        'title': a.title,
        'url': a.url,
        'source': a.source,
        'summary': a.summary,
        'published_at': a.published_at.isoformat() if a.published_at else None,
    }
```

- [ ] **Step 4: Register news routes in routes.py**

Add to `backend/app/api/routes.py`:

```python
from app.api.news_routes import router as news_router
router.include_router(news_router)
```

- [ ] **Step 5: Run news route tests**

Run: `cd backend && uv run pytest tests/test_news_routes.py -q`

Expected: all 3 tests pass.

## Task 5: Frontend News Display

**Files:**
- Modify: `frontend/src/lib/api.ts`
- Modify: `frontend/src/components/DashboardShell.tsx`
- Modify: `frontend/tests/dashboard.test.tsx`

- [ ] **Step 1: Update API types**

Add to `frontend/src/lib/api.ts`:

```typescript
export interface NewsArticle {
  id: number;
  symbol: string;
  title: string;
  url: string;
  source: string;
  summary: string;
  published_at: string | null;
}

export async function fetchNews(symbol?: string): Promise<NewsArticle[]> {
  const url = symbol
    ? `${API_BASE}/api/news/${symbol}`
    : `${API_BASE}/api/news`;
  const response = await fetch(url);
  if (!response.ok) throw new Error('Failed to fetch news');
  return response.json() as Promise<NewsArticle[]>;
}
```

- [ ] **Step 2: Update DashboardShell.tsx**

Add a news section that shows recent articles per ticker or an aggregated feed. Each card shows: title, source, relative time.

- [ ] **Step 3: Update frontend tests**

Add tests for news section rendering.

- [ ] **Step 4: Run frontend verification**

Run: `cd frontend && npm test -- --run && npm run lint && npm run build`

Expected: all pass.

## Task 6: Final Verification

- [ ] **Run all backend tests**: `cd backend && uv run pytest -q`
- [ ] **Run backend lint**: `cd backend && uv run ruff check app tests`
- [ ] **Run backend typecheck**: `cd backend && uv run mypy app`
- [ ] **Run all frontend checks**: `cd frontend && npm test -- --run && npm run lint && npm run build`
- [ ] **Run gitleaks**: `gitleaks detect --source . --no-git --config .gitleaks.toml`
