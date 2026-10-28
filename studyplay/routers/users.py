from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, status, Depends
from models.user import UserRegister
from sqlalchemy.orm import Session
from db.database import get_db
from models import User
from auth_utils import get_current_active_user

router = APIRouter()

@router.post("/register", status_code=status.HTTP_201_CREATED)
def register_user(user: UserRegister):
    if not user.accept_terms or not user.data_processing_consent:
        raise HTTPException(
            status_code=400,
            detail="Debe aceptar expresamente el consentimiento de tratamiento de datos segun la ley chilena."
        )
    
    # Asignas la marca de tiempo exacta de la aceptación antes de guardar en la BD
    user.consent_timestamp = datetime.now(timezone.utc)
    
    return {
        "message": "Usuario registrado exitosamente con consentimiento Ley N° 19.628.",
        "consent_timestamp": user.consent_timestamp
    }

@router.get("/profile", summary="Obtener perfil del estudiante autenticado")
def get_user_profile(current_user = Depends(get_current_active_user)):
    """
    Retorna los datos del estudiante para mostrar en ProfileScreen (nombre, XP, nivel, avatar).
    """
    return {
        "status": "success",
        "data": {
            "id": current_user.id,
            "email": current_user.email,
            "name": getattr(current_user, "name", "Estudiante StudyPlay"),
            "avatar_url": getattr(current_user, "avatar_url", None),
            "xp": getattr(current_user, "xp", 0),
            "level": getattr(current_user, "level", 1)
        }
    }

@router.put("/profile", summary="Actualizar perfil y preferencias")
def update_user_profile(profile_data: dict, current_user = Depends(get_current_active_user), db: Session = Depends(get_db)):
    """
    Permite modificar la información o preferencias desde SettingsScreen.
    """
    # Ejemplo básico de actualización de campos permitidos
    if "name" in profile_data:
        current_user.name = profile_data["name"]
    if "avatar_url" in profile_data:
        current_user.avatar_url = profile_data["avatar_url"]
        
    db.commit()
    
    return {
        "status": "success",
        "message": "Perfil actualizado correctamente"
    }