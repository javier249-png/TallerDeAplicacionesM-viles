from pydantic import BaseModel, ConfigDict, Field


class TrackResponse(BaseModel):
    id: int
    title: str
    category: str
    brainwave_frequency: str
    stream_url: str
    cover_art_url: str
    duration_seconds: int


class NoiseMixerRequest(BaseModel):
    white_noise_volume: float = Field(ge=0.0, le=1.0)
    rain_volume: float = Field(ge=0.0, le=1.0)
    cafe_volume: float = Field(ge=0.0, le=1.0)
    model_config = ConfigDict(extra="forbid")
