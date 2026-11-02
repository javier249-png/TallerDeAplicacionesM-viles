from sqlalchemy import Column, DateTime, ForeignKey, Integer, func

from db.database import Base


class ActivityCompletionORM(Base):
    __tablename__ = "activity_completions"

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    activity_id = Column(Integer, primary_key=True)
    completed_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
