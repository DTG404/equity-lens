"""Tests for sector heatmap endpoint."""

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.fixture
async def client() -> AsyncClient:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url='http://test') as ac:
        yield ac


@pytest.mark.asyncio
async def test_heatmap_returns_sector_tree(client) -> None:
    response = await client.get('/api/heatmap')
    assert response.status_code == 200
    data = response.json()
    assert 'children' in data
    assert len(data['children']) > 0
    sector = data['children'][0]
    assert 'name' in sector
    assert 'children' in sector
    assert 'market_cap' in sector
    assert 'change_pct' in sector


@pytest.mark.asyncio
async def test_heatmap_children_have_expected_fields(client) -> None:
    response = await client.get('/api/heatmap')
    data = response.json()
    sector = data['children'][0]
    if sector['children']:
        industry = sector['children'][0]
        assert 'name' in industry
        if industry['children']:
            ticker = industry['children'][0]
            assert 'symbol' in ticker
            assert 'price' in ticker
