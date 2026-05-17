# Equity Lens Phase 5: Single-Stock Research Page Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a single-stock research page showing price chart, news, factor scores, and generated thesis for any watched ticker.

**Architecture:** A backend research endpoint aggregates quote, price history, recent news, stub factor scores, and a stub thesis. The frontend adds a Next.js route `/stocks/[symbol]` with a dedicated page. A simple SVG line chart renders price history without external dependencies. Dashboard watchlist cards link to the research page.

**Tech Stack:** Python, FastAPI, SVG (inline for chart), Next.js App Router.

---

## File Structure Changes

```
backend/
  app/
    api/
      research_routes.py                # NEW: aggregate research endpoint
    domain/
      scoring.py                        # NEW: stub factor scoring logic
  tests/
    test_research_routes.py             # NEW: research endpoint tests
    test_scoring.py                     # NEW: scoring tests
frontend/
  app/
    stocks/
      [symbol]/
        page.tsx                        # NEW: single-stock research page
    page.tsx                            # MODIFY: link from dashboard
  src/
    lib/
      api.ts                            # MODIFY: add fetchResearch
    components/
      DashboardShell.tsx                 # MODIFY: make cards clickable
      PriceChart.tsx                     # NEW: SVG line chart component
      FactorScoreCard.tsx                # NEW: factor score display
```

## Task 1: Factor Scoring Stub

**Files:**
- Create: `backend/app/domain/scoring.py`
- Create: `backend/tests/test_scoring.py`

- [ ] **Step 1: Write failing scoring test**

Create `backend/tests/test_scoring.py`:

```python
"""Tests for stub factor scoring."""
from app.domain.models import TickerSymbol
from app.domain.scoring import compute_factor_scores


def test_compute_scores_returns_all_factors():
    scores = compute_factor_scores(TickerSymbol(value='AAPL'))
    assert 'technical' in scores
    assert 'news_sentiment' in scores
    assert 'fundamentals' in scores
    assert 'macro' in scores
    assert 'overall' in scores
    for key in ('technical', 'news_sentiment', 'fundamentals', 'macro'):
        assert 0.0 <= scores[key]['score'] <= 1.0
        assert len(scores[key]['explanation']) > 0
    assert 0.0 <= scores['overall'] <= 1.0
```

- [ ] **Step 2: Run to verify failure**

Run: `cd backend && uv run pytest tests/test_scoring.py -q`

Expected: FAIL.

- [ ] **Step 3: Implement scoring**

Create `backend/app/domain/scoring.py`:

```python
"""Stub factor scoring for MVP. Real scoring comes in Phase 6 with DeepSeek."""
import math
from app.domain.models import TickerSymbol


def compute_factor_scores(symbol: TickerSymbol) -> dict:
    """Return deterministic factor scores based on the ticker symbol hash.
    
    Phase 6 will replace this with real multi-factor scoring + DeepSeek.
    """
    seed = sum(ord(c) for c in symbol.value)
    rng = _seeded_random(seed)

    technical_score = rng[0] * 0.3 + 0.5  # 0.5-0.8 range
    news_score = rng[1] * 0.4 + 0.3       # 0.3-0.7 range
    fundamental_score = rng[2] * 0.3 + 0.4  # 0.4-0.7 range
    macro_score = rng[3] * 0.2 + 0.4      # 0.4-0.6 range

    overall = (
        technical_score * 0.3
        + news_score * 0.25
        + fundamental_score * 0.25
        + macro_score * 0.2
    )

    return {
        'technical': {
            'score': round(technical_score, 2),
            'explanation': 'Based on recent price momentum and volume trends.'
        },
        'news_sentiment': {
            'score': round(news_score, 2),
            'explanation': 'Aggregated sentiment from recent news coverage.'
        },
        'fundamentals': {
            'score': round(fundamental_score, 2),
            'explanation': 'Valuation metrics and earnings trajectory.'
        },
        'macro': {
            'score': round(macro_score, 2),
            'explanation': 'Sector and macroeconomic conditions.'
        },
        'overall': round(overall, 2),
    }


def _seeded_random(seed: int) -> list[float]:
    """Simple deterministic pseudo-random for reproducible scoring."""
    results = []
    for i in range(4):
        h = (seed * 1103515245 + (i * 12345)) & 0x7fffffff
        results.append(h / 0x7fffffff)
    return results
```

- [ ] **Step 4: Run tests**

Run: `cd backend && uv run pytest tests/test_scoring.py -q`

Expected: 1 passed.

