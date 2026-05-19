"""Research aggregate endpoint for single-stock analysis page."""
import json
from datetime import datetime, timedelta
from typing import Any, cast

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_session
from app.core.deepseek import AnalysisInput, generate_thesis_async
from app.domain import db_models as models
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
        select(models.WatchlistEntry).where(models.WatchlistEntry.symbol == sym)
    )
    if result.scalar_one_or_none() is None:
        raise HTTPException(status_code=404, detail=f'{sym} not in watchlist')

    ts = TickerSymbol(value=sym)

    # 1. Quote from DB or live
    snapshot = await session.execute(
        select(models.PriceSnapshot)
        .where(models.PriceSnapshot.symbol == sym)
        .order_by(models.PriceSnapshot.recorded_at.desc())
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
        select(models.PriceHistory)
        .where(models.PriceHistory.symbol == sym)
        .order_by(models.PriceHistory.date.desc())
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

    # If too few history points in DB, fetch live and persist
    if len(price_history) < 10:
        live_history = _get_provider().get_history(ts, days=90)
        price_history = []
        for e in live_history:
            bar_date_str = e['date'][:10]
            price_history.append({
                'date': bar_date_str,
                'open': e['open'], 'high': e['high'],
                'low': e['low'], 'close': e['close'], 'volume': e['volume'],
            })
            # Persist to DB so future requests don't need to re-fetch
            try:
                bar_date = datetime.strptime(bar_date_str, '%Y-%m-%d').date()
                existing = await session.execute(
                    select(models.PriceHistory)
                    .where(
                        models.PriceHistory.symbol == sym,
                        models.PriceHistory.date == bar_date,
                    )
                    .limit(1)
                )
                if existing.scalar_one_or_none() is None:
                    session.add(models.PriceHistory(
                        symbol=sym,
                        date=bar_date,
                        open_price=e['open'],
                        high_price=e['high'],
                        low_price=e['low'],
                        close_price=e['close'],
                        volume=int(e.get('volume', 0)),
                    ))
            except Exception:
                pass  # Non-blocking persistence
        await session.commit()

    # 3. News for this symbol
    news_result = await session.execute(
        select(models.NewsArticle)
        .where(models.NewsArticle.symbol == sym)
        .order_by(models.NewsArticle.published_at.desc())
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
        select(models.Analysis)
        .where(models.Analysis.symbol == sym)
        .order_by(models.Analysis.created_at.desc())
        .limit(1)
    )
    recent = cast(models.Analysis | None, existing.scalars().first())

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
            select(func.avg(models.NewsArticle.sentiment))
            .where(models.NewsArticle.symbol == sym)
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
    thesis_result = await generate_thesis_async(analysis_input)

    # 6. Store analysis in DB
    analysis = models.Analysis(
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


@router.post('/{symbol}/explain')
async def explain_research(
    symbol: str,
    session: AsyncSession = Depends(get_session),
) -> dict[str, Any]:
    """Generate a beginner-friendly explanation of the analysis."""
    sym = symbol.upper()

    # Check watchlist
    result = await session.execute(
        select(models.WatchlistEntry).where(models.WatchlistEntry.symbol == sym)
    )
    if result.scalar_one_or_none() is None:
        raise HTTPException(status_code=404, detail=f'{sym} not in watchlist')

    # Get latest analysis
    analysis_result = await session.execute(
        select(models.Analysis)
        .where(models.Analysis.symbol == sym)
        .order_by(models.Analysis.created_at.desc())
        .limit(1)
    )
    analysis = analysis_result.scalar_one_or_none()
    if analysis is None:
        return {
            'explanation': f'No analysis found for {sym}. Run research first.',
            'key_takeaways': [],
            'questions_to_ask': [],
        }

    # Get recent news titles
    news_result = await session.execute(
        select(models.NewsArticle)
        .where(models.NewsArticle.symbol == sym)
        .order_by(models.NewsArticle.published_at.desc())
        .limit(5)
    )
    news_titles = [n.title for n in news_result.scalars().all()]

    from app.core.deepseek import generate_explanation

    input_data = {
        'symbol': sym,
        'company_name': sym,
        'technical_score': analysis.technical_score,
        'news_sentiment_score': analysis.news_sentiment_score,
        'fundamental_score': analysis.fundamental_score,
        'macro_score': analysis.macro_score,
        'overall_score': analysis.overall_score,
        'stance': analysis.stance,
        'thesis': analysis.thesis,
        'news_titles': '\n'.join(news_titles) if news_titles else 'No recent news.',
    }

    return generate_explanation(input_data)


@router.get('/{symbol}/earnings-summary')
async def get_earnings_summary(symbol: str) -> dict[str, Any]:
    """Generate AI-powered earnings summary from existing earnings data."""
    sym = symbol.upper()

    from app.providers.finnhub import fetch_earnings as get_earnings

    result = await get_earnings(sym)

    if isinstance(result, dict) and 'error' in result:
        return {'symbol': sym, 'quarterly_trend': None, 'summary': None}

    earnings_raw = result.get('earnings', []) if isinstance(result, dict) else result

    if not earnings_raw or len(earnings_raw) < 2:
        return {
            'symbol': sym,
            'quarterly_trend': None,
            'summary': 'Insufficient earnings history available.',
        }

    beats = 0
    total = 0
    surprises: list[float] = []
    for q in earnings_raw[:8]:
        actual = q.get('actual', 0)
        estimate = q.get('estimate', 0)
        if actual and estimate:
            total += 1
            if actual >= estimate:
                beats += 1
            surprise = round(((actual - estimate) / abs(estimate)) * 100, 1) if estimate else 0
            surprises.append(surprise)

    avg_surprise = round(sum(surprises) / len(surprises), 1) if surprises else 0
    beat_rate = round((beats / total) * 100, 1) if total else 0
    recent = earnings_raw[0] if earnings_raw else {}
    last_surprise = (
        round(
            ((recent.get('actual', 0) - recent.get('estimate', 0)) / abs(recent.get('estimate', 1))) * 100,
            1,
        )
        if recent.get('estimate')
        else 0
    )

    summary = ''
    if avg_surprise > 0:
        summary = (
            f'{sym} has beaten EPS estimates in {beats} of the last {total} quarters '
            f'({beat_rate}%), with an average surprise of +{avg_surprise}%. '
        )
        if last_surprise > avg_surprise:
            summary += (
                f'The most recent quarter showed a +{last_surprise}% beat, '
                'continuing the trend of outperformance. '
            )
        else:
            summary += f'The most recent quarter showed a +{last_surprise}% beat. '
    else:
        summary = (
            f'{sym} has missed EPS estimates in {total - beats} of the last {total} quarters, '
            f'with an average miss of {avg_surprise}%. '
        )

    if avg_surprise > 3:
        summary += 'The company has consistently exceeded expectations, suggesting conservative guidance.'
    elif avg_surprise > 0:
        summary += 'Earnings have generally met or exceeded expectations.'
    else:
        summary += 'The company has struggled to meet analyst expectations.'

    return {
        'symbol': sym,
        'quarterly_trend': {
            'beat_count': beats,
            'total_quarters': total,
            'beat_rate': beat_rate,
            'avg_surprise_pct': avg_surprise,
            'last_surprise_pct': last_surprise,
        },
        'summary': summary,
        'summary_type': 'computed',
    }
