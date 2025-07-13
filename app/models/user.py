from sqlalchemy import Column, String, DateTime
from app.db.base_class import Base

class User(Base):
    __tablename__ = "User"

    id = Column(String, primary_key=True, index=True)
    nickname = Column(String)
    email = Column(String)
    provider = Column(String)
    status = Column(String)