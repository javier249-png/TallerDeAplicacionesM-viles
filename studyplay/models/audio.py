from pydantic import BaseModel, ConfigDict


class TrackResponse(BaseModel):
    id: str
    title: str
    category: str
    brainwave_frequency: str
    stream_url: str
    cover_art_url: str
    duration_seconds: int


class NoiseMixerRequest(BaseModel):
    model_config = ConfigDict(extra="allow")
