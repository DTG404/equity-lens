# Equity Lens Phase 8: Signal Outcome Tracking Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Track prediction outcomes by comparing past analysis stances against actual price movements after 1d, 1w, and 1m windows.

**Architecture:** A background evaluation function checks past analyses against current PriceSnapshot data, creates SignalOutcome records, and computes accuracy metrics. A metrics endpoint serves aggregate stats (accuracy, average return, counts). The frontend shows outcome history on the research page and dashboard.

**Tech Stack:** Python, FastAPI, SQLAlchemy, Next.js.

---

## File Structure Changes

```
backend/
  app/
    domain/
      db_models.py                         # + SignalOutcome model
    api/
      signals_routes.py                    # NEW: outcome history + metrics endpoints
    core/
      scheduler.py                         # MODIFY: add evaluate_signal_outcomes
  tests/
    test_signal_models.py                  # NEW: model tests
    test_signal_evaluation.py              # NEW: evaluation logic tests
    test_signal_routes.py                  # NEW: API endpoint tests
frontend/
  src/
    lib/
      api.ts                              # MODIFY: add signal outcome types + functions
    components/
      SignalHistory.tsx                    # NEW: outcome history component
      DashboardShell.tsx                   # MODIFY: add signal metrics section
      ResearchPage.tsx (page.tsx)          # MODIFY: show signal history for this ticker
  tests/
    dashboard.test.tsx                     # MODIFY: update for signal metrics
    research-page.test.tsx                 # MODIFY: update for signal history
```

## Task 1: SignalOutcome DB Model

**Files:**
- Modify: `backend/app/domain/db_models.py`
- Create: `backend/tests/test_signal_models.py`

- [ ] **Step 1: Write failing model test**

Create `backend/tests/test_signal_models.py` with round-trip tests for `SignalOutcome`.

```python
"""Tests for SignalOutcome model."""
import pytest
from datetime import datetime, timezone
from sqlalchemy import select
from app.domain.db_models import SignalOutcome


@pytest.mark.asyncio
async def test_signal_outcome_round_trip(async_db_session):
    outcome = SignalOutcome(
        symbol='AAPL',
        analysis_id=1,
        stance='bullish',
        confidence=0.75,
        price_at_analysis=180.0,
        window='1d',
        price_at_check=185.0,
        return_pct=2.78,
        correct=True,
    )
    async_db_session.add(outcome)
    await async_db_session.commit()

    result = await async_db_session.execute(
        select(SignalOutcome).where(SignalOutcome.symbol == 'AAPL')
    )
    saved = result.scalar_one()
    assert saved.stance == 'bullish'
    assert saved.correct is True
    assert saved.return_pct == 2.78


@pytest.mark.asyncio
async def test_signal_outcome_defaults(async_db_session):
    outcome = SignalOutcome(
        symbol='MSFT',
        analysis_id=2,
        stance='neutral',
        confidence=0.5,
        price_at_analysis=400.0,
        window='1w',
    )
    async_db_session.add(outcome)
    await async_db_session.commit()
    assert outcome.correct is False
    assert outcome.return_pct == 0.0
```

- [ ] **Step 2: Run to verify failure**

Run: `cd backend && uv run pytest tests/test_signal_models.py -q`

Expected: FAIL.

- [ ] **Step 3: Add SignalOutcome model**

```python
class SignalOutcome(Base):
    __tablename__ = 'signal_outcomes'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    symbol: Mapped[str] = mapped_column(String(10), index=True, nullable=False)
    analysis_id: Mapped[int] = mapped_column(Integer, nullable=True)
    stance: Mapped[str] = mapped_column(String(20), nullable=False)
    confidence: Mapped[float] = mapped_column(Float, default=0.0)
    price_at_analysis: Mapped[float] = mapped_column(Float, nullable=False)
    window: Mapped[str] = mapped_column(String(10), nullable=False)
    price_at_check: Mapped[float] = mapped_column(Float, default=0.0)
    return_pct: Mapped[float] = mapped_column(Float, default=0.0)
    correct: Mapped[bool] = mapped_column(default=False)
    checked_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
```

- [ ] **Step 4: Run tests**

Run: `cd backend && uv run pytest tests/test_signal_models.py -q`

Expected: pass.

## Task 2: Signal Outcome Evaluation

