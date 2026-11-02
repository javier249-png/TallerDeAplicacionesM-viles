from sqlalchemy import Column, ForeignKey, Integer, String

from db.database import Base


class PomodoroTimerORM(Base):
    __tablename__ = "pomodoro_timers"

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    session_status = Column(String(16), nullable=False)
    remaining_seconds = Column(Integer, nullable=False)
    started_at_epoch = Column(Integer, nullable=True)
