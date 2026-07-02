import requests
from bs4 import BeautifulSoup

BASE_URL = "https://docs.snowflake.com"
LIST_URL = f"{BASE_URL}/en/release-notes/all-release-notes?bundle=true"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}


def fetch_list() -> list[dict]:
    """릴리즈 노트 목록 페이지에서 최신 항목들을 가져온다."""
    response = requests.get(LIST_URL, timeout=15, headers=HEADERS)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    items = []
    for card in soup.find_all("div", class_="release-card"):
        title_tag = card.find("h2")
        link_tag = card.find("a", href=lambda h: h and "/release-notes/" in h)
        date_tag = card.find("p", class_="text-card-label")
        desc_tag = card.find("p", class_="main-text")

        if not (title_tag and link_tag):
            continue

        href = link_tag["href"]
        url = BASE_URL + href if href.startswith("/") else href

        items.append({
            "title": title_tag.get_text(strip=True),
            "date": date_tag.get_text(strip=True) if date_tag else "",
            "description": desc_tag.get_text(strip=True) if desc_tag else "",
            "url": url,
            "source": "release_notes",
        })

    return items


def fetch_content(url: str) -> str:
    """개별 릴리즈 노트 페이지의 본문을 가져온다."""
    response = requests.get(url, timeout=15, headers=HEADERS)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    content = soup.select_one("div.body, main article, div[role='main']")
    if content:
        return content.get_text(separator="\n", strip=True)
    return soup.get_text(separator="\n", strip=True)[:4000]
