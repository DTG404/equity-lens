"""SEC EDGAR filings, insider trading, and institutional ownership providers."""

from typing import Any

import httpx

from app.providers.sec_edgar import _get_cik

SEC_HEADERS = {
    'User-Agent': 'EquityLens/1.0 (research project; contact: equitylens@example.com)',
    'Accept-Encoding': 'gzip, deflate',
}

SUBMISSIONS_URL = 'https://data.sec.gov/submissions/CIK{:010d}.json'


def get_recent_filings(symbol: str, count: int = 10) -> dict[str, Any]:
    """Fetch recent SEC filings (10-K, 10-Q, 8-K) for a symbol."""
    cik = _get_cik(symbol)
    if not cik:
        return {'symbol': symbol.upper(), 'error': 'CIK not found'}

    resp = httpx.get(SUBMISSIONS_URL.format(cik), headers=SEC_HEADERS, timeout=15)
    resp.raise_for_status()
    data = resp.json()

    filings = data.get('filings', {}).get('recent', {})
    if not filings:
        return {'symbol': symbol.upper(), 'error': 'No filings found'}

    form_types = filings.get('form', [])
    dates = filings.get('filingDate', [])
    descriptions = filings.get('primaryDocument', [])
    base_url = 'https://www.sec.gov/cgi-bin/browse-edgar'
    urls = [
        f'{base_url}?action=getcompany&CIK={cik:010d}&type={f}&dateb=&owner=exclude&count=10'
        for f in form_types
    ]

    result: list[dict[str, Any]] = []
    for i, form in enumerate(form_types):
        if form in ('10-K', '10-Q', '8-K'):
            if len(result) >= count:
                break
            result.append({
                'form': form,
                'filing_date': dates[i] if i < len(dates) else None,
                'description': descriptions[i] if i < len(descriptions) else '',
                'url': urls[i] if i < len(urls) else '',
            })

    return {'symbol': symbol.upper(), 'filings': result}


def get_insider_trades(symbol: str, count: int = 20) -> dict[str, Any]:
    """Fetch recent insider trading transactions (Form 4) for a symbol."""
    cik = _get_cik(symbol)
    if not cik:
        return {'symbol': symbol.upper(), 'error': 'CIK not found'}

    resp = httpx.get(SUBMISSIONS_URL.format(cik), headers=SEC_HEADERS, timeout=15)
    resp.raise_for_status()
    data = resp.json()

    filings = data.get('filings', {}).get('recent', {})
    if not filings:
        return {'symbol': symbol.upper(), 'error': 'No filings found'}

    result: list[dict[str, Any]] = []
    form_types = filings.get('form', [])
    dates = filings.get('filingDate', [])
    descriptions = filings.get('primaryDocument', [])

    for i, form in enumerate(form_types):
        if form == '4' and len(result) < count:
            result.append({
                'form': '4',
                'filing_date': dates[i] if i < len(dates) else None,
                'description': descriptions[i] if i < len(descriptions) else '',
            })

    return {'symbol': symbol.upper(), 'trades': result}


def get_institutional_holders(symbol: str, count: int = 10) -> dict[str, Any]:
    """Fetch institutional holdings from 13F filings via EDGAR."""
    cik = _get_cik(symbol)
    if not cik:
        return {'symbol': symbol.upper(), 'error': 'CIK not found'}

    resp = httpx.get(SUBMISSIONS_URL.format(cik), headers=SEC_HEADERS, timeout=15)
    resp.raise_for_status()
    data = resp.json()

    filings = data.get('filings', {}).get('recent', {})
    if not filings:
        return {'symbol': symbol.upper(), 'error': 'No filings found'}

    result: list[dict[str, Any]] = []
    form_types = filings.get('form', [])
    dates = filings.get('filingDate', [])
    descriptions = filings.get('primaryDocument', [])

    for i, form in enumerate(form_types):
        if form == '13F-HR' and len(result) < count:
            result.append({
                'form': '13F-HR',
                'filing_date': dates[i] if i < len(dates) else None,
                'description': descriptions[i] if i < len(descriptions) else '',
            })

    return {'symbol': symbol.upper(), 'holders': result}
