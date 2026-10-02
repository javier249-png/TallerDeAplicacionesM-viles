# app/db/models.py
import enum
import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column, String, Boolean, Integer, Float, DateTime, Enum, ForeignKey, Text
)
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

def generate_uuid():
    return str(uuid.uuid4())

# ==========================================
# ENUMERACIONES (Coinciden con Pydantic / DTOs)
# ==========================================

class CategoryTypeEnum(str, enum.Enum):
    LOFI = "LOFI"
    CLASSICAL = "CLASSICAL"
    AMBIENT = "AMBIENT"
    BINAURAL = "BINAURAL"
    COLOR_NOISE = "COLOR_NOISE"
    NATURE = "NATURE"

class NoiseColorEnum(str, enum.Enum):
    NONE = "NONE"
    WHITE = "WHITE"
    PINK = "PINK"
    BROWN = "BROWN"

class PomodoroStatusEnum(str, enum.Enum):
    COMPLETED = "COMPLETED"
    INTERRUPTED = "INTERRUPTED"

# ==========================================
# MODELOS DE BASE DE DATOS
# ==========================================

class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(
        DateTime, 
        default=lambda: datetime.now(timezone.utc), 
        onupdate=lambda: datetime.now(timezone.utc), 
        nullable=False
    )

    # Relaciones con eliminación en cascada (ON DELETE CASCADE)
    pomodoro_sessions = relationship("PomodoroSession", back_populates="user", cascade="all, delete-orphan")


class Category(Base):
    __tablename__ = "categories"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(100), nullable=False)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    type = Column(Enum(CategoryTypeEnum), nullable=False)
    is_mixable = Column(Boolean, default=False, nullable=False)

    tracks = relationship("Track", back_populates="category")


class Track(Base):
    __tablename__ = "tracks"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    category_id = Column(String(36), ForeignKey("categories.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    audio_url = Column(Text, nullable=False)
    duration_seconds = Column(Integer, nullable=False)
    binaural_freq_hz = Column(Float, nullable=True)
    noise_color = Column(Enum(NoiseColorEnum), default=NoiseColorEnum.NONE, nullable=False)
    is_loopable = Column(Boolean, default=True, nullable=False)

    category = relationship("Category", back_populates="tracks")
    playlist_tracks = relationship("PlaylistTrack", back_populates="track", cascade="all, delete-orphan")


class Playlist(Base):
    __tablename__ = "playlists"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    cover_image_url = Column(Text, nullable=True)
    is_featured = Column(Boolean, default=False, nullable=False)

    playlist_tracks = relationship("PlaylistTrack", back_populates="playlist", cascade="all, delete-orphan")


class PlaylistTrack(Base):
    """Tabla intermedia para asociar Pistas a Playlists con orden explícito."""
    __tablename__ = "playlist_tracks"

    playlist_id = Column(String(36), ForeignKey("playlists.id", ondelete="CASCADE"), primary_key=True)
    track_id = Column(String(36), ForeignKey("tracks.id", ondelete="CASCADE"), primary_key=True)
    position = Column(Integer, nullable=False, default=1)

    playlist = relationship("Playlist", back_populates="playlist_tracks")
    track = relationship("Track", back_populates="playlist_tracks")


class PomodoroSession(Base):
    __tablename__ = "pomodoro_sessions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    duration_minutes = Column(Integer, nullable=False)
    status = Column(Enum(PomodoroStatusEnum), nullable=False)
    started_at = Column(DateTime, nullable=False)
    ended_at = Column(DateTime, nullable=False)

    user = relationship("User", back_populates="pomodoro_sessions")