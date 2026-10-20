from pydantic import BaseModel, Field

class PomodoroSession(BaseModel):
    work_duration_minutes: int = Field(25, ge=1, le=120)
    break_duration_minutes: int = Field(5, ge=1, le=30)
    auto_stop_audio: bool = True

class PomodoroStatusResponse(BaseModel):
    session_status: str
    player_action: str
    remaining_seconds: int