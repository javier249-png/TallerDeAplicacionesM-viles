from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from secure import Secure

from config import settings
from routers import auth, audio, pomodoro, users

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

secure_headers = Secure()

@app.middleware("http")
async def set_security_headers(request: Request, call_next):
    response = await call_next(request)
    secure_headers.framework.fastapi(response)
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
    return {"status": "healthy", "service": "studyplay-api"}

app.include_router(auth.router, prefix="/api/v1/auth", tags=["Autenticación"])
app.include_router(audio.router, prefix="/api/v1/audio", tags=["Audio Funcional & Feed"])
app.include_router(pomodoro.router, prefix="/api/v1/pomodoro", tags=["Temporizador Pomodoro"])
app.include_router(users.router, prefix="/api/v1/users", tags=["Usuarios & Leyes Chile"])