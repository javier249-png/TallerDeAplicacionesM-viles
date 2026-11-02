from fastapi import APIRouter, Body, Depends, HTTPException, status
from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from db.database import get_db
from models.pomodoro import PomodoroSession
from models.pomodoro_orm import PomodoroSessionORM
from models.user_orm import User
from security.deps import get_current_active_user

router = APIRouter()


@router.post("/start", status_code=status.HTTP_201_CREATED)
async def start_pomodoro(
    session: PomodoroSession = Body(default=PomodoroSession()),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    duration_seconds = session.work_duration_minutes * 60
    await db.execute(
        select(User.id).where(User.id == current_user.id).with_for_update()
    )
    active_result = await db.execute(
        select(PomodoroSessionORM.id).where(
            PomodoroSessionORM.user_id == current_user.id,
            PomodoroSessionORM.xp_earned == -1,
        )
    )
    if active_result.scalar_one_or_none() is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe una sesión Pomodoro activa. Paúsala antes de iniciar otra.",
        )

    pomodoro_session = PomodoroSessionORM(
        user_id=current_user.id,
        duration_seconds=duration_seconds,
        xp_earned=-1,
    )
    db.add(pomodoro_session)
    await db.commit()
    await db.refresh(pomodoro_session)
    return {
        "message": "Inicio de sesión Pomodoro registrado.",
        "session_id": pomodoro_session.id,
        "duration_seconds": duration_seconds,
        "xp_earned": pomodoro_session.xp_earned,
    }


@router.post("/pause")
async def pause_pomodoro(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    user_result = await db.execute(
        select(User)
        .where(User.id == current_user.id)
        .with_for_update()
        .execution_options(populate_existing=True)
    )
    user = user_result.scalar_one()

    session_result = await db.execute(
        select(PomodoroSessionORM)
        .where(
            PomodoroSessionORM.user_id == user.id,
            PomodoroSessionORM.xp_earned == -1,
        )
        .order_by(PomodoroSessionORM.id.desc())
        .limit(1)
        .with_for_update()
    )
    pomodoro_session = session_result.scalar_one_or_none()
    if pomodoro_session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No hay una sesión Pomodoro activa",
        )

    elapsed_result = await db.execute(
        select(
            func.timestampdiff(
                text("SECOND"),
                PomodoroSessionORM.created_at,
                func.current_timestamp(),
            )
        ).where(PomodoroSessionORM.id == pomodoro_session.id)
    )
    elapsed_seconds = elapsed_result.scalar_one()
    elapsed_seconds = min(
        pomodoro_session.duration_seconds,
        max(0, elapsed_seconds),
    )
    xp_earned = (elapsed_seconds // 60) * 10

    pomodoro_session.duration_seconds = elapsed_seconds
    pomodoro_session.xp_earned = xp_earned
    user.xp += xp_earned
    user.level = (user.xp // 200) + 1
    await db.commit()

    return {
        "message": "Sesión Pomodoro finalizada.",
        "session_id": pomodoro_session.id,
        "duration_seconds": elapsed_seconds,
        "xp_earned": xp_earned,
        "total_xp": user.xp,
        "current_level": user.level,
    }


@router.post("/resume")
async def resume_pomodoro(
    current_user: User = Depends(get_current_active_user),
):
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail=(
            "La tabla pomodoro_sessions no guarda el estado ni el tiempo restante. "
            "Se necesita almacenamiento adicional para reanudar sesiones."
        ),
    )