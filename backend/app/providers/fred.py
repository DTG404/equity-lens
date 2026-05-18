"""FRED economic data provider for macroeconomic context."""

from typing import Any

from fredapi import Fred

from app.core.config import settings

SERIES: dict[str, tuple[str, str]] = {
    'GDP': ('GDP', 'Gross Domestic Product'),
    'UNRATE': ('UNRATE', 'Unemployment Rate'),
    'CPIAUCSL': ('CPIAUCSL', 'Consumer Price Index'),
    'FEDFUNDS': ('FEDFUNDS', 'Federal Funds Rate'),
    'DGS10': ('DGS10', '10-Year Treasury Yield'),
    'DGS2': ('DGS2', '2-Year Treasury Yield'),
    'T10Y2Y': ('T10Y2Y', '10Y-2Y Yield Spread'),
    'UMCSENT': ('UMCSENT', 'Consumer Sentiment'),
    'INDPRO': ('INDPRO', 'Industrial Production'),
}


def get_macro_data() -> dict[str, Any]:
    """Fetch latest values for key economic indicators from FRED."""
    api_key = settings.fred_api_key
    if not api_key or api_key == '':
        return _get_sample_data()

    try:
        fred = Fred(api_key=api_key)
        result: dict[str, Any] = {}
        for key, (series_id, name) in SERIES.items():
            try:
                series = fred.get_series(series_id)
                if not series.empty:
                    latest = series.dropna().iloc[-1]
                    prev = series.dropna().iloc[-2] if len(series.dropna()) >= 2 else None
                    result[key] = {
                        'name': name,
                        'value': round(float(latest), 2),
                        'previous': round(float(prev), 2) if prev else None,
                        'change': round(float(latest - prev), 2) if prev else None,
                        'unit': '%' if key in ('FEDFUNDS', 'DGS10', 'DGS2', 'T10Y2Y', 'UNRATE') else '',
                    }
            except Exception:
                continue

        return {
            'source': 'FRED',
            'updated': None,
            'indicators': result,
        }
    except Exception:
        return _get_sample_data()


def _get_sample_data() -> dict[str, Any]:
    """Return sample data when FRED API key is not configured."""
    return {
        'source': 'FRED',
        'note': 'Set FRED_API_KEY in .env for live data',
        'indicators': {
            'GDP': {'name': 'Gross Domestic Product', 'value': 29.37, 'previous': 29.02, 'change': 0.35, 'unit': 'T'},
            'UNRATE': {'name': 'Unemployment Rate', 'value': 4.1, 'previous': 4.2, 'change': -0.1, 'unit': '%'},
            'CPIAUCSL': {'name': 'Consumer Price Index', 'value': 319.5, 'previous': 317.8, 'change': 1.7, 'unit': ''},
            'FEDFUNDS': {'name': 'Federal Funds Rate', 'value': 4.50, 'previous': 4.75, 'change': -0.25, 'unit': '%'},
            'DGS10': {'name': '10-Year Treasury Yield', 'value': 4.32, 'previous': 4.45, 'change': -0.13, 'unit': '%'},
            'DGS2': {'name': '2-Year Treasury Yield', 'value': 4.02, 'previous': 4.18, 'change': -0.16, 'unit': '%'},
            'T10Y2Y': {'name': '10Y-2Y Yield Spread', 'value': 0.30, 'previous': 0.27, 'change': 0.03, 'unit': '%'},
            'UMCSENT': {'name': 'Consumer Sentiment', 'value': 69.2, 'previous': 67.4, 'change': 1.8, 'unit': ''},
            'INDPRO': {'name': 'Industrial Production', 'value': 102.4, 'previous': 101.8, 'change': 0.6, 'unit': ''},
        },
    }
