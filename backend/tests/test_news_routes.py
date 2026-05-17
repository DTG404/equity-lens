"""Tests for news API endpoints."""
import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.fixture
async def client() -> AsyncClient:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url='http://test') as ac:
        yield ac


@pytest.mark.asyncio
async def test_get_news_for_watched_symbol(client: AsyncClient):
    await client.post('/api/watchlist', json={'symbol': 'AAPL'})
    response = await client.get('/api/news/AAPL')
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_get_news_for_unwatched_symbol_returns_404(client: AsyncClient):
    response = await client.get('/api/news/ZZZZ')
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_aggregated_news(client: AsyncClient):
    await client.post('/api/watchlist', json={'symbol': 'AAPL'})
    response = await client.get('/api/news')
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
