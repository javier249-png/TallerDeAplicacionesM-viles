# app/schemas/audio.py
from pydantic import BaseModel, HttpUrl, Field
from typing import Optional, List
from enum import Enum

class CategoryTypeEnum(str, Enum):
    LOFI = "LOFI"
    CLASSICAL = "CLASSICAL"
    AMBIENT = "AMBIENT"
    BINAURAL = "BINAURAL"
    COLOR_NOISE = "COLOR_NOISE"
    NATURE = "NATURE"

class NoiseColorEnum(str, Enum):
    NONE = "NONE"
    WHITE = "WHITE"
    PINK = "PINK"
    BROWN = "BROWN"

# Respuesta individual de Categoría
class CategoryResponse(BaseModel):
    id: str
    name: str
    slug: str
    type: CategoryTypeEnum
    is_mixable: bool

    class Config:
        from_attributes = True

# Respuesta individual de una Pista de Audio
class TrackResponse(BaseModel):
    id: str
    title: str
    audio_url: str
    duration_seconds: int
    binaural_freq_hz: Optional[float] = Field(default=None, description="Ejemplo: 10.0 para ondas Alfa o 18.0 para Beta")
    noise_color: NoiseColorEnum = NoiseColorEnum.NONE
    is_loopable: bool
    category: CategoryResponse

    class Config:
        from_attributes = True

# Respuesta para Playlists en el Feed
class PlaylistResponse(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    cover_image_url: Optional[str] = None
    is_featured: bool
    tracks: List[TrackResponse] = []

    class Config:
        from_attributes = True

# Estructura principal para la interfaz Home / Feed estilo Spotify
class HomeFeedResponse(BaseModel):
    featured_playlists: List[PlaylistResponse]
    deep_focus_binaural: List[TrackResponse]
    ambient_layers: List[TrackResponse]  # Ruidos de color, lluvia, etc.