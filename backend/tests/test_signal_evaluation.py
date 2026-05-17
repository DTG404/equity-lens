"""Tests for signal outcome evaluation logic."""
from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import select

from app.core.scheduler import evaluate_signal_outcomes
from app.domain.db_models import Analysis, PriceSnapshot, SignalOutcome


def _snapshot(symbol: str, price: float, age: timedelta) -> PriceSnapshot:
    return PriceSnapshot(
        symbol=symbol, price=price,
        recorded_at=datetime.now(UTC) - age,
    )


@pytest.mark.asyncio
async def test_evaluate_bullish_price_up_returns_correct(async_db_session):
    """Bullish analysis where price went up -> correct=True."""
    old = datetime.now(UTC) - timedelta(hours=72)
    analysis = Analysis(
        symbol='AAPL', stance='bullish', overall_score=0.8, created_at=old,
    )
    async_db_session.add(analysis)
    async_db_session.add(_snapshot('AAPL', 180.0, timedelta(hours=73)))
    async_db_session.add(_snapshot('AAPL', 200.0, timedelta(hours=0)))
    await async_db_session.commit()

    count = await evaluate_signal_outcomes(get_session=lambda: async_db_session)
    assert count == 1

    result = await async_db_session.execute(
        select(SignalOutcome).where(SignalOutcome.analysis_id == analysis.id),
    )
    outcome = result.scalar_one()
    assert outcome.stance == 'bullish'
    assert outcome.correct is True
    assert outcome.window == '1d'
    assert outcome.price_at_analysis == 180.0
    assert outcome.price_at_check == 200.0
    assert outcome.return_pct > 0


@pytest.mark.asyncio
async def test_evaluate_bearish_price_down_returns_correct(async_db_session):
    """Bearish analysis where price went down -> correct=True."""
    old = datetime.now(UTC) - timedelta(hours=72)
    analysis = Analysis(
        symbol='AAPL', stance='bearish', overall_score=0.3, created_at=old,
    )
    async_db_session.add(analysis)
    async_db_session.add(_snapshot('AAPL', 200.0, timedelta(hours=73)))
    async_db_session.add(_snapshot('AAPL', 150.0, timedelta(hours=0)))
    await async_db_session.commit()

    count = await evaluate_signal_outcomes(get_session=lambda: async_db_session)
    assert count >= 1

    result = await async_db_session.execute(
        select(SignalOutcome).where(SignalOutcome.analysis_id == analysis.id),
    )
    outcome = result.scalar_one()
    assert outcome.stance == 'bearish'
    assert outcome.correct is True


@pytest.mark.asyncio
async def test_evaluate_bullish_price_down_returns_incorrect(async_db_session):
    """Bullish analysis where price went down -> correct=False."""
    old = datetime.now(UTC) - timedelta(hours=72)
    analysis = Analysis(
        symbol='AAPL', stance='bullish', overall_score=0.8, created_at=old,
    )
    async_db_session.add(analysis)
    async_db_session.add(_snapshot('AAPL', 200.0, timedelta(hours=73)))
    async_db_session.add(_snapshot('AAPL', 180.0, timedelta(hours=0)))
    await async_db_session.commit()

    count = await evaluate_signal_outcomes(get_session=lambda: async_db_session)
    assert count == 1

    result = await async_db_session.execute(
        select(SignalOutcome).where(SignalOutcome.analysis_id == analysis.id),
    )
    outcome = result.scalar_one()
    assert outcome.correct is False


@pytest.mark.asyncio
async def test_evaluate_neutral_always_incorrect(async_db_session):
    """Neutral stance should always have correct=False."""
    old = datetime.now(UTC) - timedelta(hours=72)
    analysis = Analysis(
        symbol='AAPL', stance='neutral', overall_score=0.5, created_at=old,
    )
    async_db_session.add(analysis)
    async_db_session.add(_snapshot('AAPL', 180.0, timedelta(hours=73)))
    async_db_session.add(_snapshot('AAPL', 200.0, timedelta(hours=0)))
    await async_db_session.commit()

    count = await evaluate_signal_outcomes(get_session=lambda: async_db_session)
    assert count >= 1

    result = await async_db_session.execute(
        select(SignalOutcome).where(SignalOutcome.analysis_id == analysis.id),
    )
    outcome = result.scalar_one()
    assert outcome.correct is False


