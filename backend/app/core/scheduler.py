"""Background scheduler for periodic quote polling."""
import asyncio
import logging
from collections.abc import Callable
from datetime import UTC, datetime
from typing import Any

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.db import _async_session_factory, init_db
from app.domain.db_models import (
    AlertEvent,
    AlertRule,
    Analysis,
    PriceHistory,
    PriceSnapshot,
    SignalOutcome,
    WatchlistEntry,
)
from app.domain.models import TickerSymbol

logger = logging.getLogger(__name__)


async def poll_watchlist_quotes(
    provider: Any | None = None,
    get_session: Callable[[], AsyncSession] | None = None,
) -> int:
    """Poll quotes for all watchlist entries and store in PriceSnapshot."""
    from app.providers import get_market_data_provider

    prov = provider or get_market_data_provider()

    if get_session is not None:
        session = get_session()
        return await _do_poll(session, prov)

    if _async_session_factory is None:
        await init_db()
    assert _async_session_factory is not None
    async with _async_session_factory() as session:
        return await _do_poll(session, prov)


async def _do_poll(session: AsyncSession, provider: Any) -> int:
    result = await session.execute(select(WatchlistEntry.symbol))
    symbols = [row[0] for row in result.all()]

    count = 0
    for symbol in symbols:
        try:
            ts = TickerSymbol(value=symbol)
            quote = provider.get_quote(ts)
            snapshot = PriceSnapshot(
                symbol=quote.symbol,
                price=quote.price,
                change_percent=quote.change_percent,
                provider=quote.provider,
            )
            session.add(snapshot)

            from datetime import date
            today = date.today()
            existing_bar = await session.execute(
                select(PriceHistory)
                .where(
                    PriceHistory.symbol == symbol,
                    PriceHistory.date == today,
                )
                .limit(1)
            )
            if existing_bar.scalar_one_or_none() is None:
                price = quote.price
                bar = PriceHistory(
                    symbol=symbol,
                    date=today,
                    open_price=price,
                    high_price=price,
                    low_price=price,
                    close_price=price,
                    volume=0,
                )
                session.add(bar)
            count += 1
        except Exception as e:
            logger.warning('Failed to poll %s: %s', symbol, e)
    await session.commit()
    return count


async def evaluate_alerts(
    get_session: Callable[[], AsyncSession] | None = None,
) -> int:
    """Evaluate all enabled alert rules against latest price data.

    For MVP, only price alert_type is evaluated. Other types are stored
    for future implementation when their data sources are live.
    """
    if get_session is not None:
        session = get_session()
        return await _do_evaluate(session)

    if _async_session_factory is None:
        await init_db()
    assert _async_session_factory is not None
    async with _async_session_factory() as session:
        return await _do_evaluate(session)


async def _do_evaluate(session: AsyncSession) -> int:
    result = await session.execute(
        select(AlertRule).where(AlertRule.enabled.is_(True))
    )
    rules = result.scalars().all()

    count = 0
    for rule in rules:
        try:
            if rule.alert_type != 'price':
                continue

            price_result = await session.execute(
                select(PriceSnapshot)
                .where(PriceSnapshot.symbol == rule.symbol)
                .order_by(PriceSnapshot.recorded_at.desc())
                .limit(1)
            )
            snapshot = price_result.scalar_one_or_none()
            if snapshot is None:
                continue

            triggered = False
            if rule.condition == 'above' and snapshot.price > rule.threshold:
                triggered = True
            elif rule.condition == 'below' and snapshot.price < rule.threshold:
                triggered = True

            if triggered:
                direction = 'exceeded' if rule.condition == 'above' else 'fell below'
                event = AlertEvent(
                    rule_id=rule.id,
                    symbol=rule.symbol,
                    alert_type=rule.alert_type,
                    message=(
                        f'{rule.symbol} {direction} ${rule.threshold:.2f} '
                        f'(current: ${snapshot.price:.2f})'
                    ),
                    severity='warning',
                )
                session.add(event)
                count += 1
        except Exception as e:
            logger.warning('Failed to evaluate rule %d: %s', rule.id, e)

    await session.commit()
    return count


async def poll_watchlist_news(
    get_session: Callable[[], AsyncSession] | None = None,
) -> int:
    """Fetch news for all watchlist entries and store new articles."""
    from app.providers import get_news_provider

    provider = get_news_provider()

    if get_session is not None:
        session = get_session()
        return await _do_poll_news(session, provider)

    if _async_session_factory is None:
        await init_db()
    assert _async_session_factory is not None
    async with _async_session_factory() as session:
        return await _do_poll_news(session, provider)


async def _do_poll_news(session: AsyncSession, provider: Any) -> int:
    from app.domain.db_models import NewsArticle

    result = await session.execute(
        select(WatchlistEntry.symbol)
    )
    symbols = [row[0] for row in result.all()]

    count = 0
    for symbol in symbols:
        try:
            ts = TickerSymbol(value=symbol)
            articles = provider.fetch_news(ts, max_results=5)
            for article in articles:
                existing = await session.execute(
                    select(NewsArticle).where(NewsArticle.url == article['url'])
                )
                if existing.scalar_one_or_none() is not None:
                    continue
                news_item = NewsArticle(
                    symbol=symbol,
                    title=article['title'],
                    url=article['url'],
                    source=article['source'],
                    summary=article['summary'],
                    published_at=article['published_at'],
                )
                session.add(news_item)
                count += 1
        except Exception as e:
            logger.warning('Failed to fetch news for %s: %s', symbol, e)
    await session.commit()
    return count


