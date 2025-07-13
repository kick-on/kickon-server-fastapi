from pymongo import MongoClient
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)

db = client["kickon"]
collection = db["youtube_comments"]

def extract_top_comments_per_video(topic=None, limit_per_video=30, min_length=15):
    """
    각 영상에서 like_count 상위 N개의 댓글만 추출
    - 너무 짧은 댓글은 제외
    - 반환 형식: List[dict]
    """
    query = {}
    if topic:
        query = {"team_mentioned": topic}

    all_docs = list(collection.find(query))
    selected_comments = []

    for doc in all_docs:
        comments = doc.get("comments", [])
        
        # like_count 없는 경우 0으로 처리
        for c in comments:
            c["like_count"] = c.get("like_count", 0)

        # 좋아요 수 기준 정렬
        sorted_comments = sorted(
            comments, key=lambda x: x["like_count"], reverse=True
        )

        # 너무 짧은 댓글 제외 + 상위 limit개 추출
        top_comments = [
            {
                "video_id": doc["video_id"],
                "video_title": doc["video_title"],
                "text": c["text"],
                "text_for_embedding": c.get("text_for_embedding", c["text"]),
                "like_count": c["like_count"],
                "created_at": datetime.utcnow().isoformat(),
                "match": doc.get("team_mentioned", topic),
            }
            for c in sorted_comments
            if len(c["text"]) >= min_length
        ][:limit_per_video]

        selected_comments.extend(top_comments)

    print(f"총 {len(selected_comments)}개 대표 댓글 추출 완료")
    return selected_comments