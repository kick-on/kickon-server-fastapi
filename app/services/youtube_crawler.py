from youtube_comment_downloader import YoutubeCommentDownloader
from pymongo import MongoClient
from datetime import datetime, timezone
import requests

from app.core.config import settings

API_KEY = settings.youtube_api_key

# MongoDB 연결
client = MongoClient(settings.mongo_uri)
db = client["kickon"]
collection = db["youtube_comments"]

# 영상 검색 (업로드일 기준으로 필터링)
def search_videos(query, max_results=10):
    search_url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "part": "snippet",
        "q": query,
        "type": "video",
        "maxResults": max_results,
        "order": "relevance", # 관련도 중심
        "key": API_KEY
    }
    response = requests.get(search_url, params=params)
    response.raise_for_status()
    items = response.json()["items"]

    # 필터: 검색어의 양쪽 팀 이름이 모두 제목에 들어간 경우만 통과
    teams = [part.strip() for part in query.replace("하이라이트", "").split("vs") if part.strip()]
    
    filtered_items = []
    for item in items:
        title = item["snippet"]["title"].lower()
        if all(team.lower() in title for team in teams):
            filtered_items.append(item)
    
    return [
        {
            "video_id": item["id"]["videoId"],
            "title": item["snippet"]["title"],
            "published_at": item["snippet"]["publishedAt"]
        }
        for item in filtered_items
    ]

# 댓글 크롤링 및 저장
def crawl_and_store_comments_by_query(query):
    print(f"\n🔍 [1] 검색 쿼리: {query}")

    try:
        videos = search_videos(query)
        print(f"📺 [2] 검색된 영상 수: {len(videos)}")
    except Exception as e:
        print(f"❌ 유튜브 검색 중 문제 발생: {e}")
        return
    
    for video in videos:
        video_id = video["video_id"]
        print(f"\n🎬 [3] 영상 제목: {video['title']} / ID: {video_id}")

        # 이미 크롤링한 영상인지 확인
        if collection.find_one({"video_id": video_id}):
            print(f"⏩ 이미 크롤링한 영상입니다: {video['title']}")
            continue

        downloader = YoutubeCommentDownloader()
        video_url = f"https://www.youtube.com/watch?v={video_id}"

        comment_data = []

        try:
            for comment in downloader.get_comments_from_url(video_url, sort_by=0):
                comment_text = comment["text"]
                comment_obj = {
                    "author": comment.get("author", "unknown"),
                    "text": comment_text,
                    "published_at": datetime.utcnow(),
                    "text_for_embedding": f"영상 제목: {video['title']}\n댓글: {comment_text}"
                }
                comment_data.append(comment_obj)
        except Exception as e:
            print(f"❌ 댓글 크롤링 중 문제 발생: {e}")
            return
        
        print(f"✅ [4] 댓글 수집 완료: {len(comment_data)}개")

        if len(comment_data) == 0:
            print(f"❌ 댓글 없음")
            continue

        doc = {
            "video_id": video_id,
            "video_title": video["title"],
            "video_url": video_url,
            "team_mentioned": query,
            "match_date": None,
            "video_published_at": video["published_at"],
            "crawled_at": datetime.utcnow(),
            "comments": comment_data
        }

        try:
            collection.insert_one(doc)
        except Exception as e:
            print(f"❌ MongoDB 저장 중 문제 발생: {e}")