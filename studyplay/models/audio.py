from pydantic import BaseModel, Field
from typing import Optional

class TrackResponse(BaseModel):
    id: str
    title: str
    category: str
    brainwave_frequency: Optional[str] = None
    stream_url: str
    cover_art_url: str
    duration_seconds: int

class NoiseMixerRequest(BaseModel):
    white_noise_level: float = Field(0.0, ge=0.0, le=1.0)
    pink_noise_level: float = Field(0.0, ge=0.0, le=1.0)
    brown_noise_level: float = Field(0.0, ge=0.0, le=1.0)
    rain_ambient_level: float = Field(0.0, ge=0.0, le=1.0)
    wind_ambient_level: float = Field(0.0, ge=0.0, le=1.0)