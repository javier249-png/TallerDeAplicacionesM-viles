from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session

from db.database import get_db
from models.user import ForgotPasswordRequest, TokenResponse, UserLogin
from models.user_orm import UserORM
from security.jwt import create_access_token, hash_password, verify_password

router = APIRouter()


@router.post("/login", response_model=TokenResponse)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    user = db.query(UserORM).filter(UserORM.email == credentials.email).first()

    if user and verify_password(credentials.password, user.password_hash):
        access_token = create_access_token(data={"sub": str(user.id)})
        return {"access_token": access_token, "token_type": "bearer"}

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales inválidas"
    )


@router.post("/forgot-password", summary="Solicitar recuperación de contraseña")
def forgot_password(payload: ForgotPasswordRequest):
    return {
        "status": "accepted",
        "message": (
            "Si el correo está registrado, recibirás instrucciones cuando la "
            "recuperación por correo esté habilitada."
        ),
    }