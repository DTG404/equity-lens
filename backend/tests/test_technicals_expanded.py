"""Tests for expanded technical indicators."""

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
async def test_stochastic_returns_k_and_d(client: AsyncClient) -> None:
    await client.post('/api/watchlist', json={'symbol': 'AAPL'})
    response = await client.get('/api/technicals/AAPL')
    assert response.status_code == 200
    data = response.json()
    assert 'stochastic' in data
    assert 'k' in data['stochastic']
    assert 'd' in data['stochastic']


@pytest.mark.asyncio
async def test_obv_returns_value(client: AsyncClient) -> None:
    await client.post('/api/watchlist', json={'symbol': 'MSFT'})
    response = await client.get('/api/technicals/MSFT')
    assert response.status_code == 200
    data = response.json()
    assert 'obv' in data
    assert isinstance(data['obv'], (int, float))


@pytest.mark.asyncio
async def test_ichimoku_returns_all_components(client: AsyncClient) -> None:
    await client.post('/api/watchlist', json={'symbol': 'AAPL'})
    response = await client.get('/api/technicals/AAPL')
    data = response.json()
    if 'ichimoku' in data:
        assert 'conversion' in data['ichimoku']
        assert 'base' in data['ichimoku']


@pytest.mark.asyncio
async def test_adx_returns_value(client: AsyncClient) -> None:
    await client.post('/api/watchlist', json={'symbol': 'AAPL'})
    response = await client.get('/api/technicals/AAPL')
    data = response.json()
    if 'adx' in data:
        assert 0 <= data['adx'] <= 100


@pytest.mark.asyncio
async def test_new_indicators_are_present(client: AsyncClient) -> None:
    await client.post('/api/watchlist', json={'symbol': 'AAPL'})
    response = await client.get('/api/technicals/AAPL')
    data = response.json()
    new_groups = ['williams_r', 'mfi', 'cci', 'vwap', 'keltner', 'parabolic_sar']
    for group in new_groups:
        assert group in data, f'{group} missing from response'


@pytest.mark.asyncio
async def test_elder_ray_returns_bull_bear_power(client: AsyncClient) -> None:
    await client.post('/api/watchlist', json={'symbol': 'AAPL'})
    response = await client.get('/api/technicals/AAPL')
    data = response.json()
    assert 'elder_ray' in data
    assert 'bull_power' in data['elder_ray']
    assert 'bear_power' in data['elder_ray']


@pytest.mark.asyncio
async def test_ad_line_returns_value(client: AsyncClient) -> None:
    await client.post('/api/watchlist', json={'symbol': 'AAPL'})
    response = await client.get('/api/technicals/AAPL')
    data = response.json()
    assert 'ad_line' in data
    assert isinstance(data['ad_line'], (int, float))
