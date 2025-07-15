import os
import time
import shutil
from app.services.youtube_crawler import crawl_and_store_comments_by_query
from app.services.extract_top_comments import extract_top_comments_per_video
from app.services.user_service import get_random_ai_user
from app.services.vector_store import save_faiss_index_from_mongo
from app.services.gpt_generate_post import run_rag_generation
from app.db.session import SessionLocal

def run_trend_bot():
    print("\n🚀 [Trend Bot] 일반 트렌드 게시글 생성 시작")
    db = SessionLocal()
    topics = get_trending_topics(db)

    for topic in topics:
        _generate_post(db, topic)

def run_pregame_bot(topic: str = None):
    print("\n⚽ [Pre-Game Bot] 경기 전 게시글 생성")
    db = SessionLocal()
    topics = [topic] if topic else get_game_topics(db)
    for t in topics:
        _generate_post(db, t)

def run_realtime_bot(topic: str = None):
    print("\n📺 [Real-Time Bot] 경기 중 게시글 생성")
    db = SessionLocal()
    topics = [topic] if topic else get_game_topics(db)
    for t in topics:
        _generate_post(db, t)

def run_postgame_focus_bot(topic: str = None):
    print("\n🎯 [Post-Game Focus Bot] 경기 직후 집중 게시글 생성")
    db = SessionLocal()
    topics = [topic] if topic else get_game_topics(db)
    for t in topics:
        _generate_post(db, t)

# 공통 로직
def _generate_post(db, topic: str):
    print(f"\n==== {topic} ====")

    try:
        crawl_and_store_comments_by_query(topic)
    except Exception as e:
        print(f"❌ 크롤링 실패: {e}")
        return

    try:
        top_comments = extract_top_comments_per_video(topic)
        if not top_comments:
            print(f"❌ {topic}에 대표 댓글 없음 → 스킵")
            return
    except Exception as e:
        print(f"❌ 대표 댓글 추출 실패: {e}")
        return

    try:
        if os.path.exists("kickon_vector_search/faiss_index"):
            shutil.rmtree("kickon_vector_search/faiss_index")

        save_faiss_index_from_mongo(top_comments)

        if not os.path.exists("kickon_vector_search/faiss_index/index.faiss"):
            print("❌ FAISS 인덱스 생성 실패 → 스킵")
            return
    except Exception as e:
        print(f"❌ 벡터 저장 실패: {e}")
        return

    user = get_random_ai_user(db)
    if not user:
        print("❌ 조건에 맞는 AI 유저 없음")
        return

    print(f"✅ 선택된 AI 유저: {user.nickname} ({user.email})")

    try:
        post, used_comments = run_rag_generation(user, topic)

        print(f"📣 생성된 게시글:\n{post}")
        print("\n🔍 사용된 댓글:")
        for c in used_comments:
            print(f"- {c}")
        # TODO: 게시글 저장 또는 업로드
    except Exception as e:
        print(f"❌ 게시글 생성 실패: {e}")

# 헬퍼 함수
from app.services.game_service import get_game_topics
def get_trending_topics(db):
    return get_game_topics(db)  # 필요 시 트렌드용 주제 추출로 대체