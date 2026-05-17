"""Tests for research aggregate endpoint."""
import pytest
from httpx import ASGITransport, AsyncClient

from app.domain.db_models import NewsArticle, PriceSnapshot
from app.main import app


@pytest.fixture
async def client() -> AsyncClient:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url='http://test') as ac:
        yield ac


@pytest.mark.asyncio
async def test_research_returns_aggregated_data(client: AsyncClient):
    await client.post('/api/watchlist', json={'symbol': 'AAPL'})
    response = await client.get('/api/research/AAPL')
    assert response.status_code == 200
    data = response.json()
    assert 'symbol' in data
    assert 'quote' in data
    assert 'price_history' in data
    assert 'news' in data
    assert 'scores' in data
    assert 'thesis' in data
    assert 'risks' in data
    assert 'scenarios' in data
    assert 'analysis_id' in data
    assert data['symbol'] == 'AAPL'

    scenarios = data['scenarios']
    assert 'bull_case' in scenarios
    assert 'base_case' in scenarios
    assert 'bear_case' in scenarios
    assert 'model' in scenarios


@pytest.mark.asyncio
async def test_research_for_unwatched_returns_404(client: AsyncClient):
    response = await client.get('/api/research/ZZZZ')
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_research_with_db_data_uses_real_scoring(
    client: AsyncClient, async_db_session
):
    await client.post('/api/watchlist', json={'symbol': 'AAPL'})

    import datetime


    async_db_session.add(PriceSnapshot(
        symbol='AAPL', price=150.0, change_percent=3.5,
        provider='test', recorded_at=datetime.datetime.now(tz=datetime.UTC),
    ))
    async_db_session.add(NewsArticle(
        symbol='AAPL', title='Apple strong earnings',
        url='http://example.com/aapl1', sentiment=0.8,
        published_at=datetime.datetime.now(tz=datetime.UTC),
    ))
    async_db_session.add(NewsArticle(
        symbol='AAPL', title='Apple product launch',
        url='http://example.com/aapl2', sentiment=0.6,
        published_at=datetime.datetime.now(tz=datetime.UTC),
    ))
    await async_db_session.commit()

    response = await client.get('/api/research/AAPL')
    assert response.status_code == 200
    data = response.json()

    scores = data['scores']
    assert scores['technical']['score'] > 0.5
    assert scores['news_sentiment']['score'] > 0.5
    assert 'analysis_id' in data
    assert data['analysis_id'] is not None
