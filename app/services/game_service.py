from sqlalchemy.orm import Session
from typing import List
from app.models.game import Game
from app.models.team import Team
from datetime import datetime, date, timedelta

def get_game_topics(db: Session, since_date: str = "2025-07-01") -> List[str]:
    since = datetime.strptime(since_date, "%Y-%m-%d")
    today = datetime.combine(date.today(), datetime.min.time())  # 오늘 00:00

    games = (
        db.query(Game)
        .filter(Game.started_at >= since, Game.started_at <= today)
        .all()
    )

    print(f"[DEBUG] since: {since}, today: {today}")
    print(f"[DEBUG] {len(games)} games found between the range:")
    for g in games:
        print(f"  - Game ID: {g.pk}, started_at: {g.started_at}")

    team_dict = {team.pk: team.name_kr for team in db.query(Team).all()}

    topics = []
    for game in games:
        home = team_dict.get(game.home_team_pk, "알 수 없음")
        away = team_dict.get(game.away_team_pk, "알 수 없음")
        if home and away:
            topics.append(f"{home} {away} 하이라이트")
    return topics

def has_game_today(db: Session):
    """오늘 날짜에 해당하는 경기 목록을 반환. 없으면 빈 리스트."""
    today = datetime.utcnow().date()
    tomorrow = today + timedelta(days=1)

    games = (
        db.query(Game)
        .filter(Game.started_at >= today)
        .filter(Game.started_at < tomorrow)
        .all()
    )

    return games  # list[Game] 반환