"""Tests for NewsArticle model."""
from datetime import UTC, datetime

import pytest
from sqlalchemy import select

from app.domain.db_models import NewsArticle


@pytest.mark.asyncio
async def test_news_article_round_trip(async_db_session):
    article = NewsArticle(
        symbol='AAPL',
        title='Apple reports record quarterly results',
        url='https://example.com/apple-earnings',
        source='Yahoo Finance',
        summary='Apple reported strong Q2 earnings...',
        published_at=datetime(2025, 3, 15, tzinfo=UTC),
    )
    async_db_session.add(article)
    await async_db_session.commit()

    result = await async_db_session.execute(
        select(NewsArticle).where(NewsArticle.symbol == 'AAPL')
    )
    saved = result.scalar_one()
    assert saved.title == 'Apple reports record quarterly results'
    assert saved.url == 'https://example.com/apple-earnings'


@pytest.mark.asyncio
async def test_news_article_deduplicates_by_url(async_db_session):
    article1 = NewsArticle(
        symbol='AAPL',
        title='First',
        url='https://example.com/same',
        published_at=datetime(2025, 3, 15, tzinfo=UTC),
    )
    article2 = NewsArticle(
        symbol='AAPL',
        title='Second',
        url='https://example.com/same',
        published_at=datetime(2025, 3, 15, tzinfo=UTC),
    )
    async_db_session.add(article1)
    await async_db_session.commit()

    # Verify URL uniqueness constraint
    async_db_session.add(article2)
    with pytest.raises(Exception):
        await async_db_session.commit()
    await async_db_session.rollback()
