import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

_client = None


def _get_client() -> WebClient:
    global _client
    if _client is None:
        _client = WebClient(token=os.environ["SLACK_BOT_TOKEN"])
    return _client


def send(item: dict, summary: str) -> None:
    """요약된 Snowflake 뉴스를 Slack으로 전송한다."""
    is_release = item["source"] == "release_notes"
    source_emoji = "❄️" if is_release else "📝"
    source_label = "Release Note" if is_release else "Blog"
    date_text = f"  |  {item['date']}" if item.get("date") else ""

    blocks = [
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": f"{source_emoji} *Snowflake {source_label}*{date_text}",
                }
            ],
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*{item['title']}*",
            },
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": summary,
            },
        },
        {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "원문 보기 →"},
                    "url": item["url"],
                    "style": "primary",
                }
            ],
        },
        {"type": "divider"},
    ]

    try:
        _get_client().chat_postMessage(
            channel=os.environ["SLACK_CHANNEL_ID"],
            blocks=blocks,
            text=f"[Snowflake {source_label}] {item['title']}",
        )
    except SlackApiError as e:
        raise RuntimeError(f"Slack 전송 실패: {e.response['error']}") from e
