"""Tests for earnings summary endpoint."""

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.fixture
async def client() -> AsyncClient:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url='http://test') as ac:
        yield ac


@pytest.mark.asyncio
async def test_earnings_summary_returns_data(client: AsyncClient) -> None:
    await client.post('/api/watchlist', json={'symbol': 'AAPL'})
    response = await client.get('/api/research/AAPL/earnings-summary')
    assert response.status_code == 200
    data = response.json()
    assert 'symbol' in data
    assert 'quarterly_trend' in data


@pytest.mark.asyncio
async def test_earnings_summary_for_unwatched_returns_data(client: AsyncClient) -> None:
    response = await client.get('/api/research/ZZZZ/earnings-summary')
    assert response.status_code == 200
    data = response.json()
    assert data['symbol'] == 'ZZZZ'
