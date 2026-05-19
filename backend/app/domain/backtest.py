"""Strategy backtesting engine."""

from dataclasses import dataclass, field
from typing import Any

import pandas as pd
import pandas_ta as ta


@dataclass
class StrategyCondition:
    indicator: str
    operator: str  # <, >, ==, crosses_above, crosses_below
    value: float | str


@dataclass
class BacktestRequest:
    name: str = 'Strategy'
    entry_conditions: list[dict[str, Any]] = field(default_factory=list)
    exit_conditions: list[dict[str, Any]] = field(default_factory=list)
    tickers: list[str] = field(default_factory=list)
    max_positions: int = 5
    position_size: str = 'equal_weight'


def compute_indicator(series: pd.Series, indicator: str) -> pd.Series | None:
    """Compute a named indicator on a price series."""
    indicators = {
        'rsi': lambda: ta.rsi(series, length=14),
        'sma_20': lambda: ta.sma(series, length=20),
        'sma_50': lambda: ta.sma(series, length=50),
        'ema_12': lambda: ta.ema(series, length=12),
        'ema_26': lambda: ta.ema(series, length=26),
    }
    func = indicators.get(indicator)
    return func() if func else None


def evaluate_condition(value: float, operator: str, threshold: float) -> bool:
    """Evaluate a single condition against a value."""
    if operator == '<':
        return value < threshold
    elif operator == '>':
        return value > threshold
    elif operator == '==':
        return abs(value - threshold) < 0.001
    return False


def run_backtest(
    prices: list[dict[str, Any]],
    entry_conds: list[dict[str, Any]],
    exit_conds: list[dict[str, Any]],
    symbol: str,
) -> dict[str, Any]:
    """Run a single-ticker backtest against price history."""
    if not prices or len(prices) < 30:
        return {'error': 'Insufficient price history', 'trades': 0}

    df = pd.DataFrame(prices)
    close = df['close']

    trades: list[dict[str, Any]] = []
    in_position = False
    entry_date = None
    entry_price = 0.0
    entry_bar_index = 0

    for i in range(20, len(df)):
        row = df.iloc[i]
        date_str = str(row.name) if hasattr(row.name, 'strftime') else str(row.name)

        if not in_position:
            # Check entry conditions
            should_enter = True
            for cond in entry_conds:
                ind = cond.get('indicator', '')
                op = cond.get('operator', '>')
                val = float(cond.get('value', 0))
                ind_series = compute_indicator(close.iloc[: i + 1], ind)
                if ind_series is not None and len(ind_series.dropna()) > 0:
                    ind_val = float(ind_series.dropna().iloc[-1])
                    if not evaluate_condition(ind_val, op, val):
                        should_enter = False
                else:
                    should_enter = False
                if not should_enter:
                    break

            if should_enter:
                in_position = True
                entry_date = date_str
                entry_price = float(row['close'])
                entry_bar_index = i

        else:
            # Check exit conditions
            should_exit = False
            for cond in exit_conds:
                ind = cond.get('indicator', '')
                op = cond.get('operator', '>')
                val = float(cond.get('value', 0))
                ind_series = compute_indicator(close.iloc[: i + 1], ind)
                if ind_series is not None and len(ind_series.dropna()) > 0:
                    ind_val = float(ind_series.dropna().iloc[-1])
                    if evaluate_condition(ind_val, op, val):
                        should_exit = True
                        break

            if should_exit:
                exit_price = float(row['close'])
                ret = ((exit_price - entry_price) / entry_price) * 100 if entry_price else 0
                trades.append({
                    'symbol': symbol,
                    'entry_date': entry_date,
                    'exit_date': date_str,
                    'entry_price': round(entry_price, 2),
                    'exit_price': round(exit_price, 2),
                    'return_pct': round(ret, 2),
                    'bars_held': i - entry_bar_index,
                })
                in_position = False

    # Close any open position at last price
    if in_position and len(df) > 0:
        exit_price = float(df.iloc[-1]['close'])
        ret = ((exit_price - entry_price) / entry_price) * 100 if entry_price else 0
        trades.append({
            'symbol': symbol,
            'entry_date': entry_date,
            'exit_date': str(df.index[-1]) if hasattr(df.index[-1], 'strftime') else str(df.index[-1]),
            'entry_price': round(entry_price, 2),
            'exit_price': round(exit_price, 2),
            'return_pct': round(ret, 2),
            'bars_held': 0,
        })

    # Compute metrics
    total_trades = len(trades)
    winning_trades = sum(1 for t in trades if t['return_pct'] > 0)
    win_rate = round(winning_trades / total_trades, 3) if total_trades > 0 else 0
    total_return = sum(t['return_pct'] for t in trades) if trades else 0
    avg_return = round(total_return / total_trades, 2) if total_trades > 0 else 0

    # Buy & hold return
    buy_hold = (
        round(
            ((float(df.iloc[-1]['close']) - float(df.iloc[0]['close'])) / float(df.iloc[0]['close'])) * 100,
            2,
        )
        if len(df) > 0
        else 0
    )

    # Max drawdown
    peak = float(df['close'].iloc[0])
    max_dd = 0.0
    for c in df['close']:
        val = float(c)
        if val > peak:
            peak = val
        dd = (peak - val) / peak
        if dd > max_dd:
            max_dd = dd

    return {
        'symbol': symbol,
        'trades': total_trades,
        'win_rate': win_rate,
        'total_return_pct': round(total_return, 2),
        'avg_return_per_trade': avg_return,
        'max_drawdown_pct': round(-max_dd * 100, 2),
        'buy_hold_return_pct': buy_hold,
        'vs_buy_hold': round(total_return - buy_hold, 2),
        'trades_list': trades,
    }