## Task 2: Research Aggregate Endpoint

**Files:**
- Create: `backend/app/api/research_routes.py`
- Modify: `backend/app/api/routes.py`
- Create: `backend/tests/test_research_routes.py`

- [ ] **Step 1: Write failing research route test**

Create `backend/tests/test_research_routes.py`:

```python
"""Tests for research aggregate endpoint."""
from httpx import AsyncClient, ASGITransport
import pytest
from app.main import app


@pytest.fixture
async def client() -> AsyncClient:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url='http://test') as ac:
        yield ac


@pytest.mark.asyncio
async def test_research_returns_aggregated_data(client: AsyncClient):
    await client.post('/api/watchlist', json={'symbol': 'AAPL'})
    response = await client.get('/api/research/AAPL')
    assert response.status_code == 200
    data = response.json()
    assert 'symbol' in data
    assert 'quote' in data
    assert 'price_history' in data
    assert 'news' in data
    assert 'scores' in data
    assert 'thesis' in data
    assert 'risks' in data
    assert data['symbol'] == 'AAPL'


@pytest.mark.asyncio
async def test_research_for_unwatched_returns_404(client: AsyncClient):
    response = await client.get('/api/research/ZZZZ')
    assert response.status_code == 404
```

- [ ] **Step 2: Run to verify failure**

Run: `cd backend && uv run pytest tests/test_research_routes.py -q`

Expected: 1 fails (route missing), 1 passes (404 from FastAPI).

- [ ] **Step 3: Create research routes**

Create `backend/app/api/research_routes.py`:

```python
"""Research aggregate endpoint for single-stock analysis page."""
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_session
from app.domain.db_models import NewsArticle, PriceHistory, PriceSnapshot, WatchlistEntry
from app.domain.models import TickerSymbol
from app.domain.scoring import compute_factor_scores
from app.providers.yfinance_provider import YFinanceMarketDataProvider

router = APIRouter(prefix='/research', tags=['research'])

_provider = YFinanceMarketDataProvider()


@router.get('/{symbol}')
async def get_research(
    symbol: str,
    session: AsyncSession = Depends(get_session),
) -> dict[str, Any]:
    sym = symbol.upper()
    result = await session.execute(
        select(WatchlistEntry).where(WatchlistEntry.symbol == sym)
    )
    if result.scalar_one_or_none() is None:
        raise HTTPException(status_code=404, detail=f'{sym} not in watchlist')

    ts = TickerSymbol(value=sym)

    # 1. Quote from DB or live
    snapshot = await session.execute(
        select(PriceSnapshot)
        .where(PriceSnapshot.symbol == sym)
        .order_by(PriceSnapshot.recorded_at.desc())
        .limit(1)
    )
    row = snapshot.scalar_one_or_none()
    if row is not None:
        quote = {'symbol': row.symbol, 'price': row.price, 'change_percent': row.change_percent, 'provider': row.provider}
    else:
        q = _provider.get_quote(ts)
        quote = {'symbol': q.symbol, 'price': q.price, 'change_percent': q.change_percent, 'provider': q.provider}

    # 2. Price history
    history_result = await session.execute(
        select(PriceHistory)
        .where(PriceHistory.symbol == sym)
        .order_by(PriceHistory.date.desc())
        .limit(90)
    )
    price_history = [
        {
            'date': h.date.isoformat() if hasattr(h.date, 'isoformat') else str(h.date),
            'open': h.open_price, 'high': h.high_price,
            'low': h.low_price, 'close': h.close_price, 'volume': h.volume,
        }
        for h in reversed(list(history_result.scalars().all()))
    ]

    # If no history in DB, fetch live
    if not price_history:
        live_history = _provider.get_history(ts, days=30)
        price_history = [
            {'date': e['date'], 'close': e['close'],
             'open': e['open'], 'high': e['high'],
             'low': e['low'], 'volume': e['volume']}
            for e in live_history
        ]

    # 3. News for this symbol
    news_result = await session.execute(
        select(NewsArticle)
        .where(NewsArticle.symbol == sym)
        .order_by(NewsArticle.published_at.desc())
        .limit(10)
    )
    news_items = [
        {
            'id': a.id, 'title': a.title, 'url': a.url,
            'source': a.source, 'summary': a.summary,
            'published_at': a.published_at.isoformat() if a.published_at else None,
        }
        for a in news_result.scalars().all()
    ]

    # 4. Factor scores (stub — Phase 6 replaces with real scoring)
    scores = compute_factor_scores(ts)
    overall = scores['overall']
    if overall >= 0.65:
        stance = 'bullish'
    elif overall >= 0.45:
        stance = 'neutral'
    else:
        stance = 'bearish'

    # 5. Thesis (stub — Phase 6 replaces with DeepSeek synthesis)
    thesis = (
        f"{sym} shows a {stance} outlook with a composite score of "
        f"{overall:.0%}. Technical indicators are "
        f"{'favorable' if scores['technical']['score'] >= 0.5 else 'cautious'}, "
        f"and news sentiment is "
        f"{'positive' if scores['news_sentiment']['score'] >= 0.5 else 'mixed'}. "
        f"Phase 6 will replace this stub with AI-generated analysis."
    )

    risks = (
        "Key risks include sector headwinds, macroeconomic uncertainty, "
        "and company-specific execution risk."
    )

    return {
        'symbol': sym,
        'quote': quote,
        'price_history': price_history,
        'news': news_items,
        'scores': scores,
        'thesis': thesis,
        'risks': risks,
    }
```

