import re

import pytest

from app.domain.models import TickerSymbol
from app.providers.mock_market import MockMarketDataProvider


def test_mock_provider_returns_quote_for_valid_ticker():
    provider = MockMarketDataProvider()
    symbol = TickerSymbol(value='AAPL')
    quote = provider.get_quote(symbol)

    assert quote.symbol == 'AAPL'
    assert quote.price > 0
    assert isinstance(quote.change_percent, float)
    assert quote.provider == 'mock'


def test_mock_provider_rejects_invalid_ticker():
    provider = MockMarketDataProvider()

    with pytest.raises(ValueError, match=re.escape('ticker')):
        _ = provider.get_quote(TickerSymbol(value='../AAPL'))
