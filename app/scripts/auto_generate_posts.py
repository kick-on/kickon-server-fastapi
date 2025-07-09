from app.services.youtube_crawler import  crawl_and_store_comments_by_query
from app.services.vector_store import save_faiss_index_from_mongo
from app.services.gpt_generate_post import run_rag_generation
from app.data.fake_users import fake_users
import random

# 예시 경기 주제
topics = [
    "FC 서울 vs 포항 하이라이트",
    "수원FC vs 강원 FC 하이라이트",
    "대전 하나 vs 제주 SK FC 하이라이트"
]

def main():
    print("⚽️ 가상 팬 게시글 자동 생성 시작")

    for topic in topics:
        print(f"\n📥 크롤링 시작: {topic}")
        try:
             crawl_and_store_comments_by_query(topic)  # MongoDB 저장
        except Exception as e:
            print(f"❌ 크롤링 실패: {e}")
            continue

        print("📦 벡터 저장 시작")
        try:
            save_faiss_index_from_mongo()  # FAISS 업데이트
        except Exception as e:
            print(f"❌ 벡터 저장 실패: {e}")
            continue

        user = random.choice(fake_users)
        print(f"🙋 유저: {user['nickname']} ({user['team']})")

        try:
            content = run_rag_generation(user, topic)
            print(f"📣 생성된 게시글:\n{content}")
            # TODO: 게시글 업로드 or DB 저장
        except Exception as e:
            print(f"❌ 게시글 생성 실패: {e}")

if __name__ == "__main__":
    main()