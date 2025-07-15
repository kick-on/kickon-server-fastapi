from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.bots.post_generation_bots import (
    run_trend_bot,
    run_pregame_bot,
    run_realtime_bot,
    run_postgame_focus_bot,
)
from app.services.game_service import has_game_today

scheduler = BackgroundScheduler()

def setup_game_day_jobs(db: Session):
    today_games = has_game_today(db)

    if not today_games:
        print("🕒 오늘 경기가 없음 → 일반 트렌드 봇만 스케줄 등록")
        scheduler.add_job(run_trend_bot, 'interval', hours=2)
        return

    for game in today_games:
        start_time = game.started_at

        # Pre-game: 3시간 전부터 30분 간격
        scheduler.add_job(
            run_pregame_bot,
            'interval',
            minutes=30,
            start_date=start_time - timedelta(hours=3),
            end_date=start_time,
            id=f"pregame_{game.id}",
            kwargs={"topic": game.topic}
        )

        # Real-time: 경기 중 3분 간격
        scheduler.add_job(
            run_realtime_bot,
            'interval',
            minutes=3,
            start_date=start_time,
            end_date=start_time + timedelta(hours=2),
            id=f"realtime_{game.id}",
            kwargs={"topic": game.topic}
        )

        # Post-game Focus: 2시간 후부터 2시간 동안 10분 간격
        scheduler.add_job(
            run_postgame_focus_bot,
            'interval',
            minutes=10,
            start_date=start_time + timedelta(hours=2),
            end_date=start_time + timedelta(hours=4),
            id=f"postgame_focus_{game.id}",
            kwargs={"topic": game.topic}
        )

    print("✅ 오늘 경기 기반 스케줄 등록 완료")