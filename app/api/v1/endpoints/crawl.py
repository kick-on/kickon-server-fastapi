# 뉴스 크롤링 관련
from fastapi import APIRouter

router = APIRouter()

@router.get("/crawl-news", tags=["Crawling"])
def crawl_news():
    """
    축구 뉴스 사이트에서 최신 뉴스를 수집하는 API입니다.
    """
    return {
        "message": "크롤링 작업이 아직 구현되지 않았습니다.",
        "status": "stub"
    }