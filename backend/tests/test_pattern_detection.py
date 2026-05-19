"""Tests for chart pattern detection."""

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.fixture
async def client() -> AsyncClient:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url='http://test') as ac:
        yield ac


@pytest.mark.asyncio
async def test_pattern_detection_returns_patterns(client: AsyncClient) -> None:
    await client.post('/api/watchlist', json={'symbol': 'AAPL'})
    response = await client.post('/api/technicals/AAPL/patterns')
    assert response.status_code == 200
    data = response.json()
    assert 'symbol' in data
    assert 'patterns' in data
    assert isinstance(data['patterns'], list)
