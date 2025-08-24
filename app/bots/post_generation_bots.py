import os
import shutil
from app.crawlers.youtube_crawler import crawl_and_store_comments_by_query
from app.crawlers.fmkorea_crawler import crawl_fmkorea_board 
from app.rag.extract_top_comments import extract_top_comments_per_video, extract_top_fmkorea_posts
from app.services.user_service import get_random_ai_user
from app.rag.vector_store import save_faiss_index_from_mongo
from app.rag.gpt_generate_post import run_rag_generation
from app.db.sql.session import SessionLocal
from app.services.board_service import save_generated_post

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
    _generate_post_with_fmkorea(db, topic)
    db.close()

# 실시간 경기 중 (3~5분 간격, 네이버 스포츠 중계 댓글 대상)
def run_realtime_bot(topic: str = None):
    print("\n📺 [Real-Time Bot] 경기 중 게시글 생성")
    if not topic:
        print("❌ topic이 지정되지 않아 run_realtime_bot을 건너뜁니다.")
        return

    db = SessionLocal()
    _generate_post_with_fmkorea(db, topic)
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
def _generate_post_with_source(db, topic: str, source_loader_fn, source_name: str):
    print(f"\n==== {topic} ({source_name}) ====")

    try:
        sources = source_loader_fn(topic)
        if not sources:
            print(f"❌ {topic}에 사용할 {source_name} 데이터 없음 → 스킵")
            return
    except Exception as e:
        print(f"❌ {source_name} 데이터 로딩 실패: {e}")
        return

    try:
        faiss_dir = "kickon_vector_search/faiss_index"
        if os.path.exists(faiss_dir):
            shutil.rmtree(faiss_dir)

        save_faiss_index_from_mongo(sources)

        if not os.path.exists(os.path.join(faiss_dir, "index.faiss")):
            print(f"❌ FAISS 인덱스 생성 실패 → 스킵")
            return
    except Exception as e:
        print(f"❌ 벡터 저장 실패: {e}")
        return

    user = get_random_ai_user(db)
    if not user:
        print("❌ 조건에 맞는 AI 유저 없음")
        return

    print(f"✅ 선택된 AI 유저: {user.nickname} ({user.pk})")

    try:
        generated, used_sources = run_rag_generation(user, topic)

        print(f"📣 생성된 게시글:\n{generated['title']}\n{generated['contents']}")
        print("\n🔍 사용된 소스:")
        for s in used_sources:
            print(f"- {s}")
        
        saved = save_generated_post(
            db=db,
            user_pk=user.pk,
            title=generated["title"],
            contents=generated["contents"],
            has_image=False
        )
        print(f"✅ 게시글 저장 완료! pk = {saved.pk}")

    except Exception as e:
        print(f"❌ 게시글 생성 실패: {e}")

def _generate_post_with_youtube(db, topic: str):
    try:
        crawl_and_store_comments_by_query(topic)
    except Exception as e:
        print(f"❌ 유튜브 댓글 크롤링 실패: {e}")
        return

    _generate_post_with_source(
        db=db,
        topic=topic,
        source_loader_fn=extract_top_comments_per_video,
        source_name="YouTube"
    )

def _generate_post_with_fmkorea(db, topic: str):
    try:
        crawl_fmkorea_board(topic)
    except Exception as e:
        print(f"❌ 에펨코리아 크롤링 실패: {e}")
        return
    
    _generate_post_with_source(
        db=db,
        topic=topic,
        source_loader_fn=lambda t: extract_top_fmkorea_posts(limit=20, sort_by="like_count"),
        source_name="FMKorea"
    )