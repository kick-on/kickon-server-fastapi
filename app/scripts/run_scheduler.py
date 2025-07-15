from app.scheduler.post_generation_scheduler import scheduler, setup_game_day_jobs
from app.db.session import SessionLocal

if __name__ == "__main__":
    db = SessionLocal()
    setup_game_day_jobs(db)
    scheduler.start()
    print("📆 스케줄러 실행 중...")

    # 유지용 루프
    import time
    try:
        while True:
            time.sleep(60)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()