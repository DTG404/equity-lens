"""Social sentiment provider using StockTwits API."""

from typing import Any

import httpx

STOCKTWITS_URL = 'https://api.stocktwits.com/api/2/streams/symbol/{}.json'


def get_sentiment(symbol: str) -> dict[str, Any]:
    """Fetch social sentiment data for a symbol from StockTwits."""
    try:
        resp = httpx.get(STOCKTWITS_URL.format(symbol.upper()), timeout=10)
        if resp.status_code != 200:
            return {'symbol': symbol.upper(), 'error': 'No data available'}

        data = resp.json()
        messages = data.get('messages', [])

        bullish = 0
        bearish = 0
        total = 0
        recent: list[dict[str, Any]] = []

        for msg in messages[:20]:
            entities = msg.get('entities') or {}
            sentiment = entities.get('sentiment') or {}
            basic = sentiment.get('basic', 'Neutral')
            if basic == 'Bullish':
                bullish += 1
            elif basic == 'Bearish':
                bearish += 1
            total += 1

            recent.append({
                'body': msg.get('body', '')[:200],
                'sentiment': basic,
                'user': msg.get('user', {}).get('username', ''),
                'created_at': msg.get('created_at', ''),
            })

        bull_pct = round((bullish / total) * 100, 1) if total > 0 else 0
        bear_pct = round((bearish / total) * 100, 1) if total > 0 else 0
        score = round((bullish - bearish) / max(total, 1), 2)

        return {
            'symbol': symbol.upper(),
            'total_messages': total,
            'bullish': bullish,
            'bearish': bearish,
            'bullish_pct': bull_pct,
            'bearish_pct': bear_pct,
            'score': score,  # -1 to +1
            'messages': recent,
        }
    except Exception as e:
        return {'symbol': symbol.upper(), 'error': str(e)}
