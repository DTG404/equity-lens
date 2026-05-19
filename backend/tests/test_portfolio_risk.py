"""Tests for portfolio risk metrics."""

from collections.abc import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient

from app.domain.db_models import Holding, PriceSnapshot
from app.main import app


@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url='http://test') as ac:
        yield ac


@pytest.mark.asyncio
async def test_portfolio_analytics_returns_risk_metrics(async_db_session, client: AsyncClient) -> None:
    async_db_session.add(Holding(symbol='AAPL', quantity=10, average_cost=150.0))
    async_db_session.add(PriceSnapshot(symbol='AAPL', price=180.0, change_percent=1.0, provider='test'))
    await async_db_session.commit()

    response = await client.get('/api/portfolio/analytics')
    assert response.status_code == 200
    data = response.json()
    assert 'risk_metrics' in data
    assert 'sharpe_ratio' in data['risk_metrics']
    assert 'beta' in data['risk_metrics']
    assert 'max_drawdown_pct' in data['risk_metrics']


@pytest.mark.asyncio
async def test_portfolio_risk_metrics_empty_for_no_holdings(client: AsyncClient) -> None:
    response = await client.get('/api/portfolio/analytics')
    data = response.json()
    assert 'risk_metrics' in data
    assert data['risk_metrics'] is None or all(v is None for v in data['risk_metrics'].values())
