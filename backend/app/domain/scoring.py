"""Factor scoring for stock analysis."""
from typing import Any

from app.domain.models import TickerSymbol


def compute_factor_scores(
    symbol: TickerSymbol,
    price_change_pct: float | None = None,
    avg_news_sentiment: float | None = None,
) -> dict[str, Any]:
    """Compute factor scores using real price/news data when available.

    Technical score uses price change, news sentiment uses average news sentiment.
    Fundamentals and macro remain stubs returning moderate scores.
    All scores are clamped to [0.0, 1.0].
    """
    # Technical: use price change if available, else deterministic stub
    if price_change_pct is not None:
        # Map price_change_pct (e.g. -10..+10) to 0..1
        raw_tech = 0.5 + (price_change_pct / 20.0)
        technical_score = max(0.0, min(1.0, round(raw_tech, 2)))
    else:
        seed = sum(ord(c) for c in symbol.value)
        rng = _seeded_random(seed)
        technical_score = round(rng[0] * 0.3 + 0.5, 2)

    # News sentiment: use avg sentiment if available
    if avg_news_sentiment is not None:
        # Map avg_news_sentiment (typically -1..1) to 0..1
        raw_news = 0.5 + (avg_news_sentiment / 2.0)
        news_score = max(0.0, min(1.0, round(raw_news, 2)))
    else:
        seed = sum(ord(c) for c in symbol.value)
        rng = _seeded_random(seed)
        news_score = round(rng[1] * 0.4 + 0.3, 2)

    # Fundamentals and macro — deterministic stubs
    seed = sum(ord(c) for c in symbol.value)
    rng = _seeded_random(seed)
    fundamental_score = round(rng[2] * 0.3 + 0.4, 2)
    macro_score = round(rng[3] * 0.2 + 0.4, 2)

    overall = round(
        technical_score * 0.3
        + news_score * 0.25
        + fundamental_score * 0.25
        + macro_score * 0.2,
        2,
    )

    return {
        'technical': {
            'score': technical_score,
            'explanation': 'Based on recent price momentum and volume trends.',
        },
        'news_sentiment': {
            'score': news_score,
            'explanation': 'Aggregated sentiment from recent news coverage.',
        },
        'fundamentals': {
            'score': fundamental_score,
            'explanation': 'Valuation metrics and earnings trajectory.',
        },
        'macro': {
            'score': macro_score,
            'explanation': 'Sector and macroeconomic conditions.',
        },
        'overall': overall,
    }


def _seeded_random(seed: int) -> list[float]:
    """Simple deterministic pseudo-random for reproducible scoring."""
    results = []
    for i in range(4):
        h = (seed * 1103515245 + (i * 12345)) & 0x7fffffff
        results.append(h / 0x7fffffff)
    return results
