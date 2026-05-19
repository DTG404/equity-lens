"""Chart pattern detection algorithms using rule-based swing point analysis."""

from typing import Any


def find_pivot_highs(lows: list[float], highs: list[float], window: int = 5) -> list[int]:
    """Find pivot high indices using a rolling window."""
    pivots: list[int] = []
    for i in range(window, len(highs) - window):
        if all(highs[i] >= highs[i - j] for j in range(1, window + 1)) and \
           all(highs[i] >= highs[i + j] for j in range(1, window + 1)):
            pivots.append(i)
    return pivots


def find_pivot_lows(lows: list[float], highs: list[float], window: int = 5) -> list[int]:
    """Find pivot low indices using a rolling window."""
    pivots: list[int] = []
    for i in range(window, len(lows) - window):
        if all(lows[i] <= lows[i - j] for j in range(1, window + 1)) and \
           all(lows[i] <= lows[i + j] for j in range(1, window + 1)):
            pivots.append(i)
    return pivots


def detect_patterns(prices: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Detect chart patterns in price history data.

    Each price dict must have: 'high', 'low', 'close', 'date' (ISO string).
    """
    if len(prices) < 30:
        return []

    highs = [p['high'] for p in prices]
    lows = [p['low'] for p in prices]
    closes = [p['close'] for p in prices]
    dates = [p.get('date', str(i)) for i, p in enumerate(prices)]

    pivot_highs = find_pivot_highs(lows, highs, window=3)
    pivot_lows = find_pivot_lows(lows, highs, window=3)

    patterns: list[dict[str, Any]] = []

    # Double Top: two peaks at similar price level
    for i in range(len(pivot_highs) - 1):
        h1_idx = pivot_highs[i]
        h2_idx = pivot_highs[i + 1]
        h1 = highs[h1_idx]
        h2 = highs[h2_idx]
        if abs(h1 - h2) / max(h1, h2) < 0.03 and (h2_idx - h1_idx) > 3:
            neckline = min(lows[h1_idx:h2_idx + 1])
            patterns.append({
                'type': 'double_top',
                'direction': 'bearish',
                'confidence': round(0.6 + abs(h1 - h2) / max(h1, h2), 2),
                'detected_at': dates[h2_idx],
                'target_price': round(neckline - (h1 - neckline), 2),
            })

    # Double Bottom: two troughs at similar price level
    for i in range(len(pivot_lows) - 1):
        l1_idx = pivot_lows[i]
        l2_idx = pivot_lows[i + 1]
        l1 = lows[l1_idx]
        l2 = lows[l2_idx]
        if abs(l1 - l2) / max(l1, l2) < 0.03 and (l2_idx - l1_idx) > 3:
            neckline = max(highs[l1_idx:l2_idx + 1])
            patterns.append({
                'type': 'double_bottom',
                'direction': 'bullish',
                'confidence': round(0.6 + abs(l1 - l2) / max(l1, l2), 2),
                'detected_at': dates[l2_idx],
                'target_price': round(neckline + (neckline - l1), 2),
            })

    # Bull Flag: sharp rise then tight consolidation
    for i in range(10, len(prices) - 5):
        rise = (closes[i] - closes[i - 10]) / closes[i - 10]
        if rise > 0.05:
            consolidation = closes[i:i + 5]
            retrace = max(consolidation) - min(consolidation)
            avg_move = sum(abs(closes[j] - closes[j - 1]) for j in range(i - 5, i)) / 5
            if retrace < avg_move * 1.5:
                patterns.append({
                    'type': 'bull_flag',
                    'direction': 'bullish',
                    'confidence': round(0.5 + rise, 2),
                    'detected_at': dates[i + 4],
                    'target_price': round(closes[i + 4] + rise * 1.5, 2),
                })

    # Hammer: long lower wick, small body at top
    for i in range(len(prices)):
        body = abs(closes[i] - prices[i]['open'])
        lower_wick = min(closes[i], prices[i]['open']) - lows[i]
        upper_wick = highs[i] - max(closes[i], prices[i]['open'])
        if lower_wick > body * 2 and upper_wick < body * 0.5 and body > 0:
            patterns.append({
                'type': 'hammer',
                'direction': 'bullish',
                'confidence': 0.5,
                'detected_at': dates[i],
                'target_price': round(highs[i] + lower_wick, 2),
            })

    # Shooting Star: long upper wick, small body at bottom
    for i in range(len(prices)):
        body = abs(closes[i] - prices[i]['open'])
        upper_wick = highs[i] - max(closes[i], prices[i]['open'])
        lower_wick = min(closes[i], prices[i]['open']) - lows[i]
        if upper_wick > body * 2 and lower_wick < body * 0.5 and body > 0:
            patterns.append({
                'type': 'shooting_star',
                'direction': 'bearish',
                'confidence': 0.5,
                'detected_at': dates[i],
                'target_price': round(lows[i] - upper_wick, 2),
            })

    return patterns
