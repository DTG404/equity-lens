"""SEC EDGAR XBRL provider for fundamental financial data."""

from typing import Any

import httpx

SEC_HEADERS = {
    'User-Agent': 'EquityLens/1.0 (research project; contact: equitylens@example.com)',
    'Accept-Encoding': 'gzip, deflate',
}

CIK_LOOKUP_URL = 'https://www.sec.gov/files/company_tickers.json'
COMPANY_FACTS_URL = 'https://data.sec.gov/api/xbrl/companyfacts/CIK{:010d}.json'


def _get_cik(symbol: str) -> int | None:
    """Look up CIK number for a ticker symbol."""
    resp = httpx.get(CIK_LOOKUP_URL, headers=SEC_HEADERS, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    for item in data.values():
        if item.get('ticker', '').upper() == symbol.upper():
            return int(item['cik_str'])
    return None


class FundamentalsProvider:
    """Provides fundamental financial data from SEC EDGAR XBRL."""

    def get_fundamentals(self, symbol: str) -> dict[str, Any]:
        """Fetch income statement, balance sheet, cash flow, and key ratios."""
        cik = _get_cik(symbol)
        if cik is None:
            return {'symbol': symbol, 'error': 'CIK not found'}

        resp = httpx.get(COMPANY_FACTS_URL.format(cik), headers=SEC_HEADERS, timeout=15)
        resp.raise_for_status()
        facts = resp.json().get('facts', {})

        us_gaap = facts.get('us-gaap', {})
        if not us_gaap:
            return {'symbol': symbol, 'error': 'No US GAAP data available'}

        def get_value(fact: dict[str, Any], years_back: int = 2) -> float | None:
            """Extract the most recent annual value from a fact."""
            units = fact.get('units', {})
            for unit_key in units:
                entries = units[unit_key]
                annual = [
                    e for e in entries
                    if e.get('form') == '10-K' and e.get('fp') == 'FY'
                ]
                if annual:
                    sorted_entries = sorted(annual, key=lambda x: x.get('end', ''), reverse=True)
                    if years_back < len(sorted_entries):
                        val = sorted_entries[years_back].get('val')
                        return float(val) if val else None
            return None

        def get_metric(fact_name: str, years_back: int = 0) -> float | None:
            fact = us_gaap.get(fact_name, {})
            return get_value(fact, years_back)

        revenue = (
            get_metric('RevenueFromContractWithCustomerExcludingAssessedTax')
            or get_metric('Revenues')
        )
        net_income = get_metric('NetIncomeLoss')
        gross_profit = get_metric('GrossProfit')
        operating_income = get_metric('OperatingIncomeLoss')

        total_assets = get_metric('Assets')
        total_liabilities = get_metric('Liabilities')
        current_assets = get_metric('AssetsCurrent')
        current_liabilities = get_metric('LiabilitiesCurrent')
        equity = get_metric('StockholdersEquity')
        long_term_debt = get_metric('LongTermDebt') or get_metric('LongTermDebtNoncurrent')

        operating_cash_flow = get_metric('NetCashProvidedByUsedInOperatingActivities')
        free_cash_flow = None
        if operating_cash_flow is not None:
            capex = get_metric('PaymentsToAcquirePropertyPlantAndEquipment')
            if capex is not None:
                # XBRL stores capex as a positive magnitude (cash outflow)
                free_cash_flow = operating_cash_flow - capex

        eps_basic = get_metric('EarningsPerShareBasic')
        eps_diluted = get_metric('EarningsPerShareDiluted')

        return {
            'symbol': symbol.upper(),
            'income_statement': {
                'revenue': revenue,
                'gross_profit': gross_profit,
                'operating_income': operating_income,
                'net_income': net_income,
            },
            'balance_sheet': {
                'total_assets': total_assets,
                'total_liabilities': total_liabilities,
                'current_assets': current_assets,
                'current_liabilities': current_liabilities,
                'equity': equity,
                'long_term_debt': long_term_debt,
            },
            'cash_flow': {
                'operating_cash_flow': operating_cash_flow,
                'free_cash_flow': free_cash_flow,
            },
            'per_share': {
                'eps_basic': eps_basic,
                'eps_diluted': eps_diluted,
            },
            'ratios': {
                'debt_to_equity': (
                    round(long_term_debt / equity, 2)
                    if long_term_debt and equity else None
                ),
                'current_ratio': (
                    round(current_assets / current_liabilities, 2)
                    if current_assets and current_liabilities else None
                ),
                'net_margin': (
                    round((net_income / revenue) * 100, 1)
                    if net_income and revenue else None
                ),
                'gross_margin': (
                    round((gross_profit / revenue) * 100, 1)
                    if gross_profit and revenue else None
                ),
            },
        }
