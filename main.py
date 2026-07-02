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


def fetch_with_retry(fetch_fn, label: str, retries: int = 3) -> list[dict]:
    """fetch 함수를 최대 retries회 재시도한다."""
    for attempt in range(1, retries + 1):
        try:
            return fetch_fn()
        except Exception as e:
            print(f"  [{label}] 시도 {attempt}/{retries} 실패: {e}")
            if attempt < retries:
                time.sleep(10 * attempt)
    print(f"  [{label}] 최대 재시도 횟수 초과, 건너뜁니다.")
    return []


def run():
    print("=== Snowflake News 수집 시작 ===")
    st = state.load()

    print("[1/2] 릴리즈 노트 확인 중...")
    rn_items = fetch_with_retry(release_notes.fetch_list, "릴리즈 노트")
    rn_sent = process_items(rn_items, st)
    print(f"  → {rn_sent}건 전송 ({len(rn_items)}건 중 신규)")

    print("[2/2] 블로그 포스트 확인 중...")
    blog_items = fetch_with_retry(blog.fetch_list, "블로그")
    blog_sent = process_items(blog_items, st)
    print(f"  → {blog_sent}건 전송 ({len(blog_items)}건 중 신규)")

    state.save(st)
    print(f"=== 완료: 총 {rn_sent + blog_sent}건 전송 ===\n")


if __name__ == "__main__":
    run()

    # GitHub Actions 등 CI 환경에서는 1회 실행 후 종료
    if not os.environ.get("CI"):
        schedule.every().day.at("09:00").do(run)
        while True:
            schedule.run_pending()
            time.sleep(60)
