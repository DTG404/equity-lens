"""Tests for portfolio analytics endpoint."""

from datetime import UTC, datetime

import pytest
from httpx import ASGITransport, AsyncClient

from app.domain.db_models import Holding, PriceHistory, PriceSnapshot
from app.main import app


@pytest.fixture
async def client() -> AsyncClient:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url='http://test') as ac:
        yield ac


@pytest.mark.asyncio
async def test_portfolio_analytics_returns_allocation(async_db_session, client) -> None:
    """Allocation should break down by ticker."""
    async_db_session.add(Holding(symbol='AAPL', quantity=10, average_cost=150.0))
    async_db_session.add(Holding(symbol='MSFT', quantity=5, average_cost=350.0))
    async_db_session.add(PriceSnapshot(symbol='AAPL', price=180.0, change_percent=1.0, provider='test'))
    async_db_session.add(PriceSnapshot(symbol='MSFT', price=420.0, change_percent=0.5, provider='test'))
    await async_db_session.commit()

    response = await client.get('/api/portfolio/analytics')
    assert response.status_code == 200
    data = response.json()

    assert 'allocation' in data
    assert 'by_ticker' in data['allocation']
    assert len(data['allocation']['by_ticker']) == 2
    assert data['allocation']['total_value'] > 0


@pytest.mark.asyncio
async def test_portfolio_analytics_returns_value_history(async_db_session, client) -> None:
    """Value history should estimate portfolio value over time."""
    async_db_session.add(Holding(symbol='AAPL', quantity=10, average_cost=150.0))
    async_db_session.add(PriceHistory(
        symbol='AAPL', date=datetime(2026, 5, 1, tzinfo=UTC),
        open_price=170.0, high_price=175.0, low_price=168.0, close_price=172.0, volume=1000000,
    ))
    async_db_session.add(PriceHistory(
        symbol='AAPL', date=datetime(2026, 5, 2, tzinfo=UTC),
        open_price=172.0, high_price=180.0, low_price=171.0, close_price=178.0, volume=1200000,
    ))
    await async_db_session.commit()

    response = await client.get('/api/portfolio/analytics')
    data = response.json()
    assert 'value_history' in data
    assert len(data['value_history']) > 0
