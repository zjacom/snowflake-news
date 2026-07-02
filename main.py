import os
import schedule
import time
from dotenv import load_dotenv

from src.scraper.release_notes import fetch_latest_release_notes
from src.scraper.blog import fetch_latest_blog_posts
from src.summarizer.claude import summarize
from src.notifier.slack import send_message

load_dotenv()


def run():
    print("Fetching Snowflake release notes...")
    for item in fetch_latest_release_notes():
        summary = summarize(item["title"], item["content"], item["source"])
        send_message(item["title"], summary, item["url"], item["source"])

    print("Fetching Snowflake blog posts...")
    for item in fetch_latest_blog_posts():
        summary = summarize(item["title"], item["content"], item["source"])
        send_message(item["title"], summary, item["url"], item["source"])

    print("Done.")


if __name__ == "__main__":
    run()
    # 매일 오전 9시 실행
    schedule.every().day.at("09:00").do(run)
    while True:
        schedule.run_pending()
        time.sleep(60)
