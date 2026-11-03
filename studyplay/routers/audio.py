from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from db.database import get_db
from models.audio import TrackResponse, NoiseMixerRequest
from models.song import Song
from security.deps import get_current_user

router = APIRouter()


@router.get("/feed", response_model=List[TrackResponse])
async def get_spotify_feed(
    db: AsyncSession = Depends(get_db),
    category: Optional[str] = Query(None, description="lo-fi, clasica, ambient, asmr, 8d"),
    wave_type: Optional[str] = Query(None, description="Alfa, Beta, Theta")
):
    result = await db.execute(
        text(
            """
            SELECT
                s.id,
                s.title,
                s.audio_url AS stream_url,
                COALESCE(s.duration_seconds, 0) AS duration_seconds,
                COALESCE(MAX(a.cover_image_url), '') AS cover_art_url,
                COALESCE(
                    GROUP_CONCAT(DISTINCT c.name ORDER BY c.name SEPARATOR ', '),
                    ''
                ) AS category
            FROM songs AS s
            LEFT JOIN album_songs AS als ON als.song_id = s.id
            LEFT JOIN albums AS a ON a.id = als.album_id
            LEFT JOIN song_categories AS sc ON sc.song_id = s.id
            LEFT JOIN categories AS c ON c.id = sc.category_id
            WHERE (
                :category IS NULL OR EXISTS (
                    SELECT 1
                    FROM song_categories AS sc_filter
                    JOIN categories AS c_filter
                        ON c_filter.id = sc_filter.category_id
                    WHERE sc_filter.song_id = s.id
                      AND LOWER(c_filter.name) = LOWER(:category)
                )
            )
            AND (:wave_type IS NULL OR :wave_type = '')
            GROUP BY s.id, s.title, s.audio_url, s.duration_seconds
            ORDER BY s.id
            """
        ),
        {"category": category, "wave_type": wave_type},
    )
    return [
        {
            **track,
            "brainwave_frequency": "",
        }
        for track in result.mappings().all()
    ]


@router.post("/noise-generator/mix")
async def update_noise_mixer(
    config: NoiseMixerRequest,
    current_user: str = Depends(get_current_user),
):
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail=(
            "La base de datos actual no tiene una tabla para guardar la configuración "
            "del mezclador."
        ),
    )


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

    result = await db.execute(select(Song).where(Song.id == song_id))
    song = result.scalar_one_or_none()
    if song is None:
        raise HTTPException(status_code=404, detail="Pista de audio no encontrada")

    return {
        "status": "success",
        "data": {
            "id": song.id,
            "title": song.title,
            "artist": song.artist,
            "audio_url": song.audio_url,
            "duration_seconds": song.duration_seconds,
        }
    }