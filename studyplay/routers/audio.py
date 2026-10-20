from fastapi import APIRouter, Query, Depends
from typing import List, Optional
from models.audio import TrackResponse, NoiseMixerRequest
from security.deps import get_current_user

router = APIRouter()

@router.get("/feed", response_model=List[TrackResponse])
def get_spotify_feed(
    category: Optional[str] = Query(None, description="lo-fi, clasica, ambient, asmr, 8d"),
    wave_type: Optional[str] = Query(None, description="Alfa, Beta, Theta")
):
    return [
        {
            "id": "trk_01",
            "title": "Deep Focus Alpha Waves 10Hz",
            "category": "ambient",
            "brainwave_frequency": "Alfa",
            "stream_url": "https://cdn.tuapp.cl/audio/alpha.mp3",
            "cover_art_url": "https://cdn.tuapp.cl/covers/alpha.jpg",
            "duration_seconds": 3600
        }
    ]

@router.post("/noise-generator/mix")
def update_noise_mixer(config: NoiseMixerRequest, current_user: str = Depends(get_current_user)):
    return {"status": "configured", "mix": config.model_dump(), "user_id": current_user}