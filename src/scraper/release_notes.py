import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta, timezone

BASE_URL = "https://docs.snowflake.com"
LIST_URL = f"{BASE_URL}/en/release-notes/all-release-notes?bundle=true"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Cache-Control": "no-cache",
    "Pragma": "no-cache",
}

_DATE_FORMATS = ["%B %d, %Y", "%b %d, %Y"]


def _parse_date(date_str: str) -> datetime | None:
    for fmt in _DATE_FORMATS:
        try:
            return datetime.strptime(date_str.strip(), fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    return None


def fetch_content(url: str) -> str:
    """개별 릴리즈 노트 페이지의 본문을 가져온다."""
    response = requests.get(url, timeout=15, headers=HEADERS)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    content = soup.select_one("div.body, main article, div[role='main']")
    if content:
        return content.get_text(separator="\n", strip=True)[:4000]
    return soup.get_text(separator="\n", strip=True)[:4000]


def fetch_list(days: int = 7) -> list[dict]:
    """릴리즈 노트 목록에서 최근 N일 이내 항목만 가져온다."""
    response = requests.get(LIST_URL, timeout=15, headers=HEADERS)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    items = []

    for card in soup.find_all("div", class_="release-card"):
        title_tag = card.find("h2")
        link_tag = card.find("a", href=lambda h: h and "/release-notes/" in h)
        date_tag = card.find("p", class_="text-card-label")
        desc_tag = card.find("p", class_="main-text")

        if not (title_tag and link_tag):
            continue

        date_str = date_tag.get_text(strip=True) if date_tag else ""
        parsed = _parse_date(date_str)
        if parsed and parsed < cutoff:
            continue

        href = link_tag["href"]
        url = BASE_URL + href if href.startswith("/") else href
        description = desc_tag.get_text(strip=True) if desc_tag else ""

        # 목록 페이지에 설명이 없으면 개별 페이지에서 본문을 가져온다
        if not description:
            try:
                description = fetch_content(url)
            except Exception:
                pass

        items.append({
            "title": title_tag.get_text(strip=True),
            "date": date_str,
            "description": description,
            "url": url,
            "source": "release_notes",
        })

    return items
