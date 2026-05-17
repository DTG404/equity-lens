from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from app.domain.models import TickerSymbol
from app.providers.base import Quote


class MockMarketDataProvider:
    """Local-only mock market data provider for development and testing.

    Returns deterministic quote and history data. Does not fetch from any external API.
    No trade execution capability.
    """

    def get_quote(self, symbol: TickerSymbol) -> Quote:
        if symbol.value == 'AAPL':
            price = 198.50
            change = 1.2
        elif symbol.value == 'MSFT':
            price = 425.30
            change = -0.5
        elif symbol.value == 'NVDA':
            price = 875.60
            change = 3.4
        else:
            price = 100.00
            change = 0.0

        return Quote(
            symbol=symbol.value,
            price=price,
            change_percent=change,
            provider='mock',
        )

    def get_history(self, symbol: TickerSymbol, days: int = 30) -> list[dict[str, Any]]:
        """Return deterministic price history for testing."""
        result: list[dict[str, Any]] = []
        base_price = self.get_quote(symbol).price
        for i in range(days):
            d = (datetime.now() - timedelta(days=days - i - 1)).strftime('%Y-%m-%d')
            noise = (i % 7) * 0.5
            result.append({
                'date': d,
                'open': round(base_price - 0.5 + noise, 2),
                'high': round(base_price + 1.0 + noise, 2),
                'low': round(base_price - 1.0 + noise, 2),
                'close': round(base_price + noise, 2),
                'volume': 1000000 + i * 1000,
            })
        return result
