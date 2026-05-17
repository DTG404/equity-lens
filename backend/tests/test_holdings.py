"""Tests for holdings CRUD endpoints."""

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.fixture
async def client() -> AsyncClient:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url='http://test') as ac:
        yield ac


@pytest.mark.asyncio
async def test_add_holding(client: AsyncClient):
    response = await client.post('/api/holdings', json={
        'symbol': 'AAPL',
        'quantity': 10,
        'average_cost': 198.50,
    })
    assert response.status_code == 200
    data = response.json()
    assert data['symbol'] == 'AAPL'
    assert data['quantity'] == 10
    assert data['average_cost'] == 198.50
    assert 'id' in data


@pytest.mark.asyncio
async def test_list_holdings(client: AsyncClient):
    await client.post(
        '/api/holdings', json={'symbol': 'MSFT', 'quantity': 5, 'average_cost': 400.0},
    )

    response = await client.get('/api/holdings')
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    symbols = [h['symbol'] for h in data]
    assert 'MSFT' in symbols


@pytest.mark.asyncio
async def test_update_holding(client: AsyncClient):
    resp = await client.post('/api/holdings', json={
        'symbol': 'NVDA', 'quantity': 20, 'average_cost': 800.0,
    })
    holding_id = resp.json()['id']

    response = await client.put(f'/api/holdings/{holding_id}', json={
        'quantity': 25, 'average_cost': 820.0,
    })
    assert response.status_code == 200
    data = response.json()
    assert data['quantity'] == 25
    assert data['average_cost'] == 820.0


@pytest.mark.asyncio
async def test_delete_holding(client: AsyncClient):
    resp = await client.post('/api/holdings', json={
        'symbol': 'AMD', 'quantity': 100, 'average_cost': 150.0,
    })
    holding_id = resp.json()['id']

    response = await client.delete(f'/api/holdings/{holding_id}')
    assert response.status_code == 200

    response = await client.get('/api/holdings')
    ids = [h['id'] for h in response.json()]
    assert holding_id not in ids


@pytest.mark.asyncio
async def test_add_holding_invalid_symbol_returns_422(client: AsyncClient):
    response = await client.post('/api/holdings', json={
        'symbol': '$$$', 'quantity': 1, 'average_cost': 100.0,
    })
    assert response.status_code == 422
