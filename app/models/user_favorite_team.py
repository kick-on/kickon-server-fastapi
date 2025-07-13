from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class UserFavoriteTeam(Base):
    __tablename__ = "UserFavoriteTeam"

    pk = Column(Integer, primary_key=True, index=True)
    
    user_pk = Column(Integer, ForeignKey("User.pk", ondelete="CASCADE"))
    team_pk = Column(Integer, ForeignKey("Team.pk", ondelete="CASCADE"))

    priority_num = Column(Integer)

    user = relationship("User", back_populates="favorite_teams")
    team = relationship("Team", back_populates="favorite_for_users")