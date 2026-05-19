"""Tests for broker order endpoints."""

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
async def test_place_order_missing_symbol(client: AsyncClient) -> None:
    response = await client.post('/api/broker/order', json={
        'side': 'buy', 'quantity': 10, 'symbol': '',
    })
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_order_history(client: AsyncClient) -> None:
    response = await client.get('/api/broker/orders')
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
