"""Signal backtesting endpoint."""

from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_session
from app.domain.db_models import SignalOutcome

router = APIRouter(prefix='/backtest', tags=['backtest'])


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
