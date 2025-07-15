import os
import time
from app.services.youtube_crawler import  crawl_and_store_comments_by_query
from app.services.extract_top_comments import extract_top_comments_per_video
from app.services.user_service import get_random_ai_user
from app.services.game_service import get_game_topics
from app.services.vector_store import save_faiss_index_from_mongo
from app.services.gpt_generate_post import run_rag_generation
from app.db.session import SessionLocal

def main():
    db = SessionLocal()

    topics = get_game_topics(db)

    for topic in topics:
        time.sleep(5)
        print(f"\n==== {topic} ====")

        try:
             crawl_and_store_comments_by_query(topic)
        except Exception as e:
            print(f"❌ 크롤링 실패: {e}")
            continue

        try:
            top_comments = extract_top_comments_per_video(topic)
            if not top_comments:
                print(f"❌ {topic}에 대표 댓글 없음 → 스킵")
                continue
        except Exception as e:
            print(f"❌ 대표 댓글 추출 실패: {e}")
            continue

        try:
            import shutil
            if os.path.exists("kickon_vector_search/faiss_index"):
                shutil.rmtree("kickon_vector_search/faiss_index")

            save_faiss_index_from_mongo(top_comments)

            if not os.path.exists("kickon_vector_search/faiss_index/index.faiss"):
                print("❌ FAISS 인덱스 생성 실패 → 스킵")
                continue
        except Exception as e:
            print(f"❌ 벡터 저장 실패: {e}")
            continue

        user = get_random_ai_user(db)

        if user:
            print("✅ 선택된 AI 유저:")
            print(f"- ID: {user.id}")
            print(f"- 닉네임: {user.nickname}")
        else:
            print("❌ 조건에 맞는 AI 유저 없음")

        try:
            post, used_comments = run_rag_generation(user, topic)

            print(f"📣 생성된 게시글:\n{post}")
            print("\n🔍 사용된 댓글:")
            for c in used_comments:
                print(f"- {c}")

            # TODO: 게시글 업로드 or DB 저장
        except Exception as e:
            print(f"❌ 게시글 생성 실패: {e}")

if __name__ == "__main__":
    main()