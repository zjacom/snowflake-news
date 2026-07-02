import requests
from bs4 import BeautifulSoup
from datetime import date


RELEASE_NOTES_URL = "https://docs.snowflake.com/en/release-notes/new-features"


def fetch_latest_release_notes() -> list[dict]:
    """Fetch today's release note entries from Snowflake docs."""
    response = requests.get(RELEASE_NOTES_URL, timeout=15)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    entries = []

    # TODO: parse actual DOM structure after inspecting the page
    for section in soup.select("section"):
        title_tag = section.find(["h2", "h3"])
        if not title_tag:
            continue
        entries.append({
            "title": title_tag.get_text(strip=True),
            "content": section.get_text(separator="\n", strip=True),
            "url": RELEASE_NOTES_URL,
            "source": "release_notes",
        })

    return entries
