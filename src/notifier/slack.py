import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError


_client = None


def _get_client() -> WebClient:
    global _client
    if _client is None:
        _client = WebClient(token=os.environ["SLACK_BOT_TOKEN"])
    return _client


def send_message(title: str, summary: str, url: str, source: str) -> None:
    """Send a summarized Snowflake news item to Slack."""
    source_emoji = ":snowflake:" if source == "release_notes" else ":memo:"
    source_label = "Release Note" if source == "release_notes" else "Blog"

    blocks = [
        {
            "type": "header",
            "text": {"type": "plain_text", "text": f"{source_emoji} Snowflake {source_label}"},
        },
        {
            "type": "section",
            "text": {"type": "mrkdwn", "text": f"*{title}*"},
        },
        {
            "type": "section",
            "text": {"type": "mrkdwn", "text": summary},
        },
        {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "원문 보기"},
                    "url": url,
                }
            ],
        },
    ]

    try:
        _get_client().chat_postMessage(
            channel=os.environ["SLACK_CHANNEL_ID"],
            blocks=blocks,
            text=f"Snowflake {source_label}: {title}",
        )
    except SlackApiError as e:
        raise RuntimeError(f"Slack API error: {e.response['error']}") from e
