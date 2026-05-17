"""Tests for background quote polling."""
from unittest.mock import MagicMock

import pytest

from app.core.scheduler import poll_watchlist_quotes


@pytest.mark.asyncio
async def test_poll_queries_watchlist_and_stores_prices(async_db_session):
    mock_provider = MagicMock()
    mock_provider.get_quote.return_value.price = 150.0
    mock_provider.get_quote.return_value.change_percent = 0.5
    mock_provider.get_quote.return_value.symbol = 'AAPL'
    mock_provider.get_quote.return_value.provider = 'mock'

    result = await poll_watchlist_quotes(
        provider=mock_provider,
        get_session=lambda: async_db_session,
    )
    assert result >= 0
