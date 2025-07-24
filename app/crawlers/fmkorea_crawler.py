import requests
from bs4 import BeautifulSoup
from time import sleep
from typing import Optional
from datetime import datetime, timezone
import re
import random
import time
import cloudscraper
import sys

from app.services.mongo_utils import save_fmkorea_post_doc

BASE_URL = "https://www.fmkorea.com"

BOARD_PATHS = {
    "해외축구": "football_world",
    "국내축구": "football_korean",
    "축구소식통": "football_news"
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    "Referer": "https://www.fmkorea.com/",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
}

scraper = cloudscraper.create_scraper()

# 게시글 목록 수집
def get_post_links(scraper, board_path: str, page: int = 1) -> list[str]:
    url = f"{BASE_URL}/{board_path}?page={page}"
    res = scraper.get(url, headers=HEADERS)
    text_preview = res.text[:1000] 

    # 차단 여부 감지
    if (
        res.status_code == 403
        or "Cloudflare" in res.text
        or "Please enable JavaScript" in res.text
        or re.search(r'var\s+[a-zA-Z]{3}\s*=\s*"";', text_preview)  # e.g., var RTE = "";
        or re.search(r'\["[a-zA-Z0-9+/=]+",\s*"[a-zA-Z0-9+/=]+"\]', text_preview)  # base64-like 배열
    ):
        print("🚫 크롤링 차단됨! Cloudflare 또는 봇 차단 페이지 감지됨.")
        sys.exit(1)

    soup = BeautifulSoup(res.text, "html.parser")

    links = []
    for tr in soup.select("tr"):
         # 공지글 건너뜀
        if "notice" in tr.get("class", []):
            continue

        a_tag = tr.select_one("td.title a[href]")
        if not a_tag:
            continue
        href = a_tag.get("href")
        if href.startswith("/") and not href.startswith("http"):
            full_url = BASE_URL + href
            links.append(full_url)

    print(f"🔗 링크 수집 완료 ({len(links)}개): {url}")
    return links

# 게시글 본문 + 댓글 추출
def parse_post(scraper, url: str) -> Optional[dict]:
    res = scraper.get(url, headers=HEADERS)
    soup = BeautifulSoup(res.text, "html.parser")

    title_tag = soup.select_one("h1 .np_18px_span") or soup.select_one("h1 span")
    content_tag = soup.select_one("div.xe_content") or soup.select_one("div.rd_body")

    if not title_tag:
        print(f"⏭️ 건너뜀 (제목 없음): {url}")
        return None

    title = title_tag.get_text(strip=True)
    content = content_tag.get_text(strip=True) if content_tag else ""

    # 날짜
    date_tag = soup.select_one("span.date") or soup.select_one("span.rd_time")
    date_str = date_tag.get_text(strip=True) if date_tag else None

    try:
        post_datetime = datetime.strptime(date_str, "%Y.%m.%d %H:%M")
        post_datetime = post_datetime.replace(tzinfo=timezone.utc)
    except:
        print(f"⚠️ 날짜 파싱 실패: {date_str}")
        post_datetime = None

    # 조회수
    view_tag = soup.select_one("span.hit") or soup.select_one("span.rd_view")
    try:
        view_count = int(view_tag.get_text(strip=True).replace(",", "")) if view_tag else None
    except:
        print(f"⚠️ 조회수 파싱 실패: {view_tag}")
        view_count = None

    # 추천 수
    like_tag = soup.select_one("span.vote") or soup.select_one("span#good_button")
    like_text = like_tag.get_text(strip=True) if like_tag else "0"
    match = re.search(r'\d+', like_text)
    like_count = int(match.group()) if match else 0

    # 댓글 추출
    comments = []
    comment_tags = soup.select("div.comment-content")
    for tag in comment_tags:
        comment = tag.get_text(strip=True)
        if comment:
            comments.append(comment)

    return {
        "url": url,
        "title": title,
        "content": content,
        "comments": comments,
        "source": "fmkorea",
        "crawled_at": datetime.now(timezone.utc),
        "post_datetime": post_datetime,
        "view_count": view_count,
        "like_count": like_count,
        "text_for_embedding": f"{title}: {content}"
    }


# 게시판 크롤링 실행
def crawl_fmkorea_board(board_name: str, page_limit: int = 1):
    board_path = BOARD_PATHS.get(board_name)
    if not board_path:
        print(f"❌ 유효하지 않은 게시판 이름: {board_name}")
        return

    session = requests.Session()

    for page in range(1, page_limit + 1):
        print(f"\n📄 [{board_name}] {page}페이지 수집 중...")
        post_links = get_post_links(scraper, board_path, page)

        for idx, url in enumerate(post_links):
            # # 이미 DB에 저장된 게시글이면 중단
            # if fmkorea_collection.find_one({"url": url}):
            #     print(f"🛑 이미 수집한 게시글 발견 → 크롤링 중단")
            #     return

            # print(f"\n➡️ [{idx+1}/{len(post_links)}] 크롤링 중: {url}")
            try:
                post = parse_post(scraper, url)
                if post:
                    save_fmkorea_post_doc(post)
                    print(f"💾 저장 완료: {post['title'][:30]}")
                else:
                    print(f"❌ 저장 스킵 (파싱 실패): {url}")
            except Exception as e:
                print(f"❌ 예외 발생: {e} → {url}")
            
            delay = random.uniform(1.0, 2.5)  # 1.0초 ~ 2.5초 사이 랜덤
            time.sleep(delay)

# 예시 실행
if __name__ == "__main__":
    crawl_fmkorea_board("해외축구", page_limit=5)