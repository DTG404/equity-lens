"""Backtesting endpoints."""

from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_session
from app.domain.backtest import run_backtest
from app.domain.db_models import PriceHistory, SignalOutcome

router = APIRouter(prefix='/backtest', tags=['backtest'])


@router.post('/run')
async def run_backtest_endpoint(
    body: dict[str, Any],
    session: AsyncSession = Depends(get_session),
) -> dict[str, Any]:
    """Run a strategy backtest against historical price data."""
    strategy = body.get('strategy', {})
    tickers = strategy.get('tickers', [])
    entry_conds = strategy.get('entry_conditions', [])
    exit_conds = strategy.get('exit_conditions', [])

    if not tickers:
        return {'error': 'No tickers provided'}

    results: list[dict[str, Any]] = []
    for symbol in tickers:
        result = await session.execute(
            select(PriceHistory)
            .where(PriceHistory.symbol == symbol)
            .order_by(PriceHistory.date)
        )
        rows = result.scalars().all()

        if not rows:
            results.append({'symbol': symbol, 'error': 'No price history', 'trades': 0})
            continue

        prices = [
            {
                'close': r.close_price,
                'high': r.high_price,
                'low': r.low_price,
                'open': r.open_price,
                'volume': r.volume,
                'date': str(r.date),
            }
            for r in rows
        ]

        bt_result = run_backtest(prices, entry_conds, exit_conds, symbol)
        results.append(bt_result)

    total_trades = sum(r.get('trades', 0) for r in results)
    total_return = sum(r.get('total_return_pct', 0) for r in results)
    total_bh = sum(r.get('buy_hold_return_pct', 0) for r in results)
    win_trades = sum(r.get('trades', 0) * r.get('win_rate', 0) for r in results)

    return {
        'strategy_name': strategy.get('name', 'Backtest'),
        'tickers': tickers,
        'total_trades': total_trades,
        'overall_return_pct': round(total_return, 2),
        'buy_hold_return_pct': round(total_bh, 2),
        'win_rate': round(win_trades / total_trades, 3) if total_trades > 0 else 0,
        'results': results,
    }


@router.get('/signals')
async def backtest_signals(
    session: AsyncSession = Depends(get_session),
) -> dict[str, Any]:
    """Aggregate signal performance by stance and window."""
    result = await session.execute(select(SignalOutcome))
    outcomes = result.scalars().all()

    total = len(outcomes)
    correct = sum(1 for o in outcomes if o.correct)
    accuracy = round((correct / total) * 100, 1) if total > 0 else 0

    # By stance
    stances: dict[str, dict[str, Any]] = {}
    for o in outcomes:
        s = stances.setdefault(o.stance, {'count': 0, 'correct': 0, 'total_return': 0.0})
        s['count'] += 1
        if o.correct:
            s['correct'] += 1
        s['total_return'] += o.return_pct

    stance_results = {}
    for stance, data in stances.items():
        stance_results[stance] = {
            'count': data['count'],
            'accuracy': round((data['correct'] / data['count']) * 100, 1),
            'avg_return': round(data['total_return'] / data['count'], 2),
        }

    # By window
    windows: dict[str, dict[str, Any]] = {}
    for o in outcomes:
        w = windows.setdefault(o.window, {'count': 0, 'correct': 0, 'total_return': 0.0})
        w['count'] += 1
        if o.correct:
            w['correct'] += 1
        w['total_return'] += o.return_pct

    window_results = {}
    for window, data in windows.items():
        window_results[window] = {
            'count': data['count'],
            'accuracy': round((data['correct'] / data['count']) * 100, 1),
            'avg_return': round(data['total_return'] / data['count'], 2),
        }

    return {
        'total_signals': total,
        'correct_signals': correct,
        'overall_accuracy': accuracy,
        'by_stance': stance_results,
        'by_window': window_results,
    }
