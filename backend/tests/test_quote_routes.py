"""Tests for quote endpoints."""
import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.fixture
async def client() -> AsyncClient:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url='http://test') as ac:
        yield ac


@pytest.mark.asyncio
async def test_get_latest_quote_for_watched_symbol(client: AsyncClient):
    await client.post('/api/watchlist', json={'symbol': 'AAPL'})
    response = await client.get('/api/quotes/AAPL')
    assert response.status_code == 200
    data = response.json()
    assert 'symbol' in data
    assert 'price' in data


@pytest.mark.asyncio
async def test_get_quote_for_unwatched_symbol_returns_404(client: AsyncClient):
    response = await client.get('/api/quotes/ZZZZ')
    assert response.status_code == 404
