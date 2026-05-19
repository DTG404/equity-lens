"""Tests for multiticker comparison endpoint."""

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.fixture
async def client() -> AsyncClient:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url='http://test') as ac:
        yield ac


async def test_compare_returns_metrics_for_valid_tickers(client: AsyncClient) -> None:
    response = await client.get('/api/compare?tickers=AAPL,MSFT')
    assert response.status_code == 200
    data = response.json()
    assert 'tickers' in data
    assert 'metrics' in data
    assert len(data['tickers']) == 2
    assert 'price' in data['metrics']['AAPL']


async def test_compare_rejects_too_many_tickers(client: AsyncClient) -> None:
    tickers = ','.join([f'A{i}' for i in range(10)])
    response = await client.get(f'/api/compare?tickers={tickers}')
    assert response.status_code == 422


async def test_compare_rejects_single_ticker(client: AsyncClient) -> None:
    response = await client.get('/api/compare?tickers=AAPL')
    assert response.status_code == 422
