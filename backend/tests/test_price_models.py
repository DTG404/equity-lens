"""Tests for price-related DB models."""
from datetime import UTC, datetime

import pytest
from sqlalchemy import select

from app.domain.db_models import PriceHistory, PriceSnapshot


@pytest.mark.asyncio
async def test_price_snapshot_round_trip(async_db_session):
    snapshot = PriceSnapshot(
        symbol='AAPL',
        price=185.50,
        change_percent=1.25,
        provider='test',
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
        date=datetime(2025, 1, 15, tzinfo=UTC).date(),
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
