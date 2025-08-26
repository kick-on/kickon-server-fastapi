import random
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import timedelta, datetime, timezone
from sqlalchemy.orm import Session
import boto3
import json
import uuid
from app.core.config import settings

from app.services.game_service import has_game_today

scheduler = BackgroundScheduler()

events = boto3.client('events')
lambda_client = boto3.client('lambda')

def setup_game_day_jobs(db: Session):
    today_games = has_game_today(db)

    if not today_games:
        print("🕒 오늘 경기가 없음 → [미구현] 일반 트렌드 봇만 스케줄 등록")
        return
    
    print(f"📌 오늘 경기 수: {len(today_games)}")

    for game in today_games:
        start_time = game.started_at
        if start_time.tzinfo is None:
            start_time = start_time.replace(tzinfo=timezone.utc)

        if not game.home_team or not game.away_team:
            print(f"❌ 팀 정보 누락 → 스킵: game_id={game.id}")
            continue
        topic = f"{game.home_team.name_kr} {game.away_team.name_kr} 하이라이트"

        print(f"⚽ 경기 등록: [{start_time}] {topic}")

        # 1. Pre-game: 3시간 전부터 경기 시작 전까지 5~20분 간격 랜덤 실행
        pre_start = start_time - timedelta(hours=3)
        pre_end = start_time
        _schedule_jobs_with_random_intervals(pre_start, pre_end, topic, "pregame", 5, 20)

        # 2. Real-time: 경기 중 1~3분 간격 랜덤 실행
        real_start = start_time
        real_end = start_time + timedelta(hours=2)
        _schedule_jobs_with_random_intervals(real_start, real_end, topic, "realtime", 1, 3)

        # 3. Post-game: 90분 후부터 2시간 동안 3~10분 간격 랜덤 실행
        post_start = start_time + timedelta(minutes=90)
        post_end = post_start + timedelta(minutes=120)
        _schedule_jobs_with_random_intervals(post_start, post_end, topic, "postgame", 3, 10)

    print("✅ 오늘 경기 기반 스케줄 등록 완료")

def _schedule_jobs_with_random_intervals(start_dt, end_dt, topic, bot_type, min_interval, max_interval):
    """
    지정된 시간 범위(start_dt ~ end_dt) 내에서 min~max 분 간격으로 랜덤 실행
    현재 시각 이후의 job만 등록함.
    """
    current_time = start_dt
    now = datetime.now(timezone.utc)

    while current_time < end_dt:
        interval_minutes = random.randint(min_interval, max_interval)
        current_time += timedelta(minutes=interval_minutes)

        if current_time >= end_dt:
            break
        if current_time <= now:
            continue  # 현재 시각 이전이면 skip

        register_lambda_schedule(current_time, bot_type, topic)

def register_lambda_schedule(run_at, bot_type, topic):
    """
    EventBridge 규칙을 생성하고 Lambda를 스케줄링합니다.
    schedule_expression은 cron 형식.
    """
    rule_name = f"kickon-{bot_type}-{uuid.uuid4().hex[:8]}"
    run_at_utc = run_at.astimezone(timezone.utc)
    
    schedule_expression = f"cron({run_at_utc.minute} {run_at_utc.hour} {run_at_utc.day} {run_at_utc.month} ? {run_at_utc.year})"
        
    region = settings.aws_region
    account_id = settings.aws_account_id
    lambda_function = settings.lambda_function_name
    
    lambda_arn = f"arn:aws:lambda:{region}:{account_id}:function:{lambda_function}"
    source_arn = f"arn:aws:events:{region}:{account_id}:rule/{rule_name}"

    # EventBridge 규칙 생성
    events.put_rule(
        Name=rule_name,
        ScheduleExpression=schedule_expression,
        State="ENABLED"
    )

    # Lambda 타겟 설정
    target_input = json.dumps({
        "task": "run_bot",
        "bot_type": bot_type,
        "topic": topic
    })
    events.put_targets(
        Rule=rule_name,
        Targets=[{
            "Id": "1",
            "Arn": lambda_arn,
            "Input": target_input
        }]
    )

    # Lambda 권한 부여
    try:
        lambda_client.add_permission(
            FunctionName=lambda_function,
            StatementId=f"{rule_name}-invoke",  # statementId 고정
            Action="lambda:InvokeFunction",
            Principal="events.amazonaws.com",
            SourceArn=source_arn
        )
    except lambda_client.exceptions.ResourceConflictException:
        print(f"✅ Permission already exists for {rule_name} — skipping duplicate permission.")
    except lambda_client.exceptions.PolicyLengthExceededException:
        print(f"❌ Policy length exceeded — skipping permission add for {rule_name}")

    print(f"📌 Lambda scheduled: {rule_name} ({schedule_expression})")