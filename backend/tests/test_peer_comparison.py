"""Tests for peer comparison endpoint."""

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
async def test_peers_returns_sector_comparison(client: AsyncClient) -> None:
    await client.post('/api/watchlist', json={'symbol': 'AAPL'})
    response = await client.get('/api/peers/AAPL')
    assert response.status_code == 200
    data = response.json()
    assert 'symbol' in data
    assert 'sector' in data
    assert data['sector'] == 'Technology'
    assert 'peers' in data
    assert 'percentiles' in data


@pytest.mark.asyncio
async def test_peers_returns_top_10_peers(client: AsyncClient) -> None:
    await client.post('/api/watchlist', json={'symbol': 'AAPL'})
    response = await client.get('/api/peers/AAPL')
    data = response.json()
    assert len(data['peers']) <= 10
    if data['peers']:
        assert 'symbol' in data['peers'][0]
        assert 'market_cap' in data['peers'][0]
