from sqlalchemy import Column, DateTime, Integer, String, Text, func
from db.database import Base

class Song(Base):
    __tablename__ = "songs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    artist = Column(String(255), nullable=True)
    audio_url = Column(Text, nullable=False)
    duration_seconds = Column(Integer, nullable=False)
    created_at = Column(DateTime, nullable=True, server_default=func.now())