from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class Team(Base):
    __tablename__ = "Team"

    pk = Column(Integer, primary_key=True, index=True)
    id = Column(String, unique=True, index=True)  # UUID
    code = Column(String)
    api_id = Column(Integer)
    status = Column(String)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    name_kr = Column(String)
    name_en = Column(String)
    logo_url = Column(String)

    favorite_for_users = relationship("UserFavoriteTeam", back_populates="team")
    boards = relationship("Board", back_populates="team")