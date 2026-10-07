from fastapi import APIRouter, Depends, Query
from typing import List, Optional
from models.audio import TrackResponse, SpotifyFeedResponse, AudioCategory

router = APIRouter(prefix="/api/v1/audio", tags=["Audio & Feed"])

@router.get("/feed", response_model=SpotifyFeedResponse)
async def get_spotify_style_feed():
    """
    Retorna la estructura de datos optimizada para alimentar la interfaz 
    tipo Spotify en el Front-End.
    """
    # Lógica de servicio y respuesta mock estructurada
    sample_track = TrackResponse(
        id="trk-001",
        title="Deep Focus Alpha Waves 10Hz",
        artist="Cognitive Audio Lab",
        category=AudioCategory.BINAURAL,
        frequency_hz=10.0,
        stream_url="/stream/trk-001.mp3",
        cover_image_url="/covers/alpha.jpg",
        duration_seconds=1800
    )
    
    return SpotifyFeedResponse(
        recently_played=[sample_track],
        recommended_for_focus=[sample_track],
        binaural_beats=[sample_track],
        environmental_noises=[]
    )

@router.get("/tracks", response_model=List[TrackResponse])
async def list_tracks(
    category: Optional[AudioCategory] = None,
    limit: int = Query(default=20, le=50)
):
    """
    Filtra pistas por categorías específicas (Ruido blanco/marrón/rosado, ASMR, 8D, Ambient).
    """
    # El dev-back implementará la llamada al repositorio que maneje el DevOps
    return []