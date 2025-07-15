import os
import shutil
from app.services.youtube_crawler import crawl_and_store_comments_by_query
from app.services.extract_top_comments import extract_top_comments_per_video
from app.services.user_service import get_random_ai_user
from app.services.vector_store import save_faiss_index_from_mongo
from app.services.gpt_generate_post import run_rag_generation
from app.db.session import SessionLocal

# 일반 상황용 (비시즌, 일정 없음 → 트렌딩 키워드 기반)
def run_trend_bot():
    print("\n🚀 [Trend Bot] 일반 트렌드 게시글 생성 시작")
    db = SessionLocal()
    
    topics = []  # TODO: 트렌드 키워드 로직 추가 (예: 트위터, 커뮤니티, 뉴스 기반 키워드 추출)

    if not topics:
        print("❌ 트렌드 키워드 없음 → 트렌드 봇 스킵")
        return
    
    for topic in topics:
        print(f"[Trend] 커뮤니티 크롤링 미구현 → 스킵: {topic}")
    
    db.close()

# 경기 전 (실시간 반응 분석 전 준비)
def run_pregame_bot(topic: str = None):
    print("\n⚽ [Pre-Game Bot] 경기 전 게시글 생성")
    if not topic:
        print("❌ topic이 지정되지 않아 run_pregame_bot을 건너뜁니다.")
        return

    db = SessionLocal()
    print(f"[Pre-Game] 커뮤니티 크롤링 미구현 → 스킵: {topic}")
    db.close()

# 실시간 경기 중 (3~5분 간격, 네이버 스포츠 중계 댓글 대상)
def run_realtime_bot(topic: str = None):
    print("\n📺 [Real-Time Bot] 경기 중 게시글 생성")
    if not topic:
        print("❌ topic이 지정되지 않아 run_realtime_bot을 건너뜁니다.")
        return

    db = SessionLocal()
    print(f"[Real-Time] 네이버 중계 댓글 크롤링 미구현 → 스킵: {topic}")
    db.close()

# 경기 직후 (하이라이트 및 팬 반응 분석)
def run_postgame_focus_bot(topic: str = None):
    print("\n🎯 [Post-Game Focus Bot] 경기 직후 게시글 생성")
    if not topic:
        print("❌ topic이 지정되지 않아 run_postgame_focus_bot을 건너뜁니다.")
        return

    db = SessionLocal()
    _generate_post_with_youtube(db, topic)
    db.close()

# 공통 로직
def _generate_post_with_youtube(db, topic: str):
    print(f"\n==== {topic} ====")

    try:
        crawl_and_store_comments_by_query(topic)
    except Exception as e:
        print(f"❌ 유튜브 댓글 크롤링 실패: {e}")
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
        faiss_dir = "kickon_vector_search/faiss_index"
        if os.path.exists(faiss_dir):
            shutil.rmtree(faiss_dir)

        save_faiss_index_from_mongo(top_comments)

        if not os.path.exists(os.path.join(faiss_dir, "index.faiss")):
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