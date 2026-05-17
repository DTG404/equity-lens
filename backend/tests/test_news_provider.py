"""Tests for news providers."""
from app.domain.models import TickerSymbol
from app.providers.yfinance_news import YFinanceNewsProvider


def test_yfinance_news_returns_articles_for_ticker():
    provider = YFinanceNewsProvider()
    articles = provider.fetch_news(TickerSymbol(value='AAPL'), max_results=3)
    assert len(articles) > 0
    for article in articles:
        assert 'title' in article
        assert 'url' in article
        assert 'source' in article
        assert 'published_at' in article
