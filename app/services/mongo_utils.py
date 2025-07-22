from pymongo import MongoClient
from app.core.config import settings

client = MongoClient(settings.mongo_uri)
db = client["kickon"]

youtube_collection = db["youtube_comments"]
fmkorea_collection = db["fmkorea_posts"]

def save_youtube_comment_doc(doc: dict):
    youtube_collection.insert_one(doc)

def save_fmkorea_post_doc(doc: dict):
    fmkorea_collection.insert_one(doc)

def is_video_already_crawled(video_id: str) -> bool:
    collection = db["youtube_comments"]
    return collection.find_one({"video_id": video_id}) is not None