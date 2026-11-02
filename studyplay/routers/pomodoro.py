import time

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.database import get_db
from models.pomodoro import PomodoroSession, PomodoroStatusResponse
from models.pomodoro_orm import PomodoroTimerORM
from models.user_orm import UserORM
from security.deps import get_current_active_user

router = APIRouter()


@router.post("/start", response_model=PomodoroStatusResponse)
async def start_pomodoro(
    session: PomodoroSession,
    current_user: UserORM = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(PomodoroTimerORM).where(PomodoroTimerORM.user_id == current_user.id)
    )
    timer = result.scalar_one_or_none()
    remaining_seconds = session.work_duration_minutes * 60

    if timer is None:
        timer = PomodoroTimerORM(
            user_id=current_user.id,
            session_status="running",
            remaining_seconds=remaining_seconds,
            started_at_epoch=int(time.time()),
        )
        db.add(timer)
    else:
        timer.session_status = "running"
        timer.remaining_seconds = remaining_seconds
        timer.started_at_epoch = int(time.time())

    await db.commit()
    return {
        "session_status": "running",
        "player_action": "play",
        "remaining_seconds": remaining_seconds,
    }


@router.post("/pause", response_model=PomodoroStatusResponse)
async def pause_pomodoro(
    current_user: UserORM = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(PomodoroTimerORM).where(PomodoroTimerORM.user_id == current_user.id)
    )
    timer = result.scalar_one_or_none()
    if timer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No hay una sesión Pomodoro activa",
        )

    if timer.session_status == "running":
        started_at = timer.started_at_epoch
        if started_at is not None:
            timer.remaining_seconds = max(
                0, timer.remaining_seconds - (int(time.time()) - started_at)
            )
        timer.started_at_epoch = None
        timer.session_status = "paused" if timer.remaining_seconds else "completed"
        await db.commit()

    return {
        "session_status": timer.session_status,
        "player_action": "pause",
        "remaining_seconds": timer.remaining_seconds,
    }


@router.post("/resume", response_model=PomodoroStatusResponse)
async def resume_pomodoro(
    current_user: UserORM = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(PomodoroTimerORM).where(PomodoroTimerORM.user_id == current_user.id)
    )
    timer = result.scalar_one_or_none()
    if timer is None or timer.session_status != "paused":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No hay una sesión Pomodoro pausada para reanudar",
        )

    if timer.remaining_seconds == 0:
        timer.session_status = "completed"
        await db.commit()
        return {
            "session_status": "completed",
            "player_action": "pause",
            "remaining_seconds": 0,
        }

    timer.session_status = "running"
    timer.started_at_epoch = int(time.time())
    await db.commit()
    return {
        "session_status": "running",
        "player_action": "play",
        "remaining_seconds": timer.remaining_seconds,
    }