**Files:**
- Modify: `backend/app/core/scheduler.py`
- Create: `backend/tests/test_signal_evaluation.py`

- [ ] **Step 1: Write failing evaluation tests**

Create `backend/tests/test_signal_evaluation.py` with tests for:
- Evaluating a bullish analysis with higher price → correct
- Evaluating a bearish analysis with lower price → correct
- Window matching (1d outcome for 1d-old analysis)
- No duplicate outcomes for same analysis+window

- [ ] **Step 2: Run to verify failure**

Run: `cd backend && uv run pytest tests/test_signal_evaluation.py -q`

Expected: FAIL.

- [ ] **Step 3: Add evaluate_signal_outcomes to scheduler.py**

Add `evaluate_signal_outcomes(session)` that:
- Finds Analysis records that don't have SignalOutcome for each window yet
- For each, checks current price from PriceSnapshot
- Compares price change direction against stance (bullish→profit, bearish→loss)
- Creates SignalOutcome records
- Returns count of new outcomes

- [ ] **Step 4: Run tests**

Run: `cd backend && uv run pytest tests/test_signal_evaluation.py -q`

Expected: pass.

## Task 3: Signal Outcome API Endpoints

**Files:**
- Create: `backend/app/api/signals_routes.py`
- Modify: `backend/app/api/routes.py`
- Create: `backend/tests/test_signal_routes.py`

- [ ] **Step 1: Write failing tests**

Create `backend/tests/test_signal_routes.py` with tests for:
- GET /api/signals/outcomes returns history
- GET /api/signals/outcomes?symbol=AAPL filters by symbol
- GET /api/signals/metrics returns accuracy stats

- [ ] **Step 2: Run to verify failure**

Run: `cd backend && uv run pytest tests/test_signal_routes.py -q`

Expected: FAIL.

- [ ] **Step 3: Create signals routes**

Create `backend/app/api/signals_routes.py` with:
- GET /api/signals/outcomes — list outcomes (optional ?symbol= filter)
- GET /api/signals/metrics — aggregate stats: total_signals, correct_count, accuracy_pct, avg_return

Register router in routes.py.

- [ ] **Step 4: Run tests**

Run: `cd backend && uv run pytest tests/test_signal_routes.py -q`

Expected: pass.

## Task 4: Frontend Signal History

**Files:**
- Create: `frontend/src/components/SignalHistory.tsx`
- Modify: `frontend/src/lib/api.ts`
- Modify: `frontend/app/stocks/[symbol]/page.tsx`
- Modify: `frontend/tests/research-page.test.tsx`

- [ ] **Step 1: Update API types**

Add to `frontend/src/lib/api.ts`:

```typescript
export interface SignalOutcome {
  id: number;
  symbol: string;
  stance: string;
  confidence: number;
  price_at_analysis: number;
  window: string;
  price_at_check: number;
  return_pct: number;
  correct: boolean;
  checked_at: string;
}

export interface SignalMetrics {
  total_signals: number;
  correct_count: number;
  accuracy_pct: number;
  avg_return: number;
}

export async function fetchSignalOutcomes(symbol?: string): Promise<SignalOutcome[]> { ... }
export async function fetchSignalMetrics(): Promise<SignalMetrics> { ... }
```

- [ ] **Step 2: Create SignalHistory component**

Create `frontend/src/components/SignalHistory.tsx` showing:
- Overall accuracy metric
- Signal outcome table (symbol, stance, window, return, correct/wrong badge)
- Green/red color coding for correct/incorrect

- [ ] **Step 3: Update research page**

Add SignalHistory section to the research page, filtered for the current ticker symbol.

- [ ] **Step 4: Update tests**

Add tests for signal outcome display and metrics.

- [ ] **Step 5: Run frontend verification**

Run: `cd frontend && npm test -- --run && npm run lint && npm run build`

Expected: all pass.

## Task 5: Final Verification

- [ ] **Run all backend tests**: `cd backend && uv run pytest -q`
- [ ] **Run backend lint**: `cd backend && uv run ruff check app tests`
- [ ] **Run backend typecheck**: `cd backend && uv run mypy app`
- [ ] **Run all frontend checks**: `cd frontend && npm test -- --run && npm run lint && npm run build`
- [ ] **Run gitleaks**: `gitleaks detect --source . --no-git --config .gitleaks.toml`
