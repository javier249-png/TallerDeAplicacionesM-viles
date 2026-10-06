# app/api/v2/feed.py
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session, joinedload

from app.schemas.audio import HomeFeedResponse, TrackResponse, PlaylistResponse
from app.db.session import get_db
from app.db.models import Playlist, Track, Category, CategoryTypeEnum

router = APIRouter(prefix="/feed", tags=["Feed Principal (v2)"])

@router.get(
    "/",
    response_model=HomeFeedResponse,
    status_code=status.HTTP_200_OK,
    summary="Obtener el feed principal estilo Spotify"
)
def get_home_feed(db: Session = Depends(get_db)):
    """
    Entrega el feed inicial de la aplicación móvil compuesto por:
    1. Playlists destacadas con sus pistas correspondientes.
    2. Pistas con frecuencias binaurales (ondas Alfa / Beta).
    3. Capas de sonido independientes (ruidos de color, lluvia) listos para mezcla.
    """
    # 1. Consultar Playlists destacadas
    featured_playlists_query = (
        db.query(Playlist)
        .filter(Playlist.is_featured == True)
        .options(joinedload(Playlist.playlist_tracks).joinedload(Track.category))
        .limit(10)
        .all()
    )

    featured_playlists = []
    for playlist in featured_playlists_query:
        # Mapea las pistas ordenadas dentro de la relación
        sorted_tracks = [pt.track for pt in sorted(playlist.playlist_tracks, key=lambda x: x.position)]
        playlist_dict = {
            "id": playlist.id,
            "title": playlist.title,
            "description": playlist.description,
            "cover_image_url": playlist.cover_image_url,
            "is_featured": playlist.is_featured,
            "tracks": sorted_tracks
        }
        featured_playlists.append(playlist_dict)

    # 2. Consultar pistas de Frecuencia Binaural
    binaural_tracks = (
        db.query(Track)
        .join(Category)
        .filter(Category.type == CategoryTypeEnum.BINAURAL)
        .options(joinedload(Track.category))
        .limit(10)
        .all()
    )

    # 3. Consultar capas mezclables (Ruidos de color, sonidos de la naturaleza)
    ambient_layers = (
        db.query(Track)
        .join(Category)
        .filter(Category.is_mixable == True)
        .options(joinedload(Track.category))
        .all()
    )

    return {
        "featured_playlists": featured_playlists,
        "deep_focus_binaural": binaural_tracks,
        "ambient_layers": ambient_layers
    }