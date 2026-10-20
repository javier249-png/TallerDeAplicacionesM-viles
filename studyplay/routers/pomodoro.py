from fastapi import APIRouter, Depends
from models.pomodoro import PomodoroSession, PomodoroStatusResponse
from security.deps import get_current_user

router = APIRouter()

@router.post("/start", response_model=PomodoroStatusResponse)
def start_pomodoro(session: PomodoroSession, current_user: str = Depends(get_current_user)):
    return {
        "session_status": "running",
        "player_action": "play",
        "remaining_seconds": session.work_duration_minutes * 60
    }

@router.post("/pause", response_model=PomodoroStatusResponse)
def pause_pomodoro(current_user: str = Depends(get_current_user)):
    return {
        "session_status": "paused",
        "player_action": "pause",
        "remaining_seconds": 0
    }