async def evaluate_signal_outcomes(
    get_session: Callable[[], AsyncSession] | None = None,
) -> int:
    """Evaluate past analysis stances against current price data.

    For each analysis, determine which time windows have elapsed based on age.
    Compare the price direction since analysis creation against the stance
    to determine correctness. Creates SignalOutcome records for each window.
    Returns the count of new outcomes created.
    """
    if get_session is not None:
        session = get_session()
        return await _do_evaluate_outcomes(session)

    if _async_session_factory is None:
        await init_db()
    assert _async_session_factory is not None
    async with _async_session_factory() as session:
        return await _do_evaluate_outcomes(session)


async def _do_evaluate_outcomes(session: AsyncSession) -> int:
    result = await session.execute(select(Analysis).order_by(Analysis.id))
    analyses = result.scalars().all()

    now = datetime.now(UTC)
    count = 0

    for analysis in analyses:
        age_hours = (now - analysis.created_at).total_seconds() / 3600

        windows: list[str] = []
        if age_hours >= 24:
            windows.append('1d')
        if age_hours >= 24 * 7:
            windows.append('1w')
        if age_hours >= 24 * 30:
            windows.append('1m')

        if not windows:
            continue

        analysis_price_result = await session.execute(
            select(PriceSnapshot)
            .where(
                PriceSnapshot.symbol == analysis.symbol,
                PriceSnapshot.recorded_at <= analysis.created_at,
            )
            .order_by(PriceSnapshot.recorded_at.desc())
            .limit(1)
        )
        analysis_snapshot = analysis_price_result.scalar_one_or_none()
        if analysis_snapshot is None:
            continue

        price_at_analysis = analysis_snapshot.price

        current_price_result = await session.execute(
            select(PriceSnapshot)
            .where(PriceSnapshot.symbol == analysis.symbol)
            .order_by(PriceSnapshot.recorded_at.desc())
            .limit(1)
        )
        current_snapshot = current_price_result.scalar_one_or_none()
        if current_snapshot is None:
            continue

        current_price = current_snapshot.price
        if price_at_analysis == 0:
            continue

        return_pct = round(((current_price - price_at_analysis) / price_at_analysis) * 100, 2)

        for window in windows:
            existing = await session.execute(
                select(SignalOutcome).where(
                    SignalOutcome.analysis_id == analysis.id,
                    SignalOutcome.window == window,
                )
            )
            if existing.scalar_one_or_none() is not None:
                continue

            price_up = current_price > price_at_analysis
            correct = False
            if analysis.stance == 'bullish' and price_up:
                correct = True
            elif analysis.stance == 'bearish' and not price_up:
                correct = True

            outcome = SignalOutcome(
                symbol=analysis.symbol,
                analysis_id=analysis.id,
                stance=analysis.stance,
                confidence=analysis.overall_score,
                price_at_analysis=price_at_analysis,
                window=window,
                price_at_check=current_price,
                return_pct=return_pct,
                correct=correct,
            )
            session.add(outcome)
            count += 1

    await session.commit()
    return count


# ── APScheduler daemon ──────────────────────────────────────────────────────────



_scheduler: AsyncIOScheduler | None = None


def start_scheduler() -> AsyncIOScheduler:
    """Create and start the APScheduler instance with configured jobs."""
    global _scheduler
    if _scheduler is not None:
        return _scheduler

    _scheduler = AsyncIOScheduler()

    if settings.quote_poll_seconds > 0:
        _scheduler.add_job(
            _run_async_job(poll_watchlist_quotes),
            IntervalTrigger(seconds=settings.quote_poll_seconds),
            id='poll_quotes',
            name='Poll watchlist quotes',
            replace_existing=True,
        )

    if settings.news_poll_seconds > 0:
        _scheduler.add_job(
            _run_async_job(poll_watchlist_news),
            IntervalTrigger(seconds=settings.news_poll_seconds),
            id='poll_news',
            name='Poll watchlist news',
            replace_existing=True,
        )

    if settings.alert_eval_seconds > 0:
        _scheduler.add_job(
            _run_async_job(evaluate_alerts),
            IntervalTrigger(seconds=settings.alert_eval_seconds),
            id='eval_alerts',
            name='Evaluate alert rules',
            replace_existing=True,
        )

    if settings.signal_eval_seconds > 0:
        _scheduler.add_job(
            _run_async_job(evaluate_signal_outcomes),
            IntervalTrigger(seconds=settings.signal_eval_seconds),
            id='eval_signals',
            name='Evaluate signal outcomes',
            replace_existing=True,
        )

    _scheduler.start()
    logger.info('APScheduler started with %d jobs', len(_scheduler.get_jobs()))
    return _scheduler


def stop_scheduler() -> None:
    """Shut down the APScheduler instance."""
    global _scheduler
    if _scheduler is None:
        return
    _scheduler.shutdown(wait=False)
    _scheduler = None
    logger.info('APScheduler shut down')


def _run_async_job(async_func: Callable[..., Any]) -> Callable[[], Any]:
    """Wrap an async function for APScheduler's sync job interface."""
    def wrapper() -> None:
        try:
            asyncio.create_task(_safe_run(async_func))
        except Exception as e:
            logger.error('Failed to schedule job %s: %s', async_func.__name__, e)
    return wrapper


async def _safe_run(async_func: Callable[..., Any]) -> None:
    """Run an async scheduler function with error isolation."""
    try:
        result = await async_func()
        logger.info('Scheduler job %s completed: %s', async_func.__name__, result)
    except Exception as e:
        logger.error('Scheduler job %s failed: %s', async_func.__name__, e)
