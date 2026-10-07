from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

class AudioCategory(str, Enum):
    LOFI = "lo-fi"
    CLASSICAL = "música clásica"
    AMBIENT = "ambient"
    BINAURAL = "ondas binaurales (alfa/beta)"
    NOISE = "ruido (blanco/marrón/rosado)"
    EIGHT_D = "audio 8d"
    ASMR = "asmr"

class TrackResponse(BaseModel):
    id: str
    title: str
    artist: str
    category: AudioCategory
    frequency_hz: Optional[float] = Field(None, description="Frecuencia binaural estimada (ej. 10Hz para Alfa, 18Hz para Beta)")
    stream_url: str
    cover_image_url: str
    duration_seconds: int

class SpotifyFeedResponse(BaseModel):
    recently_played: List[TrackResponse]
    recommended_for_focus: List[TrackResponse]
    binaural_beats: List[TrackResponse]
    environmental_noises: List[TrackResponse]

# Pomodoro Models
class PomodoroState(str, Enum):
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"

class PomodoroAction(BaseModel):
    session_id: str
    state: PomodoroState
    current_time_seconds: int

class PomodoroPlayerSync(BaseModel):
    session_id: str
    state: PomodoroState
    player_must_stop: bool
    remaining_time_seconds: int