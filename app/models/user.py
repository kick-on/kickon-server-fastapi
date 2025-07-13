from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class User(Base):
    __tablename__ = "User"

    pk = Column(Integer, primary_key=True, index=True) 
    id = Column(String, primary_key=True, index=True)
    nickname = Column(String)
    email = Column(String)
    provider = Column(String)
    status = Column(String)

    favorite_teams = relationship("UserFavoriteTeam", back_populates="user")