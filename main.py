import os
import sys
import schedule
import time
from dotenv import load_dotenv

# Windows 콘솔 UTF-8 출력
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

from src.scraper import release_notes, blog
from src.summarizer.claude import summarize
from src.notifier.slack import send
from src import state

load_dotenv()


def process_items(items: list[dict], st: dict) -> int:
    sent_count = 0
    for item in items:
        if not state.is_new(item["url"], st):
            continue
        try:
            summary = summarize(item)
            send(item, summary)
            state.mark_sent(item["url"], st)
            print(f"  ✓ {item['title']}")
            sent_count += 1
        except Exception as e:
            print(f"  ✗ {item['title']}: {e}")
    return sent_count


def run():
    print("=== Snowflake News 수집 시작 ===")
    st = state.load()

    print("[1/2] 릴리즈 노트 확인 중...")
    rn_items = release_notes.fetch_list()
    rn_sent = process_items(rn_items, st)
    print(f"  → {rn_sent}건 전송 ({len(rn_items)}건 중 신규)")

    print("[2/2] 블로그 포스트 확인 중...")
    blog_items = blog.fetch_list()
    blog_sent = process_items(blog_items, st)
    print(f"  → {blog_sent}건 전송 ({len(blog_items)}건 중 신규)")

    state.save(st)
    print(f"=== 완료: 총 {rn_sent + blog_sent}건 전송 ===\n")


if __name__ == "__main__":
    run()

    # 매일 오전 9시 실행
    schedule.every().day.at("09:00").do(run)
    while True:
        schedule.run_pending()
        time.sleep(60)
