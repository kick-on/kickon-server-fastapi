import uuid
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from app.db.base_class import Base

class Board(Base):
    __tablename__ = "Board"

    pk = Column(Integer, primary_key=True, index=True)
    id = Column(UUID(as_uuid=True), default=uuid.uuid4)
    status = Column(String, default="ACTIVATED")
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
    etc = Column(String, nullable=True)

    user_pk = Column(Integer, ForeignKey("User.pk"), nullable=False)
    team_pk = Column(Integer, ForeignKey("Team.pk"), nullable=True)

    title = Column(String(255), nullable=False)
    contents = Column(Text, nullable=False)

    has_image = Column(Boolean, default=False)
    is_pinned = Column(Boolean, default=False)

    user = relationship("User", back_populates="boards", lazy="joined")
    team = relationship("Team", back_populates="boards", lazy="joined")