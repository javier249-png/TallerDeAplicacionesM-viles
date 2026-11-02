from sqlalchemy import Column, Integer, String, Text
from db.database import Base

class SongORM(Base):
    __tablename__ = "songs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    artist = Column(String(255), nullable=False)
    album_id = Column(Integer, nullable=False)
    audio_url = Column(String(500), nullable=True)
    embed_html = Column(Text, nullable=True)  # <--- Campo para el iframe de YouTube
    duration_seconds = Column(Integer, nullable=False)