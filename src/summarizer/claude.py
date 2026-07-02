import os
import anthropic


_client = None


def _get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        _client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    return _client


def summarize(title: str, content: str, source: str) -> str:
    """Summarize a Snowflake release note or blog post in Korean."""
    source_label = "릴리즈 노트" if source == "release_notes" else "블로그 포스트"
    prompt = f"""다음은 Snowflake {source_label}입니다. 핵심 내용을 한국어로 3~5줄로 요약해주세요.
Slack 메시지로 전송할 것이므로 간결하고 명확하게 작성해주세요.

제목: {title}

내용:
{content[:3000]}
"""
    message = _get_client().messages.create(
        model="claude-sonnet-4-6",
        max_tokens=512,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text.strip()
