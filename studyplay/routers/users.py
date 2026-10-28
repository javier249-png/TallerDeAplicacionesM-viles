from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from db.database import get_db
from models.user import UserProfileUpdate, UserRegister
from models.user_orm import UserORM
from security.deps import get_current_active_user
from security.jwt import hash_password

router = APIRouter()


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register_user(user: UserRegister, db: Session = Depends(get_db)):
    if not user.accept_terms or not user.data_processing_consent:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Debe aceptar expresamente el consentimiento de tratamiento de datos según la ley chilena.",
        )

    existing_user = db.query(UserORM).filter(UserORM.email == user.email).first()
    if existing_user is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe una cuenta con ese correo electrónico.",
        )

    consent_timestamp = datetime.now(timezone.utc)
    new_user = UserORM(
        email=user.email,
        password_hash=hash_password(user.password),
        accept_terms=user.accept_terms,
        data_processing_consent=user.data_processing_consent,
        consent_timestamp=consent_timestamp,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": "Usuario registrado exitosamente con consentimiento Ley N° 19.628.",
        "consent_timestamp": consent_timestamp,
    }


@router.get("/profile", summary="Obtener perfil del estudiante autenticado")
def get_user_profile(current_user: UserORM = Depends(get_current_active_user)):
    return {
        "status": "success",
        "data": {
            "id": current_user.id,
            "email": current_user.email,
            "name": current_user.name,
            "avatar_url": current_user.avatar_url,
            "xp": current_user.xp,
            "level": current_user.level,
        },
    }


@router.put("/profile", summary="Actualizar perfil y preferencias")
def update_user_profile(
    profile_data: UserProfileUpdate,
    current_user: UserORM = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    updates = profile_data.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(current_user, field, value)

    db.commit()

    return {
        "status": "success",
        "message": "Perfil actualizado correctamente",
    }