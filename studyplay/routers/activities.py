from datetime import datetime
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from db.database import get_db
from models.activity import ActivityCompletionORM
from models.user_orm import UserORM
from security.deps import get_current_active_user

router = APIRouter()

CHILE_TIMEZONE = ZoneInfo("America/Santiago")

ACTIVITIES = {
    1: {
        "title": "Completa 1 sesión de estudio Pomodoro",
        "description": "Estudia al menos 25 minutos sin interrupciones.",
        "xp_reward": 50,
    },
    2: {
        "title": "Escucha un álbum Lo-Fi completo",
        "description": "Mantén la concentración utilizando la música ambiental.",
        "xp_reward": 30,
    },
}


@router.get("/", summary="Obtener actividades o tareas diarias del estudiante")
async def get_user_activities(
    current_user: UserORM = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    today = datetime.now(CHILE_TIMEZONE).date()
    result = await db.execute(
        select(ActivityCompletionORM.activity_id).where(
            ActivityCompletionORM.user_id == current_user.id,
            ActivityCompletionORM.completion_date == today,
        )
    )
    completed_activity_ids = set(result.scalars().all())

    return {
        "status": "success",
        "data": [
            {"id": activity_id, **activity, "is_completed": activity_id in completed_activity_ids}
            for activity_id, activity in ACTIVITIES.items()
        ]
    }


@router.post("/{activity_id}/complete", summary="Marcar actividad como completada y sumar XP")
async def complete_activity(
    activity_id: int,
    current_user: UserORM = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    activity = ACTIVITIES.get(activity_id)
    if activity is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Actividad no encontrada",
        )

    reward_xp = activity["xp_reward"]
    user_id = current_user.id
    today = datetime.now(CHILE_TIMEZONE).date()
    db.add(
        ActivityCompletionORM(
            user_id=user_id,
            activity_id=activity_id,
            completion_date=today,
        )
    )
    current_user.xp += reward_xp
    current_user.level = (current_user.xp // 200) + 1
    try:
        await db.commit()
    except IntegrityError as exc:
        await db.rollback()
        result = await db.execute(
            select(ActivityCompletionORM).where(
                ActivityCompletionORM.user_id == user_id,
                ActivityCompletionORM.activity_id == activity_id,
                ActivityCompletionORM.completion_date == today,
            )
        )
        if result.scalar_one_or_none() is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="La actividad ya fue completada",
            ) from None
        raise exc

    return {
        "status": "success",
        "message": "¡Actividad completada con éxito!",
        "data": {
            "activity_id": activity_id,
            "xp_earned": reward_xp,
            "total_xp": current_user.xp,
            "current_level": current_user.level,
        },
    }