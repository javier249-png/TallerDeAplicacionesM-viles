# app/api/v2/users.py
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.schemas.user import UserDataExportResponse, AccountDeletionResponse
from app.core.security import get_current_user_id
from app.db.session import get_db
from app.db.models import User, PomodoroSession  # Modelos de SQLAlchemy administrados por el Dev de DB

router = APIRouter(prefix="/users/me", tags=["Privacidad y Gestión de Usuario (v2)"])

@router.get(
    "/data-export",
    response_model=UserDataExportResponse,
    status_code=status.HTTP_200_OK,
    summary="Exportar todos los datos del usuario (Portabilidad ARCO/GDPR)"
)
def export_user_data(
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Recopila y devuelve en formato JSON estructurado toda la información personal,
    métricas e historial de sesiones Pomodoro asociadas a la cuenta.
    """
    user = db.query(User).filter(User.id == current_user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado."
        )

    # Consulta el historial de sesiones Pomodoro del usuario
    sessions = db.query(PomodoroSession).filter(
        PomodoroSession.user_id == current_user_id
    ).order_by(PomodoroSession.started_at.desc()).all()

    return {
        "user_id": user.id,
        "email": user.email,
        "is_active": user.is_active,
        "created_at": user.created_at,
        "updated_at": user.updated_at,
        "pomodoro_sessions": sessions
    }

@router.delete(
    "/delete-account",
    response_model=AccountDeletionResponse,
    status_code=status.HTTP_200_OK,
    summary="Eliminar cuenta y datos definitivamente (Derecho de Cancelación)"
)
def delete_user_account(
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Elimina permanentemente el registro del usuario en MySQL.
    Gracias a las reglas ON DELETE CASCADE de la base de datos, 
    se purga todo el historial relacionado (sesiones, preferencias, etc.).
    """
    user = db.query(User).filter(User.id == current_user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado."
        )

    # Eliminación física en la base de datos
    db.delete(user)
    db.commit()

    return {
        "message": "Su cuenta y todos sus datos personales han sido eliminados de forma permanente de nuestros sistemas.",
        "deleted_at": datetime.now(timezone.utc)
    }