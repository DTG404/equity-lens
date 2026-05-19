"""DeepSeek-powered analysis service for thesis and scenario generation."""

from dataclasses import dataclass, field
from typing import Any

import httpx

from app.core.config import settings


@dataclass
class AnalysisInput:
    symbol: str
    company_name: str
    technical_score: float = 0.0
    news_sentiment_score: float = 0.0
    fundamental_score: float = 0.0
    macro_score: float = 0.0
    overall_score: float = 0.0
    recent_news_titles: list[str] = field(default_factory=list)


DEEPSEEK_API_URL = 'https://api.deepseek.com/v1/chat/completions'
FALLBACK_MODEL = 'fallback'
DEEPSEEK_MODEL = 'deepseek-chat'


def _build_fallback(input_data: AnalysisInput) -> dict[str, Any]:
    """Build a structured fallback response when DeepSeek API is unavailable."""
    stance = 'bullish' if input_data.overall_score >= 0.65 else (
        'bearish' if input_data.overall_score < 0.45 else 'neutral'
    )
    pct = f'{input_data.overall_score:.0%}'
    return {
        'thesis': (
            f'{input_data.symbol} ({input_data.company_name}) presents a '
            f'{stance} outlook with a composite score of {pct}. '
            f'Technical factors score {input_data.technical_score:.2f}, '
            f'news sentiment {input_data.news_sentiment_score:.2f}, '
            f'fundamentals {input_data.fundamental_score:.2f}, and '
            f'macro conditions {input_data.macro_score:.2f}. '
            f'Enable DEEPSEEK_API_KEY for AI-generated analysis.'
        ),
        'bull_case': (
            f'If positive momentum continues and {input_data.symbol} maintains '
            f'its current trajectory, the stock could outperform sector peers. '
            f'Strong technical and sentiment signals support upside potential.'
        ),
        'base_case': (
            f'{input_data.symbol} is expected to trade in line with sector '
            f'averages given current fundamentals. The composite score of {pct} '
            f'reflects a balanced risk-reward profile.'
        ),
        'bear_case': (
            'Key risks include sector headwinds, macroeconomic uncertainty, '
            'and potential earnings disappointments. A deterioration in '
            'technical or sentiment signals could lead to downside.'
        ),
        'model': FALLBACK_MODEL,
    }


def _build_prompt(input_data: AnalysisInput) -> str:
    """Build the structured prompt for the DeepSeek API."""
    news_context = '\n'.join(
        f'- {t}' for t in input_data.recent_news_titles
    ) if input_data.recent_news_titles else 'No recent news available.'
    return (
        f'Analyze {input_data.symbol} ({input_data.company_name}) and provide '
        f'a structured investment thesis with three scenarios.\n\n'
        f'Factor Scores:\n'
        f'- Technical: {input_data.technical_score:.2f}\n'
        f'- News Sentiment: {input_data.news_sentiment_score:.2f}\n'
        f'- Fundamentals: {input_data.fundamental_score:.2f}\n'
        f'- Macro: {input_data.macro_score:.2f}\n'
        f'- Overall: {input_data.overall_score:.2f}\n\n'
        f'Recent News:\n{news_context}\n\n'
        f'Respond in JSON format with keys: thesis, bull_case, base_case, bear_case. '
        f'Keep each field under 500 words.'
    )


def generate_thesis(input_data: AnalysisInput) -> dict[str, Any]:
    """Generate investment thesis and scenarios using DeepSeek or fallback.
    Synchronous wrapper — uses anyio.run(). Prefer generate_thesis_async() in async contexts.
    """
    api_key = settings.deepseek_api_key
    if not api_key:
        return _build_fallback(input_data)

    prompt = _build_prompt(input_data)

    try:
        import anyio
        response = anyio.run(_call_deepseek_api, api_key, prompt)
        return response
    except Exception:
        return _build_fallback(input_data)


async def generate_thesis_async(input_data: AnalysisInput) -> dict[str, Any]:
    """Async version of generate_thesis. Use this from async route handlers."""
    api_key = settings.deepseek_api_key
    if not api_key:
        return _build_fallback(input_data)

    prompt = _build_prompt(input_data)

    try:
        return await _call_deepseek_api(api_key, prompt)
    except Exception:
        return _build_fallback(input_data)


