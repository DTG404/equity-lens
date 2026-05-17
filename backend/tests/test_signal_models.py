"""Tests for SignalOutcome model."""
import pytest
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
