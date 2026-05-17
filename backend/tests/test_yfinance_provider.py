"""Tests for YFinance market data provider."""
from app.domain.models import TickerSymbol
from app.providers.yfinance_provider import YFinanceMarketDataProvider


def test_provider_returns_quote_for_valid_ticker():
    provider = YFinanceMarketDataProvider()
    symbol = TickerSymbol(value='AAPL')
    quote = provider.get_quote(symbol)
    assert quote.symbol == 'AAPL'
    assert quote.price > 0
    assert isinstance(quote.change_percent, float)
    assert quote.provider == 'yfinance'


def test_provider_returns_history_for_valid_ticker():
    provider = YFinanceMarketDataProvider()
    history = provider.get_history(TickerSymbol(value='MSFT'), days=5)
    assert len(history) > 0
    for entry in history:
        assert 'date' in entry
        assert 'open' in entry
        assert 'high' in entry
        assert 'low' in entry
        assert 'close' in entry
        assert 'volume' in entry
