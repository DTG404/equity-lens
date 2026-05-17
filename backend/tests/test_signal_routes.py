"""Tests for signal outcome API endpoints."""

import pytest
from httpx import ASGITransport, AsyncClient

from app.domain.db_models import SignalOutcome
from app.main import app


@pytest.fixture
async def client() -> AsyncClient:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url='http://test') as ac:
        yield ac


@pytest.mark.asyncio
async def test_list_outcomes_returns_empty(client: AsyncClient):
    response = await client.get('/api/signals/outcomes')
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_list_outcomes_with_data(client: AsyncClient, async_db_session):
    async_db_session.add(
        SignalOutcome(
            symbol='AAPL',
            analysis_id=1,
            stance='bullish',
            confidence=0.8,
            price_at_analysis=180.0,
            window='1d',
            price_at_check=200.0,
            return_pct=11.11,
            correct=True,
        )
    )
    async_db_session.add(
        SignalOutcome(
            symbol='MSFT',
            analysis_id=2,
            stance='bearish',
            confidence=0.6,
            price_at_analysis=400.0,
            window='1w',
            price_at_check=380.0,
            return_pct=-5.0,
            correct=True,
        )
    )
    await async_db_session.commit()

    response = await client.get('/api/signals/outcomes')
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    symbols = {d['symbol'] for d in data}
    assert symbols == {'AAPL', 'MSFT'}
    assert data[0]['correct'] is True


@pytest.mark.asyncio
async def test_list_outcomes_filters_by_symbol(client: AsyncClient, async_db_session):
    async_db_session.add(
        SignalOutcome(
            symbol='AAPL', analysis_id=1, stance='bullish', price_at_analysis=180.0,
            window='1d', price_at_check=200.0, return_pct=11.11, correct=True,
        )
    )
    async_db_session.add(
        SignalOutcome(
            symbol='MSFT', analysis_id=2, stance='bearish', price_at_analysis=400.0,
            window='1w', price_at_check=380.0, return_pct=-5.0, correct=True,
        )
    )
    await async_db_session.commit()

    response = await client.get('/api/signals/outcomes?symbol=AAPL')
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]['symbol'] == 'AAPL'


@pytest.mark.asyncio
async def test_metrics_returns_accuracy_stats(client: AsyncClient, async_db_session):
    async_db_session.add_all([
        SignalOutcome(
            symbol='AAPL', analysis_id=1, stance='bullish', price_at_analysis=180.0,
            window='1d', price_at_check=200.0, return_pct=11.11, correct=True,
        ),
        SignalOutcome(
            symbol='MSFT', analysis_id=2, stance='bearish', price_at_analysis=400.0,
            window='1w', price_at_check=380.0, return_pct=-5.0, correct=True,
        ),
        SignalOutcome(
            symbol='GOOG', analysis_id=3, stance='bullish', price_at_analysis=150.0,
            window='1d', price_at_check=140.0, return_pct=-6.67, correct=False,
        ),
    ])
    await async_db_session.commit()

    response = await client.get('/api/signals/metrics')
    assert response.status_code == 200
    data = response.json()
    assert data['total_signals'] == 3
    assert data['correct_count'] == 2
    assert data['accuracy_pct'] == 66.67
    assert data['avg_return'] is not None


@pytest.mark.asyncio
async def test_metrics_with_no_data(client: AsyncClient):
    response = await client.get('/api/signals/metrics')
    assert response.status_code == 200
    data = response.json()
    assert data['total_signals'] == 0
    assert data['correct_count'] == 0
    assert data['accuracy_pct'] == 0.0
    assert data['avg_return'] == 0.0
