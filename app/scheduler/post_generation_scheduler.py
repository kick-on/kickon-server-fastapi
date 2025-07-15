from apscheduler.schedulers.background import BackgroundScheduler
from datetime import timedelta, datetime, timezone
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
    
    print(f"📌 오늘 경기 수: {len(today_games)}")

    for game in today_games:
        start_time = game.started_at
        if start_time.tzinfo is None:
            start_time = start_time.replace(tzinfo=timezone.utc)

        home = game.home_team.name_kr if game.home_team else "?"
        away = game.away_team.name_kr if game.away_team else "?"
        topic = f"{home} {away} 하이라이트"

        print(f"⚽ 경기 등록: [{start_time}] {topic}")

        print(f"현재 시각 (UTC): {datetime.now(timezone.utc)}")
        print(f"현재 시각 (Local): {datetime.now()}")
        print(f"경기 시작 시각: {start_time} / 타입: {type(start_time)}")

        # Pre-game: 3시간 전부터 30분 간격
        scheduler.add_job(
            run_pregame_bot,
            'interval',
            minutes=30,
            start_date=start_time - timedelta(hours=3),
            end_date=start_time,
            timezone='UTC',
            id=f"pregame_{game.id}",
            kwargs={"topic": topic}
        )

        # Real-time: 경기 중 3분 간격
        scheduler.add_job(
            run_realtime_bot,
            'interval',
            minutes=3,
            start_date=start_time,
            end_date=start_time + timedelta(hours=2),
            timezone='UTC',
            id=f"realtime_{game.id}",
            kwargs={"topic": topic}
        )

        # Post-game Focus: 90분 후부터 2시간 동안 10분 간격
        scheduler.add_job(
            run_postgame_focus_bot,
            'interval',
            minutes=10,
            start_date=start_time + timedelta(minutes=90),
            end_date=start_time + timedelta(minutes=90 + 120),
            timezone='UTC',
            id=f"postgame_focus_{game.id}",
            kwargs={"topic": topic}
        )

    print("✅ 오늘 경기 기반 스케줄 등록 완료")