@pytest.mark.asyncio
async def test_window_matches_analysis_age(async_db_session):
    """Analysis age determines window: >=24h -> 1d, >=7d -> 1w, >=30d -> 1m."""
    now = datetime.now(UTC)
    base_age = timedelta(days=60)

    a1 = Analysis(symbol='AAPL', stance='bullish', created_at=now - timedelta(hours=25))
    a2 = Analysis(symbol='MSFT', stance='bullish', created_at=now - timedelta(days=8))
    a3 = Analysis(symbol='GOOG', stance='bullish', created_at=now - timedelta(days=31))

    async_db_session.add_all([a1, a2, a3])
    for sym in ['AAPL', 'MSFT', 'GOOG']:
        async_db_session.add(PriceSnapshot(
            symbol=sym, price=100.0, recorded_at=now - base_age,
        ))
        async_db_session.add(PriceSnapshot(
            symbol=sym, price=200.0, recorded_at=now,
        ))

    await async_db_session.commit()

    count = await evaluate_signal_outcomes(get_session=lambda: async_db_session)
    assert count == 6

    outcomes_result = await async_db_session.execute(
        select(SignalOutcome).order_by(SignalOutcome.id),
    )
    outcomes = outcomes_result.scalars().all()

    a1_outcomes = [o for o in outcomes if o.symbol == 'AAPL']
    assert len(a1_outcomes) == 1
    assert a1_outcomes[0].window == '1d'

    a2_outcomes = [o for o in outcomes if o.symbol == 'MSFT']
    assert len(a2_outcomes) == 2
    assert {o.window for o in a2_outcomes} == {'1d', '1w'}

    a3_outcomes = [o for o in outcomes if o.symbol == 'GOOG']
    assert len(a3_outcomes) == 3
    assert {o.window for o in a3_outcomes} == {'1d', '1w', '1m'}


@pytest.mark.asyncio
async def test_no_duplicate_outcomes(async_db_session):
    """Calling evaluate_signal_outcomes twice should not create duplicates."""
    old = datetime.now(UTC) - timedelta(hours=72)
    analysis = Analysis(symbol='AAPL', stance='bullish', created_at=old)
    async_db_session.add(analysis)
    async_db_session.add(_snapshot('AAPL', 180.0, timedelta(hours=73)))
    async_db_session.add(_snapshot('AAPL', 200.0, timedelta(hours=0)))
    await async_db_session.commit()

    count1 = await evaluate_signal_outcomes(get_session=lambda: async_db_session)
    assert count1 == 1

    count2 = await evaluate_signal_outcomes(get_session=lambda: async_db_session)
    assert count2 == 0

    result = await async_db_session.execute(
        select(SignalOutcome).where(SignalOutcome.analysis_id == analysis.id),
    )
    outcomes = result.scalars().all()
    assert len(outcomes) == 1


@pytest.mark.asyncio
async def test_evaluate_multiple_analyses(async_db_session):
    """evaluate_signal_outcomes handles multiple analyses correctly."""
    old = datetime.now(UTC) - timedelta(hours=72)
    a1 = Analysis(symbol='AAPL', stance='bullish', created_at=old)
    a2 = Analysis(symbol='MSFT', stance='bearish', created_at=old)
    async_db_session.add_all([a1, a2])
    for sym, price in [('AAPL', 180.0), ('MSFT', 200.0)]:
        async_db_session.add(
            _snapshot(sym, price, timedelta(hours=73)),
        )
    for sym, price in [('AAPL', 200.0), ('MSFT', 150.0)]:
        async_db_session.add(
            _snapshot(sym, price, timedelta(hours=0)),
        )
    await async_db_session.commit()

    count = await evaluate_signal_outcomes(get_session=lambda: async_db_session)
    assert count == 2
