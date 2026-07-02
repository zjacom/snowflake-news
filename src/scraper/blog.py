import requests
from bs4 import BeautifulSoup


BLOG_URL = "https://www.snowflake.com/blog/"


def fetch_latest_blog_posts() -> list[dict]:
    """Fetch latest blog post summaries from the Snowflake blog."""
    response = requests.get(BLOG_URL, timeout=15)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    posts = []

    # TODO: parse actual DOM structure after inspecting the page
    for article in soup.select("article"):
        title_tag = article.find(["h2", "h3"])
        link_tag = article.find("a", href=True)
        if not title_tag:
            continue
        posts.append({
            "title": title_tag.get_text(strip=True),
            "content": article.get_text(separator="\n", strip=True),
            "url": link_tag["href"] if link_tag else BLOG_URL,
            "source": "blog",
        })

    return posts
