"""Tests for provider factory dispatch."""

from app.core.config import settings
from app.providers import get_market_data_provider
from app.providers.mock_market import MockMarketDataProvider
from app.providers.yfinance_provider import YFinanceMarketDataProvider


def test_factory_returns_mock_when_configured(monkeypatch):
    monkeypatch.setattr(settings, 'market_data_provider', 'mock')
    provider = get_market_data_provider()
    assert isinstance(provider, MockMarketDataProvider)


def test_factory_returns_yfinance_when_configured(monkeypatch):
    monkeypatch.setattr(settings, 'market_data_provider', 'yfinance')
    provider = get_market_data_provider()
    assert isinstance(provider, YFinanceMarketDataProvider)


def test_factory_fallback_for_unknown_config(monkeypatch):
    monkeypatch.setattr(settings, 'market_data_provider', 'unknown')
    provider = get_market_data_provider()
    assert isinstance(provider, MockMarketDataProvider)
