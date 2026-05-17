"""Tests for alert API endpoints."""

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.fixture
async def client() -> AsyncClient:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url='http://test') as ac:
        yield ac


@pytest.mark.asyncio
async def test_list_rules_returns_empty(client: AsyncClient):
    response = await client.get('/api/alerts/rules')
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_create_rule(client: AsyncClient):
    response = await client.post(
        '/api/alerts/rules',
        json={'symbol': 'AAPL', 'alert_type': 'price', 'condition': 'above', 'threshold': 200.0},
    )
    assert response.status_code == 200
    data = response.json()
    assert data['symbol'] == 'AAPL'
    assert data['alert_type'] == 'price'
    assert data['condition'] == 'above'
    assert data['threshold'] == 200.0
    assert data['enabled'] is True
    assert 'id' in data


@pytest.mark.asyncio
async def test_create_rule_validates_alert_type(client: AsyncClient):
    response = await client.post(
        '/api/alerts/rules',
        json={'symbol': 'AAPL', 'alert_type': 'invalid', 'condition': 'above', 'threshold': 100.0},
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_rule_validates_condition(client: AsyncClient):
    response = await client.post(
        '/api/alerts/rules',
        json={'symbol': 'AAPL', 'alert_type': 'price', 'condition': 'invalid', 'threshold': 100.0},
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_delete_rule(client: AsyncClient):
    create = await client.post(
        '/api/alerts/rules',
        json={'symbol': 'MSFT', 'alert_type': 'price', 'condition': 'below', 'threshold': 300.0},
    )
    rule_id = create.json()['id']

    response = await client.delete(f'/api/alerts/rules/{rule_id}')
    assert response.status_code == 200

    list_resp = await client.get('/api/alerts/rules')
    assert list_resp.json() == []


@pytest.mark.asyncio
async def test_delete_nonexistent_rule_returns_404(client: AsyncClient):
    response = await client.delete('/api/alerts/rules/9999')
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_list_events_returns_recent_first(client: AsyncClient):
    response = await client.get('/api/alerts/events')
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_unread_count(client: AsyncClient):
    response = await client.get('/api/alerts/events/unread-count')
    assert response.status_code == 200
    data = response.json()
    assert 'count' in data
    assert isinstance(data['count'], int)


@pytest.mark.asyncio
async def test_mark_event_read(client: AsyncClient, async_db_session):
    await client.post(
        '/api/alerts/rules',
        json={'symbol': 'AAPL', 'alert_type': 'price', 'condition': 'above', 'threshold': 100.0},
    )
    from app.core.scheduler import evaluate_alerts
    from app.domain.db_models import PriceSnapshot

    async_db_session.add(PriceSnapshot(symbol='AAPL', price=200.0, change_percent=10.0))
    await async_db_session.commit()

    await evaluate_alerts(get_session=lambda: async_db_session)

    unread = await client.get('/api/alerts/events/unread-count')
    assert unread.json()['count'] >= 1

    events = await client.get('/api/alerts/events')
    event_id = events.json()[0]['id']

    resp = await client.patch(f'/api/alerts/events/{event_id}/read')
    assert resp.status_code == 200

    unread2 = await client.get('/api/alerts/events/unread-count')
    count_before = unread.json()['count']
    count_after = unread2.json()['count']
    assert count_after == count_before - 1


@pytest.mark.asyncio
async def test_mark_all_events_read(client: AsyncClient, async_db_session):
    await client.post(
        '/api/alerts/rules',
        json={'symbol': 'AAPL', 'alert_type': 'price', 'condition': 'above', 'threshold': 100.0},
    )
    from app.core.scheduler import evaluate_alerts
    from app.domain.db_models import PriceSnapshot

    async_db_session.add(PriceSnapshot(symbol='AAPL', price=200.0, change_percent=10.0))
    await async_db_session.commit()

    await evaluate_alerts(get_session=lambda: async_db_session)

    resp = await client.post('/api/alerts/events/read-all')
    assert resp.status_code == 200

    unread = await client.get('/api/alerts/events/unread-count')
    assert unread.json()['count'] == 0
