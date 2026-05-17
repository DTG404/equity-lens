"""Tests for the Analysis ORM model."""
import pytest
from sqlalchemy import select

from app.domain.db_models import Analysis


@pytest.mark.asyncio
async def test_analysis_round_trip(async_db_session):
    analysis = Analysis(
        symbol='AAPL',
        technical_score=0.7,
        news_sentiment_score=0.6,
        fundamental_score=0.5,
        macro_score=0.5,
        overall_score=0.58,
        stance='neutral',
        thesis='Test thesis',
        bull_case='Bull case',
        base_case='Base case',
        bear_case='Bear case',
        model_used='deepseek-chat',
        input_snapshot='{"symbol": "AAPL"}',
    )
    async_db_session.add(analysis)
    await async_db_session.commit()

    result = await async_db_session.execute(
        select(Analysis).where(Analysis.symbol == 'AAPL')
    )
    saved = result.scalar_one()
    assert saved.symbol == 'AAPL'
    assert saved.technical_score == 0.7
    assert saved.overall_score == 0.58
    assert saved.stance == 'neutral'
    assert saved.thesis == 'Test thesis'
    assert saved.model_used == 'deepseek-chat'
    assert saved.created_at is not None


@pytest.mark.asyncio
async def test_analysis_defaults(async_db_session):
    analysis = Analysis(symbol='MSFT')
    async_db_session.add(analysis)
    await async_db_session.commit()

    result = await async_db_session.execute(
        select(Analysis).where(Analysis.symbol == 'MSFT')
    )
    saved = result.scalar_one()
    assert saved.technical_score == 0.0
    assert saved.stance == 'neutral'
    assert saved.model_used == 'fallback'
    assert saved.created_at is not None


@pytest.mark.asyncio
async def test_analysis_multiple_per_symbol(async_db_session):
    a1 = Analysis(symbol='AAPL', overall_score=0.5)
    a2 = Analysis(symbol='AAPL', overall_score=0.7)
    async_db_session.add_all([a1, a2])
    await async_db_session.commit()

    result = await async_db_session.execute(
        select(Analysis)
        .where(Analysis.symbol == 'AAPL')
        .order_by(Analysis.created_at.desc())
    )
    saved = result.scalars().all()
    assert len(saved) == 2
