from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.database import get_db
from models.user import ForgotPasswordRequest, TokenResponse
from models.user_orm import User
from security.jwt import create_access_token, hash_password, verify_password

router = APIRouter()


@router.post("/login", response_model=TokenResponse)
async def login(
    credentials: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(User).where(User.email == credentials.username)
    )
    user = result.scalar_one_or_none()

    if user and await verify_password(credentials.password, user.password_hash):
        access_token = await create_access_token(data={"sub": str(user.id)})
        return {"access_token": access_token, "token_type": "bearer"}

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales inválidas"
    )


@router.post("/forgot-password", summary="Solicitar recuperación de contraseña")
async def forgot_password(payload: ForgotPasswordRequest):
    return {
        "status": "accepted",
        "message": (
            "Si el correo está registrado, recibirás instrucciones cuando la "
            "recuperación por correo esté habilitada."
        ),
    }