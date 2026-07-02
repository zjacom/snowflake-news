# Snowflake News

Snowflake의 릴리즈 노트와 블로그 최신 글을 AI로 요약하여 Slack으로 알림을 보내는 자동화 봇입니다.  
매 평일 오전 8시(KST)에 GitHub Actions를 통해 자동 실행됩니다.

## 동작 방식

1. **릴리즈 노트 수집** — [Snowflake Docs](https://docs.snowflake.com/en/release-notes/all-release-notes?bundle=true) 페이지에서 최근 7일 이내 항목을 파싱
2. **블로그 수집** — [Snowflake RSS 피드](https://www.snowflake.com/feed/)에서 최근 7일 이내 포스트를 파싱
3. **AI 요약** — Claude API(claude-sonnet-4-6)로 핵심 내용을 자연스러운 한국어로 요약
4. **Slack 전송** — Slack Block Kit 메시지로 채널에 전송
5. **중복 방지** — 전송한 URL을 `state.json`에 기록하여 재전송 방지

## 프로젝트 구조

```
snowflake-news/
├── main.py                      # 진입점 + 스케줄러
├── state.json                   # 전송 이력 (자동 업데이트)
├── requirements.txt
├── .env.example
├── .github/
│   └── workflows/
│       └── snowflake-news.yml   # GitHub Actions 스케줄 워크플로우
└── src/
    ├── scraper/
    │   ├── release_notes.py     # Snowflake 릴리즈 노트 스크레이퍼
    │   └── blog.py              # Snowflake 블로그 RSS 파서
    ├── summarizer/
    │   └── claude.py            # Claude API 요약
    └── notifier/
        └── slack.py             # Slack 메시지 전송
```

## 설치 및 실행

### 1. 의존성 설치

```bash
pip install -r requirements.txt
```

### 2. 환경 변수 설정

`.env.example`을 복사하여 `.env` 파일을 만들고 값을 채웁니다.

```bash
cp .env.example .env
```

```
ANTHROPIC_API_KEY=sk-ant-api03-...   # console.anthropic.com
SLACK_BOT_TOKEN=xoxb-...             # api.slack.com/apps → OAuth & Permissions
SLACK_CHANNEL_ID=C0XXXXXXXXX         # Slack 채널 상세정보에서 확인
```

### 3. 로컬 실행

```bash
python main.py
```

로컬에서는 1회 실행 후 매일 오전 9시마다 반복 실행됩니다.  
CI 환경(GitHub Actions)에서는 1회 실행 후 종료됩니다.

## GitHub Actions 설정

### Secrets 등록

GitHub 저장소 → **Settings → Secrets and variables → Actions** 에서 아래 3개를 등록합니다.

| Name | 설명 |
|---|---|
| `ANTHROPIC_API_KEY` | Anthropic API 키 |
| `SLACK_BOT_TOKEN` | Slack Bot Token (`xoxb-`로 시작) |
| `SLACK_CHANNEL_ID` | 메시지를 받을 Slack 채널 ID |

### Slack 앱 설정

1. [api.slack.com/apps](https://api.slack.com/apps) 에서 앱 생성
2. **OAuth & Permissions → Scopes → Bot Token Scopes** 에 `chat:write` 추가
3. 워크스페이스에 앱 설치 후 Bot Token 복사
4. 메시지를 받을 채널에 `/invite @앱이름` 으로 봇 초대

### 실행 스케줄

평일(월~금) 오전 8시 KST에 자동 실행됩니다.  
**Actions 탭 → Snowflake News → Run workflow** 로 수동 실행도 가능합니다.

## 주요 설계 결정

- **블로그 스크레이핑**: Cloudflare 차단으로 직접 크롤링 불가 → RSS 피드(`snowflake.com/feed/`) 활용
- **빈 본문 처리**: 목록/RSS에서 본문이 없는 항목은 개별 페이지를 직접 fetch하여 보완
- **중복 방지**: 전송한 URL을 `state.json`에 저장, GitHub Actions 실행 후 자동 커밋
- **날짜 필터**: 최근 7일 이내 항목만 처리하여 초기 실행 시 과거 데이터 대량 전송 방지
