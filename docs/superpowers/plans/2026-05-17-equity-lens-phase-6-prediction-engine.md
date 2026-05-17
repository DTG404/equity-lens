# Equity Lens Phase 6: Prediction Engine Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace stub factor scoring with data-driven scoring, add DeepSeek-powered thesis/scenario generation, and store analysis audit trail.

**Architecture:** Factor scoring reads actual price data and news sentiment from the DB instead of using PRNG. A DeepSeek analysis service generates thesis and bull/base/bear scenarios via the DeepSeek API, with graceful fallback if no API key is set. Each analysis is stored in an `Analysis` DB table for full auditability.

**Tech Stack:** Python, httpx (DeepSeek API client), SQLAlchemy, FastAPI.

---

## File Structure Changes

```
backend/
  pyproject.toml                            # no new deps needed (httpx already installed)
  app/
    domain/
      scoring.py                            # MODIFY: data-driven scoring
      db_models.py                          # MODIFY: + Analysis model
    core/
      deepseek.py                           # NEW: DeepSeek API client
      config.py                             # MODIFY: ensure deepseek_api_key is loaded
    api/
      research_routes.py                    # MODIFY: use real scoring + DeepSeek + store analysis
  tests/
    test_scoring.py                         # MODIFY: update for data-driven scoring
    test_deepseek.py                        # NEW: DeepSeek client tests
    test_analysis_model.py                  # NEW: Analysis model tests
frontend/
  src/
    lib/
      api.ts                                # MODIFY: add scenarios to ResearchData
    components/
      FactorScoreCard.tsx                   # MODIFY: unchanged (data shape is same)
      ScenarioCard.tsx                      # NEW: bull/base/bear scenario display
    app/
      stocks/
        [symbol]/
          page.tsx                          # MODIFY: show scenarios, audit info, regenerate button
  tests/
    research-page.test.tsx                  # MODIFY: update for scenarios
```

## Task 1: Data-Driven Factor Scoring

**Files:**
- Modify: `backend/app/domain/scoring.py`
- Modify: `backend/tests/test_scoring.py`

- [ ] **Step 1: Rewrite scoring to accept real data**

Replace `compute_factor_scores` to accept optional price and news data instead of being purely PRNG-based. The new signature: `compute_factor_scores(symbol, price_change_pct=None, avg_news_sentiment=None)`. Technical score uses price change, news sentiment uses avg sentiment, fundamentals/macro remain stubs.

- [ ] **Step 2: Write updated tests**

Test that:
- Technical score increases with positive price change
- News sentiment score increases with positive news
- Fundamentals and macro are still returned
- Overall score is in 0-1 range

- [ ] **Step 3: Run tests to verify pass**

Run: `cd backend && uv run pytest tests/test_scoring.py -q`

Expected: all pass.

## Task 2: DeepSeek Analysis Service

**Files:**
- Create: `backend/app/core/deepseek.py`
- Create: `backend/tests/test_deepseek.py`

- [ ] **Step 1: Write failing DeepSeek tests**

Create `backend/tests/test_deepseek.py`:

```python
"""Tests for DeepSeek analysis service."""
from app.core.deepseek import generate_thesis, AnalysisInput


def test_generate_thesis_returns_structure_without_api_key(monkeypatch):
    monkeypatch.setenv('DEEPSEEK_API_KEY', '')
    result = generate_thesis(AnalysisInput(
        symbol='AAPL',
        company_name='Apple Inc.',
        technical_score=0.7,
        news_sentiment_score=0.6,
        fundamental_score=0.5,
        macro_score=0.5,
        overall_score=0.58,
        recent_news_titles=['Apple reports strong earnings'],
    ))
    assert 'thesis' in result
    assert 'bull_case' in result
    assert 'base_case' in result
    assert 'bear_case' in result
    assert result['model'] == 'fallback'
```

- [ ] **Step 2: Run to verify failure**

Run: `cd backend && uv run pytest tests/test_deepseek.py -q`

Expected: FAIL.

- [ ] **Step 3: Implement DeepSeek client**

Create `backend/app/core/deepseek.py` with:
- `AnalysisInput` dataclass containing all factor scores, news titles, symbol
- `generate_thesis(input)` function that:
  - If `deepseek_api_key` is set → calls DeepSeek API with structured prompt
  - If not set or API call fails → returns structured fallback with "fallback" model
  - Returns dict with thesis, bull_case, base_case, bear_case, model

