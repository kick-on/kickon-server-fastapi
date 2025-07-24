from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# SQLAlchemy 엔진 생성
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,  # 연결 상태 체크
)

# 세션 로컬 클래스 정의
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)