async def _call_deepseek_api(api_key: str, prompt: str) -> dict[str, Any]:
    """Make an async call to the DeepSeek API."""
    import json

    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(
            DEEPSEEK_API_URL,
            headers={
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json',
            },
            json={
                'model': DEEPSEEK_MODEL,
                'messages': [
                    {
                        'role': 'system',
                        'content': (
                            'You are a financial analyst. Respond in JSON format '
                            'with keys: thesis, bull_case, base_case, bear_case.'
                        ),
                    },
                    {'role': 'user', 'content': prompt},
                ],
                'temperature': 0.7,
                'max_tokens': 2000,
            },
        )
        resp.raise_for_status()
        data = resp.json()
        content = data['choices'][0]['message']['content']
        parsed: dict[str, Any] = json.loads(content)
        parsed['model'] = DEEPSEEK_MODEL
        return parsed


def generate_explanation(input_data: dict[str, Any]) -> dict[str, Any]:
    """Generate a beginner-friendly explanation using DeepSeek or fallback."""
    from app.core.config import settings

    api_key = settings.deepseek_api_key
    if not api_key:
        return _fallback_explanation(input_data)

    try:
        prompt = _build_explain_prompt(input_data)
        response = httpx.post(
            'https://api.deepseek.com/v1/chat/completions',
            headers={'Authorization': f'Bearer {api_key}'},
            json={
                'model': 'deepseek-chat',
                'messages': [{'role': 'user', 'content': prompt}],
                'temperature': 0.7,
                'max_tokens': 1000,
            },
            timeout=30,
        )
        response.raise_for_status()
        text = response.json()['choices'][0]['message']['content']
        return _parse_explanation(text)
    except Exception:
        return _fallback_explanation(input_data)


def _build_explain_prompt(data: dict[str, Any]) -> str:
    return (
        f"You are a patient investing mentor. Explain {data.get('symbol')} analysis "
        f"to a complete beginner in plain English.\n\n"
        f"Overall score: {data.get('overall_score', 0.5)*100:.0f}% ({data.get('stance', 'neutral')})\n"
        f"Technical: {data.get('technical_score', 0.5)*100:.0f}%\n"
        f"News Sentiment: {data.get('news_sentiment_score', 0.5)*100:.0f}%\n"
        f"Fundamentals: {data.get('fundamental_score', 0.5)*100:.0f}%\n"
        f"Macro: {data.get('macro_score', 0.5)*100:.0f}%\n"
        f"Thesis: {data.get('thesis', 'N/A')}\n"
        f"Recent news: {data.get('news_titles', 'None')}\n\n"
        "Provide:\n"
        "1. Plain-language explanation (2-3 paragraphs)\n"
        "2. 3-5 key takeaways (bullet points)\n"
        "3. 2-3 questions the investor should ask themselves\n\n"
        "Write in simple English. Avoid jargon."
    )


def _fallback_explanation(data: dict[str, Any]) -> dict[str, Any]:
    stance = data.get('stance', 'neutral')
    overall = data.get('overall_score', 0.5) * 100
    return {
        'explanation': (
            f"{data.get('symbol')} has an overall score of {overall:.0f}%, "
            f"which suggests a {stance} outlook. "
            f"This score considers technical indicators, news sentiment, fundamentals, and macro conditions. "
            f"Always remember that past performance doesn't guarantee future results."
        ),
        'key_takeaways': [
            f"The overall score of {overall:.0f}% indicates a {stance} outlook.",
            "This analysis combines multiple factors—not just one signal.",
            "Consider diversifying rather than acting on a single stock assessment.",
        ],
        'questions_to_ask': [
            'Do I understand what is driving this score?',
            'What would need to change for my view to be wrong?',
            'How does this fit into my overall investment plan?',
        ],
    }


def _parse_explanation(text: str) -> dict[str, Any]:
    lines = [ln.strip() for ln in text.strip().split('\n') if ln.strip()]
    explanation_parts = []
    takeaways = []
    questions = []
    mode = 'explanation'

    for line in lines:
        lower = line.lower()
        if 'key takeaways' in lower:
            mode = 'takeaways'
            continue
        if ('question' in lower and 'ask' in lower) or 'ask yourself' in lower:
            mode = 'questions'
            continue
        if mode == 'takeaways' and (line.startswith('- ') or line.startswith('* ') or line[0].isdigit()):
            takeaways.append(line.lstrip('- *0123456789. '))
        elif mode == 'questions' and (line.startswith('- ') or line.startswith('* ') or line[0].isdigit()):
            questions.append(line.lstrip('- *0123456789. '))
        elif mode == 'explanation':
            explanation_parts.append(line)

    return {
        'explanation': ' '.join(explanation_parts) if explanation_parts else text,
        'key_takeaways': takeaways[:5] if takeaways else ['Analysis complete.'],
        'questions_to_ask': questions[:3] if questions else ['Review the analysis details.'],
    }
