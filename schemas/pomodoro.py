# app/schemas/pomodoro.py
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class PomodoroStatusEnum(str, Enum):
    RUNNING = "RUNNING"
    PAUSED = "PAUSED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"

class PomodoroEventTypeEnum(str, Enum):
    PAUSE = "PAUSE"
    RESUME = "RESUME"
    COMPLETE_CYCLE = "COMPLETE_CYCLE"
    FINISH = "FINISH"
    CANCEL = "CANCEL"

# Petición para iniciar un Pomodoro
class PomodoroStartRequest(BaseModel):
    work_duration_minutes: int = Field(default=25, ge=1, le=120, description="Minutos de estudio/enfoque")
    break_duration_minutes: int = Field(default=5, ge=1, le=60, description="Minutos de descanso")

# Petición para enviar eventos del temporizador desde la App Móvil
class PomodoroEventRequest(BaseModel):
    session_id: str
    event_type: PomodoroEventTypeEnum

# Respuesta de la Sesión
class PomodoroSessionResponse(BaseModel):
    session_id: str
    user_id: str
    work_duration_minutes: int
    break_duration_minutes: int
    completed_cycles: int
    status: PomodoroStatusEnum
    started_at: datetime
    ended_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Respuesta con la instrucción directa para el reproductor de audio móvil
class PomodoroAudioActionResponse(BaseModel):
    session_id: str
    current_status: PomodoroStatusEnum
    completed_cycles: int
    audio_action: str = Field(description="Acción que la App Móvil debe ejecutar en el reproductor (ej. PAUSE, PLAY, PLAY_BREAK_SOUND)")
    message: str