- [ ] **Step 4: Run tests**

Run: `cd backend && uv run pytest tests/test_deepseek.py -q`

Expected: test passes with fallback (no API key by default).

## Task 3: Analysis Audit Model

**Files:**
- Modify: `backend/app/domain/db_models.py`
- Create: `backend/tests/test_analysis_model.py`

- [ ] **Step 1: Add Analysis model to db_models.py**

```python
class Analysis(Base):
    __tablename__ = 'analyses'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    symbol: Mapped[str] = mapped_column(String(10), index=True, nullable=False)
    technical_score: Mapped[float] = mapped_column(Float, default=0.0)
    news_sentiment_score: Mapped[float] = mapped_column(Float, default=0.0)
    fundamental_score: Mapped[float] = mapped_column(Float, default=0.0)
    macro_score: Mapped[float] = mapped_column(Float, default=0.0)
    overall_score: Mapped[float] = mapped_column(Float, default=0.0)
    stance: Mapped[str] = mapped_column(String(20), default='neutral')
    thesis: Mapped[str] = mapped_column(String(10000), default='')
    bull_case: Mapped[str] = mapped_column(String(5000), default='')
    base_case: Mapped[str] = mapped_column(String(5000), default='')
    bear_case: Mapped[str] = mapped_column(String(5000), default='')
    model_used: Mapped[str] = mapped_column(String(100), default='fallback')
    input_snapshot: Mapped[str] = mapped_column(String(10000), default='')
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
```

- [ ] **Step 2: Write analysis model tests**

Create `tests/test_analysis_model.py` with round-trip and query tests.

- [ ] **Step 3: Run tests**

Run: `cd backend && uv run pytest tests/test_analysis_model.py -q`

Expected: all pass.

## Task 4: Update Research Endpoint

**Files:**
- Modify: `backend/app/api/research_routes.py`
- Modify: `backend/tests/test_research_routes.py`

- [ ] **Step 1: Update research route to use real scoring + DeepSeek + store analysis**

The research endpoint now:
1. Computes factor scores from real data (price change from latest snapshot, avg news sentiment from DB)
2. Calls DeepSeek to generate thesis + scenarios
3. Stores the Analysis in DB
4. Returns all data including scenarios and analysis metadata

- [ ] **Step 2: Update tests**

Update `test_research_routes.py` to expect scenarios and analysis metadata in the response.

- [ ] **Step 3: Run all backend tests**

Run: `cd backend && uv run pytest -q`

Expected: all existing tests + new tests pass.

## Task 5: Frontend Scenarios + Audit Display

**Files:**
- Create: `frontend/src/components/ScenarioCard.tsx`
- Modify: `frontend/app/stocks/[symbol]/page.tsx`
- Modify: `frontend/src/lib/api.ts`
- Modify: `frontend/tests/research-page.test.tsx`

- [ ] **Step 1: Update API types**

Add to `frontend/src/lib/api.ts`: bull_case, base_case, bear_case, model_used, analysis_id to ResearchData.

- [ ] **Step 2: Create ScenarioCard component**

Create `frontend/src/components/ScenarioCard.tsx` showing three columns: bull, base, bear scenarios with color coding (green/blue/red).

- [ ] **Step 3: Update research page**

Add ScenarioCard and analysis metadata (model used, timestamp) to the research page.

- [ ] **Step 4: Update tests**

Update `research-page.test.tsx` to test for scenarios and audit info.

- [ ] **Step 5: Run frontend verification**

Run: `cd frontend && npm test -- --run && npm run lint && npm run build`

Expected: all pass.

## Task 6: Final Verification

- [ ] **Run all backend tests**: `cd backend && uv run pytest -q`
- [ ] **Run backend lint**: `cd backend && uv run ruff check app tests`
- [ ] **Run backend typecheck**: `cd backend && uv run mypy app`
- [ ] **Run all frontend checks**: `cd frontend && npm test -- --run && npm run lint && npm run build`
- [ ] **Run gitleaks**: `gitleaks detect --source . --no-git --config .gitleaks.toml`
