"""Unit tests for pattern detection algorithms."""

from app.domain.patterns import detect_patterns, find_pivot_highs, find_pivot_lows


def test_find_pivot_highs() -> None:
    data = [1, 2, 3, 4, 5, 4, 3, 2, 1]
    pivots = find_pivot_highs(data, data, window=2)
    assert len(pivots) > 0
    assert data[pivots[0]] == max(data)


def test_find_pivot_lows() -> None:
    data = [5, 4, 3, 2, 1, 2, 3, 4, 5]
    pivots = find_pivot_lows(data, data, window=2)
    assert len(pivots) > 0
    assert data[pivots[0]] == min(data)


def test_detect_double_top() -> None:
    # Create synthetic double top pattern
    prices = []
    for i in range(50):
        if 10 <= i <= 15:
            base = 100 + (i - 10) * 5
        elif 15 < i <= 20:
            base = 125 - (i - 15) * 5
        elif 25 <= i <= 30:
            base = 100 + (i - 25) * 5
        elif 30 < i <= 35:
            base = 125 - (i - 30) * 5
        else:
            base = 100
        prices.append({
            'high': base + 2, 'low': base - 2, 'close': base,
            'open': base, 'volume': 1000000, 'date': f'2025-0{i+1:02d}',
        })

    patterns = detect_patterns(prices)
    types = [p['type'] for p in patterns]
    assert 'double_top' in types


def test_detect_double_bottom() -> None:
    # Create synthetic double bottom pattern
    prices = []
    for i in range(50):
        if 10 <= i <= 15:
            base = 100 - (i - 10) * 5
        elif 15 < i <= 20:
            base = 75 + (i - 15) * 5
        elif 25 <= i <= 30:
            base = 100 - (i - 25) * 5
        elif 30 < i <= 35:
            base = 75 + (i - 30) * 5
        else:
            base = 100
        prices.append({
            'high': base + 2, 'low': base - 2, 'close': base,
            'open': base, 'volume': 1000000, 'date': f'2025-0{i+1:02d}',
        })

    patterns = detect_patterns(prices)
    types = [p['type'] for p in patterns]
    assert 'double_bottom' in types


def test_detect_bull_flag() -> None:
    # Create synthetic bull flag: sharp rise then tight consolidation
    prices = []
    for i in range(30):
        if i < 10:
            base = 100 + i * 3  # sharp rise
        elif i < 15:
            base = 130  # consolidation
        else:
            base = 100
        prices.append({
            'high': base + 1, 'low': base - 1, 'close': base,
            'open': base, 'volume': 1000000, 'date': f'2025-0{i+1:02d}',
        })

    patterns = detect_patterns(prices)
    types = [p['type'] for p in patterns]
    assert 'bull_flag' in types


def test_detect_hammer() -> None:
    prices = []
    for i in range(30):
        base = 100
        if i == 15:
            # Hammer candle: long lower wick, tiny upper wick
            prices.append({
                'high': 101, 'low': 95, 'close': 101,
                'open': 100, 'volume': 1000000, 'date': '2025-03-16',
            })
        else:
            prices.append({
                'high': base + 1, 'low': base - 1, 'close': base,
                'open': base, 'volume': 1000000, 'date': f'2025-0{i+1:02d}',
            })

    patterns = detect_patterns(prices)
    types = [p['type'] for p in patterns]
    assert 'hammer' in types


def test_detect_shooting_star() -> None:
    prices = []
    for i in range(30):
        base = 100
        if i == 15:
            # Shooting star: long upper wick, tiny lower wick
            prices.append({
                'high': 106, 'low': 100, 'close': 100,
                'open': 101, 'volume': 1000000, 'date': '2025-03-16',
            })
        else:
            prices.append({
                'high': base + 1, 'low': base - 1, 'close': base,
                'open': base, 'volume': 1000000, 'date': f'2025-0{i+1:02d}',
            })

    patterns = detect_patterns(prices)
    types = [p['type'] for p in patterns]
    assert 'shooting_star' in types


def test_empty_patterns_for_short_data() -> None:
    prices = [
        {'high': 100, 'low': 99, 'close': 99.5, 'open': 100,
         'volume': 1000, 'date': '2025-01-01'},
    ]
    patterns = detect_patterns(prices)
    assert patterns == []
