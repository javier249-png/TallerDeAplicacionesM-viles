from sqlalchemy import Column, Date, ForeignKey, Integer

from db.database import Base


class ActivityCompletionORM(Base):
    __tablename__ = "activity_daily_completions"

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    completion_date = Column(Date, primary_key=True)
    activity_id = Column(Integer, primary_key=True)
