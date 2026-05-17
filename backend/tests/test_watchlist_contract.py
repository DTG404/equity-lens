import re

import pytest

from app.domain.models import TickerSymbol, WatchlistItem


def test_ticker_symbol_normalizes_to_uppercase():
    symbol = TickerSymbol(value='aapl')
    assert symbol.value == 'AAPL'


def test_ticker_symbol_rejects_invalid_symbols():
    with pytest.raises(ValueError, match=re.escape('ticker')):
        _ = TickerSymbol(value='../AAPL')


def test_watchlist_item_exposes_prediction_summary_fields():
    item = WatchlistItem(symbol='MSFT', company_name='Microsoft Corp')
    assert item.symbol == 'MSFT'
    assert item.company_name == 'Microsoft Corp'
    assert item.signal == 'unrated'
    assert item.confidence == 0.0
