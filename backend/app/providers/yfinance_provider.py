"""Real market data provider using yfinance."""
from typing import Any

import yfinance as yf

from app.domain.models import TickerSymbol
from app.providers.base import MarketDataProvider, Quote


class YFinanceMarketDataProvider(MarketDataProvider):
    provider_name = 'yfinance'

    def get_quote(self, symbol: TickerSymbol) -> Quote:
        ticker = yf.Ticker(symbol.value)
        info = ticker.info or {}
        price = info.get('currentPrice') or info.get('regularMarketPrice') or 0.0
        previous_close = info.get('previousClose') or price or 1.0
        change_percent = (
            ((price - previous_close) / previous_close) * 100 if previous_close else 0.0
        )
        if not price or price <= 0:
            fast_info = ticker.fast_info
            price = getattr(fast_info, 'last_price', 0.0) or 0.0
        return Quote(
            symbol=symbol.value,
            price=round(float(price), 2),
            change_percent=round(float(change_percent), 2),
            provider=self.provider_name,
        )

    def get_history(self, symbol: TickerSymbol, days: int = 30) -> list[dict[str, Any]]:
        ticker = yf.Ticker(symbol.value)
        hist = ticker.history(period=f'{max(days, 5)}d')
        result: list[dict[str, Any]] = []
        for date, row in hist.iterrows():
            result.append({
                'date': date.strftime('%Y-%m-%d'),
                'open': round(float(row['Open']), 2),
                'high': round(float(row['High']), 2),
                'low': round(float(row['Low']), 2),
                'close': round(float(row['Close']), 2),
                'volume': int(row['Volume']),
            })
        return result
