import json
import os

STATE_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "state.json")


def load() -> dict:
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"sent_urls": []}


def save(state: dict) -> None:
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)


def is_new(url: str, state: dict) -> bool:
    return url not in state["sent_urls"]


def mark_sent(url: str, state: dict) -> None:
    if url not in state["sent_urls"]:
        state["sent_urls"].append(url)
