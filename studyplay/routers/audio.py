from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.database import get_db
from models.audio import TrackResponse, NoiseMixerRequest
from models.song import SongORM
from security.deps import get_current_user

router = APIRouter()


@router.get("/feed", response_model=List[TrackResponse])
async def get_spotify_feed(
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
async def update_noise_mixer(
    config: NoiseMixerRequest,
    current_user: str = Depends(get_current_user),
):
    return {"status": "configured", "mix": config.model_dump(), "user_id": current_user}


@router.get("/albums", summary="Listar álbumes de estudio")
async def get_albums():
    """
    Retorna el listado de álbumes dinámicos (Lo-Fi, Binaural, Ambient) para la HomeScreen.
    """
    # Aquí puedes consultar tu tabla 'albums' de la base de datos
    # Ejemplo de estructura estática/dinámica que espera el front:
    return {
        "status": "success",
        "data": [
            {
                "id": 1,
                "title": "Lo-Fi Focus Sessions",
                "description": "Ritmos suaves ideales para mantener la concentración profunda.",
                "cover_image_url": "https://images.unsplash.com/photo-1518609878373-06d740f60d8b",
                "category": "lo-fi"
            },
            {
                "id": 2,
                "title": "Binaural Alpha Waves",
                "description": "Frecuencias específicas para estimular la memoria y el estudio.",
                "cover_image_url": "https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4",
                "category": "binaural"
            }
        ]
    }


@router.get("/songs/{song_id}", summary="Obtener detalles y stream de una canción")
async def get_song_detail(song_id: int, db: AsyncSession = Depends(get_db)):
    if song_id < 1:
        raise HTTPException(status_code=404, detail="Pista de audio no encontrada")

    result = await db.execute(select(SongORM).where(SongORM.id == song_id))
    song = result.scalar_one_or_none()
    if song is None:
        raise HTTPException(status_code=404, detail="Pista de audio no encontrada")

    return {
        "status": "success",
        "data": {
            "id": song.id,
            "title": song.title,
            "artist": song.artist,
            "album_id": song.album_id,
            "audio_url": song.audio_url,
            "embed_html": song.embed_html,
            "duration_seconds": song.duration_seconds,
        }
    }