import requests
from bs4 import BeautifulSoup
from email.utils import parsedate_to_datetime
from datetime import timezone

RSS_URL = "https://www.snowflake.com/feed/"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    ),
    "Accept": "application/rss+xml, application/xml, text/xml, */*",
    "Accept-Language": "en-US,en;q=0.9",
}


def fetch_list() -> list[dict]:
    """Snowflake RSS 피드에서 최신 블로그 포스트 목록을 가져온다."""
    response = requests.get(RSS_URL, timeout=15, headers=HEADERS)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "lxml-xml")

    items = []
    for item in soup.find_all("item"):
        title_tag = item.find("title")
        link_tag = item.find("link")
        date_tag = item.find("pubDate")
        desc_tag = item.find("description")
        content_tag = item.find("content:encoded") or item.find("encoded")

        if not (title_tag and link_tag):
            continue

        # description 또는 content:encoded에서 텍스트 추출
        raw_desc = (content_tag or desc_tag)
        if raw_desc:
            content_text = BeautifulSoup(raw_desc.get_text(), "html.parser").get_text(
                separator="\n", strip=True
            )
        else:
            content_text = ""

        pub_date = ""
        if date_tag:
            try:
                dt = parsedate_to_datetime(date_tag.get_text(strip=True))
                pub_date = dt.astimezone(timezone.utc).strftime("%Y-%m-%d")
            except Exception:
                pub_date = date_tag.get_text(strip=True)

        items.append({
            "title": title_tag.get_text(strip=True),
            "date": pub_date,
            "content": content_text[:4000],
            "url": link_tag.get_text(strip=True),
            "source": "blog",
        })

    return items
