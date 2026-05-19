"""Data provider dispatch — factory functions read settings to return correct provider."""

from typing import Any

from app.core.config import settings
from app.providers.base import BrokerProvider, MarketDataProvider
from app.providers.mock_market import MockMarketDataProvider
from app.providers.yfinance_news import YFinanceNewsProvider
from app.providers.yfinance_provider import YFinanceMarketDataProvider


def get_market_data_provider() -> MarketDataProvider:
    """Return the configured market data provider."""
    name = settings.market_data_provider
    if name == 'yfinance':
        return YFinanceMarketDataProvider()
    return MockMarketDataProvider()


def get_news_provider() -> Any:
    """Return the configured news provider."""
    name = settings.news_data_provider
    if name == 'yfinance':
        return YFinanceNewsProvider()
    return YFinanceNewsProvider()


def get_broker_provider() -> BrokerProvider:
    """Return the configured broker provider."""
    name = settings.broker_provider
    if name == 'alpaca':
        from app.providers.alpaca import AlpacaBrokerProvider

        return AlpacaBrokerProvider()
    raise ValueError(f'Unknown broker provider: {name}')
