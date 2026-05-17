"""Tests for watchlist CRUD endpoints."""

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.fixture
async def client() -> AsyncClient:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url='http://test') as ac:
        yield ac


@pytest.mark.asyncio
async def test_add_watchlist_entry(client: AsyncClient):
    response = await client.post('/api/watchlist', json={
        'symbol': 'AAPL',
        'company_name': 'Apple Inc.',
    })
    assert response.status_code == 200
    data = response.json()
    assert data['symbol'] == 'AAPL'
    assert data['company_name'] == 'Apple Inc.'


@pytest.mark.asyncio
async def test_list_watchlist_returns_added_entries(client: AsyncClient):
    await client.post('/api/watchlist', json={'symbol': 'MSFT', 'company_name': 'Microsoft Corp'})

    response = await client.get('/api/watchlist')
    assert response.status_code == 200
    data = response.json()
    symbols = [item['symbol'] for item in data]
    assert 'MSFT' in symbols


@pytest.mark.asyncio
async def test_delete_watchlist_entry(client: AsyncClient):
    await client.post('/api/watchlist', json={'symbol': 'NVDA', 'company_name': 'NVIDIA Corp'})

    response = await client.delete('/api/watchlist/NVDA')
    assert response.status_code == 200

    response = await client.get('/api/watchlist')
    symbols = [item['symbol'] for item in response.json()]
    assert 'NVDA' not in symbols


@pytest.mark.asyncio
async def test_add_duplicate_symbol_returns_error(client: AsyncClient):
    await client.post('/api/watchlist', json={'symbol': 'AAPL'})
    response = await client.post('/api/watchlist', json={'symbol': 'AAPL'})
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_add_invalid_ticker_returns_error(client: AsyncClient):
    response = await client.post('/api/watchlist', json={'symbol': '../INVALID'})
    assert response.status_code == 422
