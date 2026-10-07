from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from db.database import get_db
from models.user import UserLogin, TokenResponse
from security.jwt import create_access_token, verify_password

router = APIRouter()

@router.post("/login", response_model=TokenResponse)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    # ------------------------------------------------------------------
    # MODO PRUEBA / MOCK (Úsalo mientras el DevOps configura la BD)
    # ------------------------------------------------------------------
    if credentials.email == "user@example.com" and credentials.password == "secret123":
        access_token = create_access_token(data={"sub": "user_123"})
        return {"access_token": access_token, "token_type": "bearer"}
    
    # ------------------------------------------------------------------
    # MODO PRODUCCIÓN / BASE DE DATOS (Descomentar cuando la BD esté lista)
    # ------------------------------------------------------------------
    # user = db.query(UserORM).filter(UserORM.email == credentials.email).first()
    # if user and verify_password(credentials.password, user.password_hash):
    #     access_token = create_access_token(data={"sub": str(user.id)})
    #     return {"access_token": access_token, "token_type": "bearer"}

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, 
        detail="Credenciales inválidas"
    )