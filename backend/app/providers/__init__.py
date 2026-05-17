"""Data provider dispatch — factory functions read settings to return correct provider."""

from app.core.config import settings
from app.providers.base import MarketDataProvider
from app.providers.mock_market import MockMarketDataProvider
from app.providers.yfinance_provider import YFinanceMarketDataProvider
from app.providers.yfinance_news import YFinanceNewsProvider


def get_market_data_provider() -> MarketDataProvider:
    """Return the configured market data provider."""
    name = settings.market_data_provider
    if name == 'yfinance':
        return YFinanceMarketDataProvider()
    return MockMarketDataProvider()


def get_news_provider():
    """Return the configured news provider."""
    name = settings.news_data_provider
    if name == 'yfinance':
        return YFinanceNewsProvider()
    return YFinanceNewsProvider()
