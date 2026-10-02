# app/api/v2/pomodoro.py
import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.schemas.pomodoro import (
    PomodoroStartRequest,
    PomodoroEventRequest,
    PomodoroSessionResponse,
    PomodoroAudioActionResponse,
    PomodoroEventTypeEnum,
    PomodoroStatusEnum
)
from app.core.security import get_current_user_id
from app.db.session import get_db
from app.db.models import PomodoroSession  # Modelo definido por el Dev de DB

router = APIRouter(prefix="/pomodoro", tags=["Pomodoro Sync (v2)"])

@router.post(
    "/start",
    response_model=PomodoroSessionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Iniciar una nueva sesión Pomodoro"
)
def start_pomodoro_session(
    payload: PomodoroStartRequest,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Crea un registro de sesión Pomodoro en MySQL asociado al usuario autenticado.
    """
    new_session = PomodoroSession(
        id=str(uuid.uuid4()),
        user_id=current_user_id,
        work_duration_minutes=payload.work_duration_minutes,
        break_duration_minutes=payload.break_duration_minutes,
        completed_cycles=0,
        status=PomodoroStatusEnum.RUNNING,
        started_at=datetime.now(timezone.utc)
    )
    
    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    
    return new_session

@router.post(
    "/event",
    response_model=PomodoroAudioActionResponse,
    summary="Sincronizar eventos del reloj y controlar el reproductor de audio"
)
def process_pomodoro_event(
    payload: PomodoroEventRequest,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Recibe los eventos del temporizador móvil y devuelve comandos de acción para el audio:
    - PAUSE -> Pausa el reproductor de audio.
    - RESUME -> Reanuda el reproductor de audio.
    - COMPLETE_CYCLE -> Pausa música de estudio e inicia tono/sonido de descanso.
    - FINISH/CANCEL -> Detiene totalmente la reproducción.
    """
    session = db.query(PomodoroSession).filter(
        PomodoroSession.id == payload.session_id,
        PomodoroSession.user_id == current_user_id
    ).first()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sesión Pomodoro no encontrada para este usuario."
        )

    audio_action = "CONTINUE"
    message = "Evento procesado correctamente."

    # Lógica de estados y control de audio
    if payload.event_type == PomodoroEventTypeEnum.PAUSE:
        session.status = PomodoroStatusEnum.PAUSED
        audio_action = "PAUSE_AUDIO"
        message = "Reloj pausado. Pausando reproducción de audio."

    elif payload.event_type == PomodoroEventTypeEnum.RESUME:
        session.status = PomodoroStatusEnum.RUNNING
        audio_action = "RESUME_AUDIO"
        message = "Reloj reanudado. Reanudando reproducción de audio."

    elif payload.event_type == PomodoroEventTypeEnum.COMPLETE_CYCLE:
        session.completed_cycles += 1
        audio_action = "PLAY_BREAK_SOUND"
        message = f"¡Ciclo {session.completed_cycles} completado! Deteniendo música de enfoque e iniciando tiempo de descanso."

    elif payload.event_type == PomodoroEventTypeEnum.FINISH:
        session.status = PomodoroStatusEnum.COMPLETED
        session.ended_at = datetime.now(timezone.utc)
        audio_action = "STOP_AUDIO"
        message = "Sesión Pomodoro finalizada exitosamente."

    elif payload.event_type == PomodoroEventTypeEnum.CANCEL:
        session.status = PomodoroStatusEnum.CANCELLED
        session.ended_at = datetime.now(timezone.utc)
        audio_action = "STOP_AUDIO"
        message = "Sesión Pomodoro cancelada."

    db.commit()
    db.refresh(session)

    return {
        "session_id": session.id,
        "current_status": session.status,
        "completed_cycles": session.completed_cycles,
        "audio_action": audio_action,
        "message": message
    }

@router.get(
    "/active",
    response_model=Optional[PomodoroSessionResponse],
    summary="Obtener sesión Pomodoro activa del usuario"
)
def get_active_session(
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Permite a la app móvil recuperar el estado si la aplicación fue cerrada o enviada a segundo plano.
    """
    session = db.query(PomodoroSession).filter(
        PomodoroSession.user_id == current_user_id,
        PomodoroSession.status.in_([PomodoroStatusEnum.RUNNING, PomodoroStatusEnum.PAUSED])
    ).first()
    
    return session