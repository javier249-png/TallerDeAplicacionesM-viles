# app/schemas/user.py
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime
from app.schemas.pomodoro import PomodoroSessionResponse

# Esquema para la exportación completa de datos (Derecho de Acceso y Portabilidad)
class UserDataExportResponse(BaseModel):
    user_id: str
    email: EmailStr
    is_active: bool
    created_at: datetime
    updated_at: datetime
    pomodoro_sessions: List[PomodoroSessionResponse]

    class Config:
        from_attributes = True

# Respuesta al eliminar la cuenta (Derecho de Cancelación)
class AccountDeletionResponse(BaseModel):
    message: str
    deleted_at: datetime