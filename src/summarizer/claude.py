import os
import anthropic

_client = None


def _get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        _client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    return _client


def summarize(item: dict) -> str:
    """Snowflake 릴리즈 노트 또는 블로그 포스트를 자연스러운 한국어로 요약한다."""
    is_release = item["source"] == "release_notes"
    source_label = "릴리즈 노트" if is_release else "블로그 포스트"
    content = item.get("content") or item.get("description") or ""

    prompt = f"""당신은 Snowflake 기술 전문가입니다. 아래 Snowflake {source_label}를 읽고, 핵심 내용을 자연스러운 한국어로 요약해주세요.

요약 작성 지침:
- 3~5문장으로 간결하게 작성
- 어떤 기능이 추가/변경되었는지, 어떤 이점이 있는지 중심으로 서술
- 기술 용어(Snowflake 고유 명칭 등)는 영어 그대로 사용
- Slack 메시지로 읽기 좋게 자연스러운 문장으로 작성
- "~했습니다", "~됩니다" 등 격식체 사용

제목: {item['title']}
날짜: {item.get('date', '')}

내용:
{content[:3000]}

요약:"""

    message = _get_client().messages.create(
        model="claude-sonnet-4-6",
        max_tokens=512,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text.strip()
