"""News provider using yfinance ticker news."""
from datetime import UTC, datetime
from typing import Any

import yfinance as yf

from app.domain.models import TickerSymbol


class YFinanceNewsProvider:
    provider_name = 'yfinance'

    def fetch_news(self, symbol: TickerSymbol, max_results: int = 10) -> list[dict[str, Any]]:
        ticker = yf.Ticker(symbol.value)
        news = getattr(ticker, 'news', []) or []
        results: list[dict[str, Any]] = []
        for item in news[:max_results]:
            content = item.get('content', item)
            title = content.get('title', '')
            canonical = content.get('canonicalUrl')
            url = (
                canonical.get('url', '')
                if isinstance(canonical, dict)
                else content.get('link', '')
            )
            provider_data = content.get('provider')
            source = (
                provider_data.get('displayName', 'Yahoo Finance')
                if isinstance(provider_data, dict)
                else 'Yahoo Finance'
            )
            summary = content.get('summary', '') or content.get('description', '') or ''
            pub_time = content.get('pubDate', 0)
            if isinstance(pub_time, (int, float)):
                published_at = datetime.fromtimestamp(pub_time, tz=UTC)
            else:
                published_at = datetime.now(UTC)

            if title and url:
                results.append({
                    'title': title,
                    'url': url,
                    'source': source,
                    'summary': summary,
                    'published_at': published_at,
                })
        return results
