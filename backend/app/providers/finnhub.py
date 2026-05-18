"""Finnhub news and earnings calendar provider."""

from typing import Any

import httpx

from app.core.config import settings

BASE_URL = 'https://finnhub.io/api/v1'


async def fetch_news(symbol: str, count: int = 10) -> dict[str, Any]:
    """Fetch recent news for a symbol from Finnhub."""
    api_key = settings.finnhub_api_key
    if not api_key:
        from app.domain.models import TickerSymbol
        from app.providers.yfinance_news import YFinanceNewsProvider

        provider = YFinanceNewsProvider()
        articles = provider.fetch_news(TickerSymbol(value=symbol.upper()), max_results=count)
        return {'symbol': symbol.upper(), 'source': 'yfinance (fallback)', 'articles': articles}

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f'{BASE_URL}/company-news',
                params={'symbol': symbol.upper(), 'from': '2026-01-01', 'to': '2026-12-31'},
                timeout=10,
            )
            if resp.status_code != 200:
                return {'symbol': symbol.upper(), 'error': 'Finnhub API error'}

            data = resp.json()
            articles = [
                {
                    'title': a.get('headline', ''),
                    'url': a.get('url', ''),
                    'source': a.get('source', ''),
                    'summary': a.get('summary', '')[:500],
                    'published_at': a.get('datetime', ''),
                }
                for a in data[:count]
                if a.get('headline')
            ]

            return {'symbol': symbol.upper(), 'source': 'finnhub', 'articles': articles}
    except Exception as e:
        return {'symbol': symbol.upper(), 'error': str(e)}


async def fetch_earnings(symbol: str) -> dict[str, Any]:
    """Fetch upcoming earnings dates and estimates from Finnhub."""
    api_key = settings.finnhub_api_key
    if not api_key:
        return {
            'symbol': symbol.upper(),
            'note': 'Set FINNHUB_API_KEY for live data',
            'earnings': [
                {'date': '2026-07-28', 'quarter': 'Q3 2026', 'estimate': None},
                {'date': '2026-04-28', 'quarter': 'Q2 2026', 'estimate': 2.15, 'actual': 2.32},
            ],
        }

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f'{BASE_URL}/earnings',
                params={'symbol': symbol.upper()},
                timeout=10,
            )
            if resp.status_code != 200:
                return {'symbol': symbol.upper(), 'error': 'Finnhub API error'}

            data = resp.json()
            earnings = [
                {
                    'date': e.get('date', ''),
                    'quarter': f"Q{e.get('quarter', '')} {e.get('year', '')}",
                    'estimate': e.get('estimate'),
                    'actual': e.get('actual'),
                    'surprise': round(e.get('surprise', 0), 2) if e.get('surprise') else None,
                }
                for e in data[:8]
            ]

            return {'symbol': symbol.upper(), 'source': 'finnhub', 'earnings': earnings}
    except Exception as e:
        return {'symbol': symbol.upper(), 'error': str(e)}


async def fetch_earnings_calendar() -> list[dict[str, Any]]:
    """Fetch upcoming earnings across the market."""
    api_key = settings.finnhub_api_key
    if not api_key:
        return [
            {'symbol': 'AAPL', 'date': '2026-07-28', 'quarter': 'Q3 2026'},
            {'symbol': 'MSFT', 'date': '2026-07-22', 'quarter': 'Q4 2026'},
            {'symbol': 'NVDA', 'date': '2026-08-20', 'quarter': 'Q2 2026'},
            {'symbol': 'GOOGL', 'date': '2026-07-23', 'quarter': 'Q2 2026'},
            {'symbol': 'AMZN', 'date': '2026-07-31', 'quarter': 'Q2 2026'},
            {'symbol': 'META', 'date': '2026-07-30', 'quarter': 'Q2 2026'},
            {'symbol': 'TSLA', 'date': '2026-07-16', 'quarter': 'Q2 2026'},
        ]

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f'{BASE_URL}/calendar/earnings',
                params={},
                timeout=10,
            )
            if resp.status_code != 200:
                return []

            data = resp.json()
            result = []
            for e in (data.get('earningsCalendar') or [])[:20]:
                result.append({
                    'symbol': e.get('symbol', ''),
                    'date': e.get('date', ''),
                    'quarter': e.get('quarter', ''),
                    'estimate': e.get('epsEstimate'),
                })
            return result
    except Exception:
        return []
