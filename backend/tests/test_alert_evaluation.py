"""Tests for alert evaluation logic."""

import pytest
from sqlalchemy import select

from app.core.scheduler import evaluate_alerts
from app.domain.db_models import AlertEvent, AlertRule, PriceSnapshot


@pytest.mark.asyncio
async def test_evaluate_price_above_triggers_event(async_db_session):
    rule = AlertRule(symbol='AAPL', alert_type='price', condition='above', threshold=150.0)
    async_db_session.add(rule)
    snapshot = PriceSnapshot(symbol='AAPL', price=160.0, change_percent=5.0)
    async_db_session.add(snapshot)
    await async_db_session.commit()

    count = await evaluate_alerts(get_session=lambda: async_db_session)

    assert count == 1
    result = await async_db_session.execute(select(AlertEvent))
    events = result.scalars().all()
    assert len(events) == 1
    assert events[0].symbol == 'AAPL'
    assert events[0].alert_type == 'price'
    assert 'exceeded' in events[0].message or 'above' in events[0].message


@pytest.mark.asyncio
async def test_evaluate_price_below_triggers_event(async_db_session):
    rule = AlertRule(symbol='MSFT', alert_type='price', condition='below', threshold=400.0)
    async_db_session.add(rule)
    snapshot = PriceSnapshot(symbol='MSFT', price=380.0, change_percent=-3.0)
    async_db_session.add(snapshot)
    await async_db_session.commit()

    count = await evaluate_alerts(get_session=lambda: async_db_session)

    assert count == 1
    result = await async_db_session.execute(select(AlertEvent))
    events = result.scalars().all()
    assert len(events) == 1
    assert events[0].symbol == 'MSFT'
    assert 'below' in events[0].message


@pytest.mark.asyncio
async def test_evaluate_wrong_symbol_does_not_trigger(async_db_session):
    rule = AlertRule(symbol='AAPL', alert_type='price', condition='above', threshold=100.0)
    async_db_session.add(rule)
    snapshot = PriceSnapshot(symbol='MSFT', price=500.0, change_percent=10.0)
    async_db_session.add(snapshot)
    await async_db_session.commit()

    count = await evaluate_alerts(get_session=lambda: async_db_session)

    assert count == 0
    result = await async_db_session.execute(select(AlertEvent))
    events = result.scalars().all()
    assert len(events) == 0


@pytest.mark.asyncio
async def test_evaluate_disabled_rule_does_not_trigger(async_db_session):
    rule = AlertRule(
        symbol='AAPL', alert_type='price', condition='above', threshold=100.0, enabled=False
    )
    async_db_session.add(rule)
    snapshot = PriceSnapshot(symbol='AAPL', price=200.0, change_percent=10.0)
    async_db_session.add(snapshot)
    await async_db_session.commit()

    count = await evaluate_alerts(get_session=lambda: async_db_session)

    assert count == 0
    result = await async_db_session.execute(select(AlertEvent))
    events = result.scalars().all()
    assert len(events) == 0
