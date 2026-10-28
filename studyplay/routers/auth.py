from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from db.database import get_db
from models.user import UserLogin, TokenResponse
from security.jwt import create_access_token, verify_password

router = APIRouter()

@router.post("/login", response_model=TokenResponse)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    # ------------------------------------------------------------------
    # MODO PRODUCCIÓN / BASE DE DATOS 
    # ------------------------------------------------------------------
    # Nota: Asegúrate de importar tu modelo ORM (ej. from models.user_orm import UserORM)
    user = db.query(UserORM).filter(UserORM.email == credentials.email).first()
    
    if user and verify_password(credentials.password, user.password_hash):
        access_token = create_access_token(data={"sub": str(user.id)})
        return {"access_token": access_token, "token_type": "bearer"}

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, 
        detail="Credenciales inválidas"
    )

@router.post("/forgot-password", summary="Solicitar recuperación de contraseña")
def forgot_password(payload: dict, db: Session = Depends(get_db)):
    """
    Recibe el correo electrónico del estudiante y procesa la solicitud 
    de recuperación de contraseña para la ForgotPasswordScreen.
    """
    email = payload.get("email")
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El correo electrónico es obligatorio."
        )
    
    # Validar si el usuario existe (opcionalmente puedes no revelar si el correo existe por seguridad)
    user = db.query(UserORM).filter(UserORM.email == email).first()
    
    # Aquí puedes integrar la lógica para enviar el correo (ej. con Celery, SendGrid, etc.)
    # Por seguridad, siempre retornamos un mensaje genérico de éxito:
    return {
        "status": "success",
        "message": "Si el correo está registrado, se han enviado las instrucciones para restablecer la contraseña."
    }