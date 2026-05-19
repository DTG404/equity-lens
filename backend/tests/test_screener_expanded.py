"""Tests for expanded screener filters, presets, and CSV export."""

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.fixture
async def client() -> AsyncClient:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url='http://test') as ac:
        yield ac


@pytest.mark.asyncio
async def test_screener_accepts_new_filters(client: AsyncClient) -> None:
    """New valuation, financial health, and market metric filters are accepted."""
    response = await client.get(
        '/api/screener?min_market_cap=100000000000&min_pe=10&max_pe=50'
        '&min_ps=0.5&max_ps=20&min_pb=0.5&max_pb=30'
        '&max_debt_to_equity=2.0&min_profit_margin=0.05&min_revenue_growth=0.0'
        '&min_beta=0.5&max_beta=2.5'
        '&min_short_float=0.0&max_short_float=0.5&min_inst_ownership=0.1'
        '&min_dividend_yield=0.0&max_dividend_yield=0.1'
    )
    assert response.status_code == 200
    data = response.json()
    assert 'results' in data
    assert isinstance(data['results'], list)


@pytest.mark.asyncio
async def test_screener_presets_crud(client: AsyncClient) -> None:
    """Preset endpoints support create, list, and delete."""
    create = await client.post(
        '/api/screener/presets',
        json={
            'name': 'test_large_cap',
            'filters': {'min_market_cap': 200000000000, 'sector': 'Technology'},
        },
    )
    assert create.status_code == 200
    created = create.json()
    assert created['name'] == 'test_large_cap'

    listed = await client.get('/api/screener/presets')
    assert listed.status_code == 200
    presets = listed.json()
    assert isinstance(presets, list)
    names = [p['name'] for p in presets]
    assert 'test_large_cap' in names

    delete = await client.delete('/api/screener/presets/test_large_cap')
    assert delete.status_code == 200

    after = await client.get('/api/screener/presets')
    after_names = [p['name'] for p in after.json()]
    assert 'test_large_cap' not in after_names


@pytest.mark.asyncio
async def test_screener_presets_missing_name(client: AsyncClient) -> None:
    """Creating a preset without a name returns 422."""
    response = await client.post(
        '/api/screener/presets',
        json={'filters': {}},
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_screener_presets_delete_nonexistent(client: AsyncClient) -> None:
    """Deleting a non-existent preset returns 404."""
    response = await client.delete('/api/screener/presets/nonexistent_preset')
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_screener_csv_export(client: AsyncClient) -> None:
    """CSV export endpoint returns text/csv with correct content type."""
    response = await client.get(
        '/api/screener/export?min_market_cap=100000000000&sector=Technology'
    )
    assert response.status_code == 200
    assert response.headers['content-type'] == 'text/csv; charset=utf-8'
    body = response.text
    assert body.startswith('symbol')
    assert 'AAPL' in body or 'MSFT' in body or body.count(',') > 0
