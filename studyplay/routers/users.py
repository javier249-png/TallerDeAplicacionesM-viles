from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, status, Depends
from models.user import UserRegister

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