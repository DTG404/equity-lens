"""Tests for SQLAlchemy ORM models."""

import pytest
from sqlalchemy import select

from app.domain.db_models import Holding, Setting, WatchlistEntry


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
