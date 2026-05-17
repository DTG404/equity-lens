"""Tests for DeepSeek analysis service."""
from unittest.mock import patch

from app.core.config import settings
from app.core.deepseek import AnalysisInput, generate_thesis


def test_generate_thesis_returns_structure_without_api_key(monkeypatch):
    monkeypatch.setattr(settings, 'deepseek_api_key', '')
    result = generate_thesis(AnalysisInput(
        symbol='AAPL',
        company_name='Apple Inc.',
        technical_score=0.7,
        news_sentiment_score=0.6,
        fundamental_score=0.5,
        macro_score=0.5,
        overall_score=0.58,
        recent_news_titles=['Apple reports strong earnings'],
    ))
    assert 'thesis' in result
    assert 'bull_case' in result
    assert 'base_case' in result
    assert 'bear_case' in result
    assert result['model'] == 'fallback'


def test_generate_thesis_with_api_key_calls_deepseek(monkeypatch):
    monkeypatch.setattr(settings, 'deepseek_api_key', 'sk-test-key')

    async def mock_call(*args, **kwargs):
        return {
            'thesis': 'Test thesis',
            'bull_case': 'Bull case',
            'base_case': 'Base case',
            'bear_case': 'Bear case',
            'model': 'deepseek-chat',
        }

    with patch('app.core.deepseek._call_deepseek_api', new=mock_call):
        result = generate_thesis(AnalysisInput(
            symbol='AAPL',
            company_name='Apple Inc.',
            technical_score=0.7,
            news_sentiment_score=0.6,
            fundamental_score=0.5,
            macro_score=0.5,
            overall_score=0.58,
            recent_news_titles=['Apple reports strong earnings'],
        ))
    assert 'thesis' in result
    assert result['thesis'] == 'Test thesis'
    assert result['model'] == 'deepseek-chat'


def test_generate_thesis_fallback_on_api_error(monkeypatch):
    monkeypatch.setattr(settings, 'deepseek_api_key', 'sk-test-key')

    async def mock_call(*args, **kwargs):
        raise Exception('API error')

    with patch('app.core.deepseek._call_deepseek_api', new=mock_call):
        result = generate_thesis(AnalysisInput(
            symbol='AAPL',
            company_name='Apple Inc.',
            technical_score=0.7,
            news_sentiment_score=0.6,
            fundamental_score=0.5,
            macro_score=0.5,
            overall_score=0.58,
            recent_news_titles=['Apple reports strong earnings'],
        ))
    assert 'thesis' in result
    assert 'bull_case' in result
    assert 'base_case' in result
    assert 'bear_case' in result
    assert result['model'] == 'fallback'
