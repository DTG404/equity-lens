"""Tests for sector performance endpoint."""

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.fixture
async def client() -> AsyncClient:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url='http://test') as ac:
        yield ac


@pytest.mark.asyncio
async def test_sector_performance_returns_sectors(client: AsyncClient) -> None:
    response = await client.get('/api/markets/sectors?period=1d')
    assert response.status_code == 200
    data = response.json()
    assert 'period' in data
    assert 'sectors' in data
    assert len(data['sectors']) > 0
