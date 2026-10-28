from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from secure import Secure

import logging
from sqlalchemy.exc import OperationalError
from sqlalchemy import text
from fastapi.responses import JSONResponse

from config import settings
from db.database import SessionLocal
from routers import auth, audio, pomodoro, users, activities

# Logger oficial para registrar errores internos en 1Panel/Docker
logger = logging.getLogger("uvicorn.error")

limiter = Limiter(key_func=get_remote_address, default_limits=["100/minute"])

app = FastAPI(
    title="StudyPlay API",
    description="API de música enfocada al rendimiento cognitivo y concentración",
    version="1.0.0",
    docs_url=None if settings.ENVIRONMENT == "production" else "/docs",
    redoc_url=None if settings.ENVIRONMENT == "production" else "/redoc"
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Manejador global de errores de Base de Datos (Seguridad OWASP: Oculta detalles al cliente, loguea internamente)
@app.exception_handler(OperationalError)
async def database_connection_error_handler(request: Request, exc: OperationalError):
    logger.error(f"[ERROR INTERNO DE BASE DE DATOS]: {repr(exc)}")
    return JSONResponse(
        status_code=503,
        content={
            "status": "error",
            "message": "Servicio temporalmente no disponible. Por favor, intente más tarde."
        }
    )

secure_headers = Secure()

@app.middleware("http")
async def set_security_headers(request: Request, call_next):
    response = await call_next(request)
    secure_headers.set_headers(response)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    return response

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

@app.get("/healthcheck", tags=["System"])
def healthcheck():
    db_status = "connected"
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
    except Exception as e:
        db_status = "disconnected"
        logger.error(f"[HEALTHCHECK ERROR]: No se pudo conectar a la base de datos -> {repr(e)}")
    
    status_code = 200 if db_status == "connected" else 503
    
    return JSONResponse(
        status_code=status_code,
        content={
            "status": "healthy" if db_status == "connected" else "degraded",
            "service": "studyplay-api",
            "database": db_status,
            "port": settings.PORT
        }
    )

app.include_router(auth.router, prefix="/api/v1/auth", tags=["Autenticación"])
app.include_router(audio.router, prefix="/api/v1/audio", tags=["Audio Funcional & Feed"])
app.include_router(pomodoro.router, prefix="/api/v1/pomodoro", tags=["Temporizador Pomodoro"])
app.include_router(users.router, prefix="/api/v1/users", tags=["Usuarios & Leyes Chile"])
app.include_router(activities.router, prefix="/api/v1/activities", tags=["Actividades & Gamificación"])