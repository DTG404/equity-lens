import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.fixture
async def client() -> AsyncClient:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url='http://test') as ac:
        yield ac


@pytest.mark.asyncio
async def test_watchlist_returns_added_symbols(client: AsyncClient):
    await client.post('/api/watchlist', json={'symbol': 'AAPL', 'company_name': 'Apple Inc.'})
    await client.post('/api/watchlist', json={'symbol': 'MSFT', 'company_name': 'Microsoft Corp'})
    await client.post('/api/watchlist', json={'symbol': 'NVDA', 'company_name': 'NVIDIA Corp'})

    response = await client.get('/api/watchlist')

    assert response.status_code == 200
    data = response.json()

    assert len(data) >= 3
    symbols = {item['symbol'] for item in data}
    assert 'AAPL' in symbols
    assert 'MSFT' in symbols
    assert 'NVDA' in symbols

    for item in data:
        assert 'symbol' in item
        assert 'company_name' in item
        assert 'price' in item
        assert 'change_percent' in item
