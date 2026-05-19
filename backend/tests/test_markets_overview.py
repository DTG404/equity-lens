"""Tests for markets overview endpoint."""

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
async def test_markets_overview_returns_all_sections(client: AsyncClient) -> None:
    response = await client.get('/api/markets/overview')
    assert response.status_code == 200
    data = response.json()
    assert 'indices' in data
    assert 'breadth' in data or data['breadth'] is None
    assert 'commodities' in data
    assert 'global' in data


@pytest.mark.asyncio
async def test_markets_overview_indices_have_required_fields(client: AsyncClient) -> None:
    response = await client.get('/api/markets/overview')
    data = response.json()
    if data['indices']:
        idx = data['indices'][0]
        assert 'symbol' in idx
        assert 'name' in idx
        assert 'price' in idx
