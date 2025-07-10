from app.services.youtube_crawler import  crawl_and_store_comments_by_query
from app.services.extract_top_comments import extract_top_comments_per_video
from app.services.vector_store import save_faiss_index_from_mongo
from app.services.gpt_generate_post import run_rag_generation
from app.data.fake_users import fake_users
import random
import os

# 예시 경기 주제
topics = [
    "첼시 vs 플루미넨시",
    "파리 생제르맹 vs 바이에른 뮌헨",
    "레알 마드리드 vs 보루시아 도르트문트"
]

def main():

    for topic in topics:
        try:
             crawl_and_store_comments_by_query(topic)  # MongoDB 저장
        except Exception as e:
            print(f"❌ 크롤링 실패: {e}")
            continue

        try:
            top_comments = extract_top_comments_per_video(topic)
        except Exception as e:
            print(f"❌ 대표 댓글 추출 실패: {e}")
            continue

        try:
            import shutil
            if os.path.exists("kickon_vector_search/faiss_index"):
                shutil.rmtree("kickon_vector_search/faiss_index")

            save_faiss_index_from_mongo(top_comments)
        except Exception as e:
            print(f"❌ 벡터 저장 실패: {e}")
            continue

        user = random.choice(fake_users)

        try:
            content = run_rag_generation(user, topic)
            print(f"📣 생성된 게시글:\n{content}")
            # TODO: 게시글 업로드 or DB 저장
        except Exception as e:
            print(f"❌ 게시글 생성 실패: {e}")

if __name__ == "__main__":
    main()