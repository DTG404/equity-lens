"""Tests for short interest endpoint."""

from collections.abc import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url='http://test') as ac:
        yield ac


@pytest.mark.asyncio
async def test_short_interest_returns_data(client: AsyncClient) -> None:
    await client.post('/api/watchlist', json={'symbol': 'AAPL'})
    response = await client.get('/api/fundamentals/AAPL/short-interest')
    assert response.status_code == 200
    data = response.json()
    assert 'symbol' in data
    assert 'short_percent_of_float' in data
    assert 'days_to_cover' in data
    assert 'squeeze_signal' in data
