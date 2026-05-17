"""Tests for news ingestion scheduler."""
import pytest

from app.core.scheduler import poll_watchlist_news


@pytest.mark.asyncio
async def test_poll_news_returns_zero_for_empty_watchlist(async_db_session):
    result = await poll_watchlist_news(get_session=lambda: async_db_session)
    assert result == 0
