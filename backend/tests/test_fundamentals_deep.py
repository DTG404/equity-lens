"""Tests for extended fundamentals endpoint."""

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.fixture
async def client() -> AsyncClient:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url='http://test') as ac:
        yield ac


@pytest.mark.asyncio
async def test_fundamentals_returns_financial_statements(client: AsyncClient) -> None:
    await client.post('/api/watchlist', json={'symbol': 'AAPL'})
    response = await client.get('/api/fundamentals/AAPL')
    assert response.status_code == 200
    data = response.json()
    assert 'financial_statements' in data
    assert 'income_statement' in data['financial_statements']
    assert 'balance_sheet' in data['financial_statements']
    assert 'cash_flow' in data['financial_statements']
