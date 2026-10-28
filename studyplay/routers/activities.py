from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from db.database import get_db
from auth_utils import get_current_active_user

router = APIRouter()

@router.get("/", summary="Obtener actividades o tareas diarias del estudiante")
def get_user_activities(current_user = Depends(get_current_active_user), db: Session = Depends(get_db)):
    """
    Retorna el listado de lecciones o misiones diarias para la HomeScreen o ActivitiesScreen.
    """
    # Aquí puedes consultar la tabla 'activities' y el progreso del usuario
    # Simulación de respuesta estructurada para el front:
    return {
        "status": "success",
        "data": [
            {
                "id": 1,
                "title": "Completa 1 sesión de estudio Pomodoro",
                "description": "Estudia al menos 25 minutos sin interrupciones.",
                "xp_reward": 50,
                "is_completed": False
            },
            {
                "id": 2,
                "title": "Escucha un álbum Lo-Fi completo",
                "description": "Mantén la concentración utilizando la música ambiental.",
                "xp_reward": 30,
                "is_completed": True
            }
        ]
    }

@router.post("/{activity_id}/complete", summary="Marcar actividad como completada y sumar XP")
def complete_activity(activity_id: int, current_user = Depends(get_current_active_user), db: Session = Depends(get_db)):
    """
    Marca la tarea como completada, otorga los puntos correspondientes (+50 XP) 
    y actualiza el nivel del estudiante en su perfil.
    """
    # Ejemplo de lógica de negocio para sumar XP:
    reward_xp = 50
    
    # Sumar XP al usuario autenticado (asumiendo que tiene el atributo xp)
    current_user.xp = getattr(current_user, "xp", 0) + reward_xp
    
    # Lógica opcional para subir de nivel cada 200 XP
    current_user.level = (current_user.xp // 200) + 1
    
    db.commit()
    
    return {
        "status": "success",
        "message": "¡Actividad completada con éxito!",
        "data": {
            "activity_id": activity_id,
            "xp_earned": reward_xp,
            "total_xp": current_user.xp,
            "current_level": current_user.level
        }
    }