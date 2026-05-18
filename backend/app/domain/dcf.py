"""DCF valuation model using SEC EDGAR fundamentals."""

from typing import Any

from app.providers.sec_edgar import FundamentalsProvider

_provider = FundamentalsProvider()


def calculate_dcf(symbol: str) -> dict[str, Any]:
    """Calculate a DCF valuation based on SEC EDGAR fundamentals."""
    fundamentals = _provider.get_fundamentals(symbol.upper())
    if 'error' in fundamentals:
        return {'symbol': symbol.upper(), 'error': fundamentals['error']}

    fcf = fundamentals.get('cash_flow', {}).get('free_cash_flow')
    if not fcf:
        return {'symbol': symbol.upper(), 'error': 'No free cash flow data available'}

    # Conservative assumptions
    growth_rate = 0.08  # 8% annual growth for 5 years
    terminal_growth = 0.03  # 3% terminal growth
    discount_rate = 0.10  # 10% WACC
    projection_years = 5

    # Project FCF
    projected = []
    cf = float(fcf)
    for year in range(1, projection_years + 1):
        cf *= (1 + growth_rate)
        discounted = cf / ((1 + discount_rate) ** year)
        projected.append({
            'year': year,
            'fcf': round(cf, 2),
            'discounted_fcf': round(discounted, 2),
        })

    # Terminal value
    terminal_value = projected[-1]['fcf'] * (1 + terminal_growth) / (discount_rate - terminal_growth)
    discounted_terminal = terminal_value / ((1 + discount_rate) ** projection_years)

    # Enterprise value
    ev = sum(p['discounted_fcf'] for p in projected) + discounted_terminal

    # Adjust for net cash / debt
    bs = fundamentals.get('balance_sheet', {})
    cash = bs.get('current_assets') or 0
    debt = bs.get('long_term_debt') or 0
    net_cash = float(cash) - float(debt) if cash and debt else 0

    equity_value = ev + net_cash

    # Estimate shares outstanding from EPS and net income
    ni = fundamentals.get('income_statement', {}).get('net_income')
    eps = fundamentals.get('per_share', {}).get('eps_basic')
    shares = (float(ni) / float(eps)) if ni and eps else 0

    fair_value = round(equity_value / shares, 2) if shares > 0 else None

    return {
        'symbol': symbol.upper(),
        'fair_value': fair_value,
        'enterprise_value': round(ev, 2),
        'net_cash': round(net_cash, 2),
        'projections': projected,
        'terminal_value': round(discounted_terminal, 2),
        'assumptions': {
            'growth_rate': f'{growth_rate*100}%',
            'terminal_growth': f'{terminal_growth*100}%',
            'discount_rate': f'{discount_rate*100}%',
            'projection_years': projection_years,
        },
        'note': 'Based on conservative assumptions. Not financial advice.',
    }
