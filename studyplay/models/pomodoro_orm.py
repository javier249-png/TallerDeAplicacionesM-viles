from sqlalchemy import Column, DateTime, ForeignKey, Integer, func

from db.database import Base


class PomodoroSessionORM(Base):
    __tablename__ = "pomodoro_sessions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    album_id = Column(Integer, nullable=True)
    duration_seconds = Column(Integer, nullable=False)
    xp_earned = Column(Integer, nullable=False)
    created_at = Column(DateTime, nullable=True, server_default=func.now())
