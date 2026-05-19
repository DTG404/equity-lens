"""Tests for backtesting engine."""

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
async def test_backtest_engine_runs(client: AsyncClient) -> None:
    payload = {
        'strategy': {
            'name': 'RSI Test',
            'entry_conditions': [{'indicator': 'rsi', 'operator': '<', 'value': 40}],
            'exit_conditions': [{'indicator': 'rsi', 'operator': '>', 'value': 60}],
            'tickers': ['AAPL'],
        }
    }
    response = await client.post('/api/backtest/run', json=payload)
    assert response.status_code == 200
    data = response.json()
    assert 'total_trades' in data
    assert 'overall_return_pct' in data


@pytest.mark.asyncio
async def test_backtest_with_empty_tickers(client: AsyncClient) -> None:
    payload = {'strategy': {'name': 'Empty', 'tickers': []}}
    response = await client.post('/api/backtest/run', json=payload)
    assert response.status_code == 200
    data = response.json()
    assert 'error' in data
