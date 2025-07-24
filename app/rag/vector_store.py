from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.docstore.document import Document
from pymongo import MongoClient
from sentence_transformers import SentenceTransformer
from datetime import datetime
import numpy as np
from tqdm import tqdm
import os
from dotenv import load_dotenv

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = "kickon"
COLLECTION_NAME = "youtube_comments"

# 임베딩 모델 설정 (저장 시와 일치해야 함)
embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# 저장 디렉토리
FAISS_DIR = "kickon_vector_search/faiss_index"

def save_faiss_index(embeddings, metadatas):
    """FAISS 인덱스를 생성하고 저장"""
    docs = [Document(page_content=meta["text"], metadata=meta) for meta in metadatas]
    vectorstore = FAISS.from_documents(docs, embedding_model)
    os.makedirs(FAISS_DIR, exist_ok=True)
    vectorstore.save_local(FAISS_DIR)

def load_faiss_index():
    """FAISS 인덱스를 로드"""
    if not os.path.exists(FAISS_DIR):
        raise FileNotFoundError("FAISS 인덱스가 존재하지 않습니다.")
    return FAISS.load_local(FAISS_DIR, embedding_model)

def save_faiss_index_from_mongo(top_comments):
    """
    대표 댓글(top_comments)을 받아 FAISS 인덱스를 생성하고 저장.
    """

    # client = MongoClient(MONGO_URI)
    # collection = client[DB_NAME][COLLECTION_NAME]

    model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    #all_docs = list(collection.find({}, {"video_id": 1, "comments.text_for_embedding": 1}))

    embeddings = []
    metadata = []

    # for doc in tqdm(all_docs):
    #     video_id = doc["video_id"]
    #     for comment in doc.get("comments", []):
    #         text = comment.get("text_for_embedding")
    #         if text:
    #             emb = model.encode(text)
    #             embeddings.append(emb)
    #             metadata.append({
    #                 "video_id": video_id,
    #                 "text": text,
    #                 "created_at": datetime.utcnow().isoformat()
    #             })

    for comment in tqdm(top_comments):
        text = comment.get("text_for_embedding")
        if text:
            emb = model.encode(text)
            embeddings.append(emb)
            metadata.append({
                "video_id": comment["video_id"],
                "text": text,
                "query": comment.get("query", ""),
                "like_count": comment.get("like_count", 0),
                "created_at": comment.get("created_at", datetime.utcnow().isoformat())
            })

    if embeddings:
        save_faiss_index(np.array(embeddings), metadata)
        print(f"✅ 총 {len(embeddings)}개 문장 벡터 저장 완료")
    else:
        print("⚠️ 저장할 임베딩이 없습니다")