- [ ] **Step 4: Register router in routes.py**

Add to `backend/app/api/routes.py`:
```python
from app.api.research_routes import router as research_router
router.include_router(research_router)
```

- [ ] **Step 5: Run tests**

Run: `cd backend && uv run pytest tests/test_research_routes.py -q`

Expected: 2 passed.

## Task 3: Frontend Research Page

**Files:**
- Create: `frontend/app/stocks/[symbol]/page.tsx`
- Create: `frontend/src/components/PriceChart.tsx`
- Create: `frontend/src/components/FactorScoreCard.tsx`
- Modify: `frontend/src/lib/api.ts`
- Modify: `frontend/src/components/DashboardShell.tsx`

- [ ] **Step 1: Update API types**

Add to `frontend/src/lib/api.ts`:

```typescript
export interface FactorScore {
  score: number;
  explanation: string;
}

export interface ResearchData {
  symbol: string;
  quote: {
    symbol: string;
    price: number;
    change_percent: number;
    provider: string;
  } | null;
  price_history: Array<{
    date: string;
    open: number;
    high: number;
    low: number;
    close: number;
    volume: number;
  }>;
  news: NewsArticle[];
  scores: {
    technical: FactorScore;
    news_sentiment: FactorScore;
    fundamentals: FactorScore;
    macro: FactorScore;
    overall: number;
  };
  thesis: string;
  risks: string;
}

export async function fetchResearch(symbol: string): Promise<ResearchData> {
  const response = await fetch(`${API_BASE}/api/research/${symbol}`);
  if (!response.ok) throw new Error('Failed to fetch research data');
  return response.json() as Promise<ResearchData>;
}
```

- [ ] **Step 2: Create PriceChart component**

Create `frontend/src/components/PriceChart.tsx` — an SVG line chart component that takes an array of {date, close} points and renders a responsive chart with axis labels.

- [ ] **Step 3: Create FactorScoreCard component**

Create `frontend/src/components/FactorScoreCard.tsx` — displays score bars for each factor with label, score percentage, and explanation.

- [ ] **Step 4: Create research page**

Create `frontend/app/stocks/[symbol]/page.tsx` — the single-stock research page that:
- Fetches research data on mount
- Shows header with symbol, price, change percent
- Renders PriceChart with close prices
- Shows news feed
- Shows factor scores with FactorScoreCard
- Shows generated thesis
- Shows risks section
- Has a "Back to Dashboard" link
- Includes safety disclaimer

- [ ] **Step 5: Make dashboard cards link to research page**

Update `frontend/src/components/DashboardShell.tsx` so each watchlist card's symbol links to `/stocks/{symbol}` using Next.js `<Link>`.

- [ ] **Step 6: Update frontend tests**

Create `frontend/tests/research-page.test.tsx` with tests for:
- Research page renders symbol header
- Price chart renders
- Factor scores display
- Thesis section renders

- [ ] **Step 7: Run frontend verification**

Run: `cd frontend && npm test -- --run && npm run lint && npm run build`

Expected: all pass.

## Task 4: Final Verification

- [ ] **Run all backend tests**: `cd backend && uv run pytest -q`
- [ ] **Run backend lint**: `cd backend && uv run ruff check app tests`
- [ ] **Run backend typecheck**: `cd backend && uv run mypy app`
- [ ] **Run all frontend checks**: `cd frontend && npm test -- --run && npm run lint && npm run build`
- [ ] **Run gitleaks**: `gitleaks detect --source . --no-git --config .gitleaks.toml`
