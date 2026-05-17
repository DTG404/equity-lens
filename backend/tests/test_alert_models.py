"""Tests for alert DB models."""

import pytest
from sqlalchemy import select

from app.domain.db_models import AlertEvent, AlertRule


@pytest.mark.asyncio
async def test_alert_rule_round_trip(async_db_session):
    rule = AlertRule(
        symbol='AAPL',
        alert_type='price',
        condition='above',
        threshold=200.0,
    )
    async_db_session.add(rule)
    await async_db_session.commit()

    result = await async_db_session.execute(
        select(AlertRule).where(AlertRule.symbol == 'AAPL')
    )
    saved = result.scalar_one()
    assert saved.symbol == 'AAPL'
    assert saved.alert_type == 'price'
    assert saved.condition == 'above'
    assert saved.threshold == 200.0
    assert saved.enabled is True
    assert saved.created_at is not None


@pytest.mark.asyncio
async def test_alert_event_round_trip(async_db_session):
    event = AlertEvent(
        rule_id=1,
        symbol='AAPL',
        alert_type='price',
        message='AAPL exceeded $200',
        severity='warning',
    )
    async_db_session.add(event)
    await async_db_session.commit()

    result = await async_db_session.execute(
        select(AlertEvent).where(AlertEvent.symbol == 'AAPL')
    )
    saved = result.scalar_one()
    assert saved.symbol == 'AAPL'
    assert saved.alert_type == 'price'
    assert saved.message == 'AAPL exceeded $200'
    assert saved.severity == 'warning'
    assert saved.read is False
    assert saved.triggered_at is not None
