"""Tests for factor scoring with data-driven computation."""
from app.domain.models import TickerSymbol
from app.domain.scoring import compute_factor_scores


def test_compute_scores_returns_all_factors():
    scores = compute_factor_scores(TickerSymbol(value='AAPL'))
    assert 'technical' in scores
    assert 'news_sentiment' in scores
    assert 'fundamentals' in scores
    assert 'macro' in scores
    assert 'overall' in scores
    for key in ('technical', 'news_sentiment', 'fundamentals', 'macro'):
        assert 0.0 <= scores[key]['score'] <= 1.0
        assert len(scores[key]['explanation']) > 0
    assert 0.0 <= scores['overall'] <= 1.0


def test_technical_score_reflects_price_change():
    """Technical score should increase with positive price change."""
    scores_up = compute_factor_scores(
        TickerSymbol(value='AAPL'), price_change_pct=5.0
    )
    scores_down = compute_factor_scores(
        TickerSymbol(value='AAPL'), price_change_pct=-5.0
    )
    assert scores_up['technical']['score'] > scores_down['technical']['score']


def test_news_sentiment_score_reflects_avg_sentiment():
    """News sentiment score should increase with positive average sentiment."""
    scores_pos = compute_factor_scores(
        TickerSymbol(value='AAPL'), avg_news_sentiment=0.8
    )
    scores_neg = compute_factor_scores(
        TickerSymbol(value='AAPL'), avg_news_sentiment=-0.5
    )
    assert scores_pos['news_sentiment']['score'] > scores_neg['news_sentiment']['score']


def test_fundamentals_and_macro_remain_stubs():
    """Fundamentals and macro should still return data even without params."""
    scores = compute_factor_scores(TickerSymbol(value='AAPL'))
    assert 'score' in scores['fundamentals']
    assert 'explanation' in scores['fundamentals']
    assert 'score' in scores['macro']
    assert 'explanation' in scores['macro']
    assert 0.0 <= scores['fundamentals']['score'] <= 1.0
    assert 0.0 <= scores['macro']['score'] <= 1.0
