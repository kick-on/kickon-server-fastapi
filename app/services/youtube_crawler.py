from youtube_comment_downloader import YoutubeCommentDownloader
from pymongo import MongoClient
from datetime import datetime, timezone
import requests
import re
from app.core.config import settings

API_KEY = settings.youtube_api_key

# MongoDB 연결
client = MongoClient(settings.mongo_uri)
db = client["kickon"]
collection = db["youtube_comments"]

# 영상 검색 (업로드일 기준으로 필터링)
def search_videos(query, max_results=5):
    search_url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "part": "snippet",
        "q": query,
        "type": "video",
        "maxResults": max_results,
        "order": "date",  # 최신순 정렬
        "key": API_KEY
    }
    response = requests.get(search_url, params=params)
    response.raise_for_status()
    items = response.json()["items"]

    today = datetime.now(timezone.utc).date() 

    return [
        {
            "video_id": item["id"]["videoId"],
            "title": item["snippet"]["title"],
            "published_at": item["snippet"]["publishedAt"]
        }
        for item in items
        #if datetime.strptime(item["snippet"]["publishedAt"], "%Y-%m-%dT%H:%M:%SZ").date() == today
    ]

# 댓글 크롤링 및 저장
def crawl_and_store_comments(video_id, video_title, published_at, query=None):
    downloader = YoutubeCommentDownloader()
    video_url = f"https://www.youtube.com/watch?v={video_id}"

    print(f"[크롤링 시작] {video_title} ({video_id})")

    comment_data = []
    try:
        for comment in downloader.get_comments_from_url(video_url, sort_by=0):  # 인기순
            comment_text = comment["text"]
            comment_obj = {
                "author": comment.get("author", "unknown"),
                "text": comment_text,
                "published_at": datetime.utcnow(),
                "text_for_embedding": f"영상 제목: {video_title}\n댓글: {comment_text}"
            }
            comment_data.append(comment_obj)
    except Exception as e:
        print(f"[에러 발생] {e}")
        return

    doc = {
        "video_id": video_id,
        "video_title": video_title,
        "video_url": video_url,
        "team_mentioned": query,
        "match_date": None,
        "video_published_at": published_at,
        "crawled_at": datetime.utcnow(),
        "comments": comment_data
    }

    collection.insert_one(doc)
    print(f"[저장 완료] 댓글 {len(comment_data)}개 저장")

# 메인 실행
if __name__ == "__main__":
    teams = [("수원 삼성", "FC 서울"), ("인천", "대전")]
    queries = [f"{home} vs {away} 하이라이트" for home, away in teams]

    for query in queries:
        print(f"\n🔍 검색어: {query}")
        videos = search_videos(query)
        for video in videos:
            video_id = video["video_id"]

            # 중복 방지
            if collection.find_one({"video_id": video_id}):
                print(f"⏩ 이미 크롤링한 영상입니다: {video['title']}")
                continue

            print("📺", video["title"])
            crawl_and_store_comments(video["video_id"], video["title"], video["published_at"], query=query)