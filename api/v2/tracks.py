# app/api/v2/tracks.py
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional

from app.schemas.audio import TrackResponse, CategoryTypeEnum, NoiseColorEnum
from app.db.session import get_db
from app.db.models import Track, Category

router = APIRouter(prefix="/tracks", tags=["Catálogo y Capas de Audio (v2)"])

@router.get(
    "/",
    response_model=List[TrackResponse],
    status_code=status.HTTP_200_OK,
    summary="Listar catálogo de pistas con filtros"
)
def list_tracks(
    category_type: Optional[CategoryTypeEnum] = Query(None, description="Filtrar por tipo de categoría"),
    noise_color: Optional[NoiseColorEnum] = Query(None, description="Filtrar por color de ruido"),
    db: Session = Depends(get_db)
):
    """
    Permite a la aplicación móvil consultar pistas filtradas según el contexto del usuario.
    """
    query = db.query(Track).options(joinedload(Track.category))

    if category_type:
        query = query.join(Category).filter(Category.type == category_type)
    
    if noise_color and noise_color != NoiseColorEnum.NONE:
        query = query.filter(Track.noise_color == noise_color)

    return query.all()

@router.get(
    "/soundscapes/layers",
    response_model=List[TrackResponse],
    status_code=status.HTTP_200_OK,
    summary="Obtener capas de fondo independientes (ruidos de color y ambientes)"
)
def get_ambient_layers(db: Session = Depends(get_db)):
    """
    Devuelve los elementos de sonido diseñados para ser reproducidos en segundo plano
    como capas simultáneas (ruido blanco/rosa/marrón, lluvia, viento).
    """
    layers = (
        db.query(Track)
        .join(Category)
        .filter(Category.is_mixable == True)
        .options(joinedload(Track.category))
        .all()
    )
    return layers