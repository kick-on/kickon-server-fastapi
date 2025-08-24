from pymongo import MongoClient
from app.core.config import settings

client = MongoClient(settings.mongo_uri)
db = client["kickon"]

youtube_collection = db["youtube_comments"]
fmkorea_collection = db["fmkorea_posts"]

db.youtube_comments.create_index("video_id", unique=True)
db.fmkorea_posts.create_index("url", unique=True)

def save_youtube_comment_doc(doc: dict):
    if youtube_collection.find_one({"video_id": doc["video_id"]}):
        print(f"❌ 중복 스킵: {doc['video_id']}")
        return
    youtube_collection.insert_one(doc)

def is_video_already_crawled(video_id: str) -> bool:
    collection = db["youtube_comments"]
    return collection.find_one({"video_id": video_id}) is not None

def save_fmkorea_post_doc(doc: dict):
    if fmkorea_collection.find_one({"url": doc["url"]}):
        print(f"❌ 중복 스킵: {doc['url']}")
        return
    fmkorea_collection.insert_one(doc)