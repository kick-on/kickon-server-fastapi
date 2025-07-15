import random
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.date import DateTrigger
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

        # 1. Pre-game: 3시간 전부터 경기 시작 전까지 5~20분 간격 랜덤 실행
        pre_start = start_time - timedelta(hours=3)
        pre_end = start_time
        _schedule_jobs_with_random_intervals(pre_start, pre_end, run_pregame_bot, topic, f"pregame_{game.id}", min_interval=5, max_interval=20)

        # 2. Real-time: 경기 중 1~3분 간격 랜덤 실행
        real_start = start_time
        real_end = start_time + timedelta(hours=2)
        _schedule_jobs_with_random_intervals(real_start, real_end, run_realtime_bot, topic, f"realtime_{game.id}", min_interval=1, max_interval=3)

        # 3. Post-game: 90분 후부터 2시간 동안 3~10분 간격 랜덤 실행
        post_start = start_time + timedelta(minutes=90)
        post_end = post_start + timedelta(minutes=120)
        _schedule_jobs_with_random_intervals(post_start, post_end, run_postgame_focus_bot, topic, f"postgame_focus_{game.id}", min_interval=3, max_interval=10)

    print("✅ 오늘 경기 기반 스케줄 등록 완료")


def _schedule_jobs_with_random_intervals(start_dt, end_dt, func, topic, job_prefix, min_interval, max_interval):
    """
    지정된 시간 범위(start_dt ~ end_dt) 내에서 min~max 분 간격으로 랜덤 실행
    현재 시각 이후의 job만 등록함.
    """
    current_time = start_dt
    i = 0
    now = datetime.now(timezone.utc)

    while current_time < end_dt:
        interval_minutes = random.randint(min_interval, max_interval)
        current_time += timedelta(minutes=interval_minutes)

        if current_time >= end_dt:
            break
        if current_time <= now:
            continue  # 현재 시각 이전이면 skip

        scheduler.add_job(
            func,
            trigger=DateTrigger(run_date=current_time, timezone="UTC"),
            id=f"{job_prefix}_{i}",
            kwargs={"topic": topic}
        )
        i += 1