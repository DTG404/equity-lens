"""Research aggregate endpoint for single-stock analysis page."""
import json
from datetime import datetime, timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_session
from app.core.deepseek import AnalysisInput, generate_thesis
from app.domain.db_models import Analysis, NewsArticle, PriceHistory, PriceSnapshot, WatchlistEntry
from app.domain.models import TickerSymbol
from app.domain.scoring import compute_factor_scores
from app.providers import get_market_data_provider
from app.providers.base import MarketDataProvider

router = APIRouter(prefix='/research', tags=['research'])

def _get_provider() -> MarketDataProvider:
    return get_market_data_provider()


@router.get('/{symbol}')
async def get_research(
    symbol: str,
    force: bool = False,
    session: AsyncSession = Depends(get_session),
) -> dict[str, Any]:
    sym = symbol.upper()
    result = await session.execute(
        select(WatchlistEntry).where(WatchlistEntry.symbol == sym)
    )
    if result.scalar_one_or_none() is None:
        raise HTTPException(status_code=404, detail=f'{sym} not in watchlist')

    ts = TickerSymbol(value=sym)

    # 1. Quote from DB or live
    snapshot = await session.execute(
        select(PriceSnapshot)
        .where(PriceSnapshot.symbol == sym)
        .order_by(PriceSnapshot.recorded_at.desc())
        .limit(1)
    )
    row = snapshot.scalar_one_or_none()
    if row is not None:
        quote = {
            'symbol': row.symbol, 'price': row.price,
            'change_percent': row.change_percent, 'provider': row.provider,
        }
    else:
        q = _get_provider().get_quote(ts)
        quote = {
            'symbol': q.symbol, 'price': q.price,
            'change_percent': q.change_percent, 'provider': q.provider,
        }

    # 2. Price history from DB
    history_result = await session.execute(
        select(PriceHistory)
        .where(PriceHistory.symbol == sym)
        .order_by(PriceHistory.date.desc())
        .limit(90)
    )
    price_history = [
        {
            'date': str(h.date) if not hasattr(h.date, 'isoformat') else str(h.date)[:10],
            'open': h.open_price, 'high': h.high_price,
            'low': h.low_price, 'close': h.close_price, 'volume': h.volume,
        }
        for h in reversed(list(history_result.scalars().all()))
    ]

    # If no history in DB, fetch live
    if not price_history:
        live_history = _get_provider().get_history(ts, days=30)
        price_history = [
            {'date': e['date'], 'close': e['close'],
             'open': e['open'], 'high': e['high'],
             'low': e['low'], 'volume': e['volume']}
            for e in live_history
        ]

    # 3. News for this symbol
    news_result = await session.execute(
        select(NewsArticle)
        .where(NewsArticle.symbol == sym)
        .order_by(NewsArticle.published_at.desc())
        .limit(10)
    )
    news_items = [
        {
            'id': a.id, 'title': a.title, 'url': a.url,
            'source': a.source, 'summary': a.summary,
            'published_at': a.published_at.isoformat() if a.published_at else None,
        }
        for a in news_result.scalars().all()
    ]

    # Cache: return existing analysis created within the last hour
    one_hour_ago = datetime.utcnow() - timedelta(hours=1)
    existing = await session.execute(
        select(Analysis)
        .where(Analysis.symbol == sym)
        .order_by(Analysis.created_at.desc())
        .limit(1)
    )
    recent = existing.scalar_one_or_none()

    risks = (
        'Key risks include sector headwinds, macroeconomic uncertainty, '
        'and company-specific execution risk.'
    )

    if recent and recent.created_at > one_hour_ago and not force:
        cached_scores = {
            'technical': {'score': recent.technical_score, 'explanation': ''},
            'news_sentiment': {'score': recent.news_sentiment_score, 'explanation': ''},
            'fundamentals': {'score': recent.fundamental_score, 'explanation': ''},
            'macro': {'score': recent.macro_score, 'explanation': ''},
            'overall': recent.overall_score,
        }
        return {
            'symbol': recent.symbol,
            'quote': quote,
            'price_history': price_history,
            'news': news_items,
            'scores': cached_scores,
            'thesis': recent.thesis,
            'risks': risks,
            'scenarios': {
                'bull_case': recent.bull_case,
                'base_case': recent.base_case,
                'bear_case': recent.bear_case,
                'model': recent.model_used,
            },
            'analysis_id': recent.id,
            'analysis_created_at': recent.created_at.isoformat(),
        }

    # 4. Compute scores from real data
    price_change_pct: float | None = None
    raw_change = quote.get('change_percent')
    if raw_change is not None:
        price_change_pct = float(raw_change)  # type: ignore[arg-type]

    avg_news_sentiment: float | None = None
    if news_items:
        sentiment_result = await session.execute(
            select(func.avg(NewsArticle.sentiment))
            .where(NewsArticle.symbol == sym)
        )
        avg_val = sentiment_result.scalar()
        if avg_val is not None:
            avg_news_sentiment = float(avg_val)

    scores = compute_factor_scores(
        ts,
        price_change_pct=price_change_pct,
        avg_news_sentiment=avg_news_sentiment,
    )
    overall = scores['overall']
    if overall >= 0.65:
        stance = 'bullish'
    elif overall >= 0.45:
        stance = 'neutral'
    else:
        stance = 'bearish'

    # 5. Generate thesis via DeepSeek or fallback
    news_titles: list[str] = [str(n['title']) for n in news_items if n['title'] is not None]
    analysis_input = AnalysisInput(
        symbol=sym,
        company_name='',
        technical_score=scores['technical']['score'],
        news_sentiment_score=scores['news_sentiment']['score'],
        fundamental_score=scores['fundamentals']['score'],
        macro_score=scores['macro']['score'],
        overall_score=overall,
        recent_news_titles=news_titles,
    )
    thesis_result = generate_thesis(analysis_input)

    # 6. Store analysis in DB
    analysis = Analysis(
        symbol=sym,
        technical_score=scores['technical']['score'],
        news_sentiment_score=scores['news_sentiment']['score'],
        fundamental_score=scores['fundamentals']['score'],
        macro_score=scores['macro']['score'],
        overall_score=overall,
        stance=stance,
        thesis=thesis_result.get('thesis', ''),
        bull_case=thesis_result.get('bull_case', ''),
        base_case=thesis_result.get('base_case', ''),
        bear_case=thesis_result.get('bear_case', ''),
        model_used=thesis_result.get('model', 'fallback'),
        input_snapshot=json.dumps({
            'symbol': sym,
            'price_change_pct': price_change_pct,
            'avg_news_sentiment': avg_news_sentiment,
        }),
    )
    session.add(analysis)
    await session.flush()
    analysis_id = analysis.id

    return {
        'symbol': sym,
        'quote': quote,
        'price_history': price_history,
        'news': news_items,
        'scores': scores,
        'thesis': thesis_result.get('thesis', ''),
        'risks': risks,
        'scenarios': {
            'bull_case': thesis_result.get('bull_case', ''),
            'base_case': thesis_result.get('base_case', ''),
            'bear_case': thesis_result.get('bear_case', ''),
            'model': thesis_result.get('model', 'fallback'),
        },
        'analysis_id': analysis_id,
        'analysis_created_at': analysis.created_at.isoformat(),
    }
