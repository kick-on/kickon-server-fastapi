import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, timezone
from app.db.sql.session import SessionLocal
from app.scheduler.post_generation_scheduler import scheduler, setup_game_day_jobs

if __name__ == "__main__":
    db = SessionLocal()

    print(f"🕒 [로컬 스케줄러] UTC Now: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')}")
    
    setup_game_day_jobs(db)
    db.close()
    
    scheduler.start()
    print("📆 로컬 스케줄러 실행 중... (종료: Ctrl+C)")

    print("📝 등록된 Job 목록:")
    for job in scheduler.get_jobs():
        print(job)

    try:
        while True:
            import time
            time.sleep(60)
    except (KeyboardInterrupt, SystemExit):
        print("🛑 종료 요청됨. 스케줄러 종료...")
        scheduler.shutdown()