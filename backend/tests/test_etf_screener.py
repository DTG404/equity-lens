"""Tests for ETF screener expansion."""

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
async def test_screener_returns_etfs(client: AsyncClient) -> None:
    response = await client.get('/api/screener?assetType=etf&limit=5')
    assert response.status_code == 200
    data = response.json()
    assert 'results' in data
    assert len(data['results']) > 0
    for r in data['results']:
        assert r.get('asset_type') == 'etf', f'{r["symbol"]} should be etf'


@pytest.mark.asyncio
async def test_screener_asset_type_filter(client: AsyncClient) -> None:
    response = await client.get('/api/screener?assetType=stock&limit=5')
    assert response.status_code == 200
    data = response.json()
    assert len(data['results']) > 0
    for r in data['results']:
        assert r.get('asset_type') == 'stock', f'{r["symbol"]} should be stock'


@pytest.mark.asyncio
async def test_screener_returns_all_without_filter(client: AsyncClient) -> None:
    response = await client.get('/api/screener?limit=10')
    assert response.status_code == 200
    data = response.json()
    assert 'results' in data
