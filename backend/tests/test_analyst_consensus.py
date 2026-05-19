"""Tests for analyst consensus endpoint."""

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.fixture
async def client() -> AsyncClient:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url='http://test') as ac:
        yield ac


@pytest.mark.asyncio
async def test_analyst_consensus_returns_ratings(client: AsyncClient) -> None:
    await client.post('/api/watchlist', json={'symbol': 'AAPL'})
    response = await client.get('/api/finnhub/analysts/AAPL')
    assert response.status_code == 200
    data = response.json()
    assert 'total_analysts' in data
    assert 'ratings' in data
    assert 'consensus' in data
