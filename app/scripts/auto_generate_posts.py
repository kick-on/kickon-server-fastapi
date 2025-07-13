from app.services.youtube_crawler import  crawl_and_store_comments_by_query
from app.services.extract_top_comments import extract_top_comments_per_video
from app.db.session import SessionLocal
from app.services.user_service import get_random_ai_user
from app.services.vector_store import save_faiss_index_from_mongo
from app.services.gpt_generate_post import run_rag_generation
import os

# 예시 경기 주제
topics = [
    "첼시 vs 플루미넨시"
]
# topics = [
#     "첼시 vs 플루미넨시",
#     "파리 생제르맹 vs 바이에른 뮌헨",
#     "레알 마드리드 vs 보루시아 도르트문트"
# ]

def main():
    db = SessionLocal()

    for topic in topics:
        try:
             crawl_and_store_comments_by_query(topic)  # MongoDB 저장
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
            print(f"- 이메일: {user.email}")
            print(f"- 상태: {user.status}")
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