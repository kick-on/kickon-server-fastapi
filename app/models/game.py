from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.db.sql.base_class import Base
from app.models.team import Team

class Game(Base):
    __tablename__ = "Game"

    pk = Column(Integer, primary_key=True, index=True)
    id = Column(String, unique=True, index=True)  # UUID 혹은 API 제공 id
    api_id = Column(Integer, unique=True, index=True)

    home_team_pk = Column(Integer, ForeignKey("Team.pk"))
    away_team_pk = Column(Integer, ForeignKey("Team.pk"))
    home_score = Column(Integer)
    away_score = Column(Integer)
    home_penalty_score = Column(Integer, nullable=True)
    away_penalty_score = Column(Integer, nullable=True)

    actual_season_pk = Column(Integer)
    round = Column(String)
    started_at = Column(DateTime)
    game_status = Column(String)

    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    home_team = relationship("Team", foreign_keys=[home_team_pk])
    away_team = relationship("Team", foreign_keys=[away_team_pk])