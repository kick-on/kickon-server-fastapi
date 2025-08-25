from pymongo import MongoClient
from app.core.config import settings

client = MongoClient(settings.mongo_uri)
db = client["kickon"]

youtube_collection = db["youtube_comments"]
fmkorea_collection = db["fmkorea_posts"]

# 중복 인덱스 생성 방지
youtube_indexes = youtube_collection.index_information()
if not any(index["key"] == [("video_id", 1)] for index in youtube_indexes.values()):
    youtube_collection.create_index("video_id", unique=True)
else:
    print("ℹ️ youtube_comments: video_id 인덱스 이미 존재")

fmkorea_indexes = fmkorea_collection.index_information()
if not any(index["key"] == [("url", 1)] for index in fmkorea_indexes.values()):
    fmkorea_collection.create_index("url", unique=True)
else:
    print("ℹ️ fmkorea_posts: url 인덱스 이미 존재")

# 중복 저장 방지 포함된 저장 함수들
def save_youtube_comment_doc(doc: dict):
    if youtube_collection.find_one({"video_id": doc["video_id"]}):
        print(f"❌ 중복 스킵: {doc['video_id']}")
        return
    youtube_collection.insert_one(doc)

def is_video_already_crawled(video_id: str) -> bool:
    return youtube_collection.find_one({"video_id": video_id}) is not None

def save_fmkorea_post_doc(doc: dict):
    if fmkorea_collection.find_one({"url": doc["url"]}):
        print(f"❌ 중복 스킵: {doc['url']}")
        return
    fmkorea_collection.insert_one(doc)