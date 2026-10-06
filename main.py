# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v2.auth import router as auth_router
from app.api.v2.pomodoro import router as pomodoro_router
from app.api.v2.users import router as users_router
from app.api.v2.feed import router as feed_router
from app.api.v2.tracks import router as tracks_router

app = FastAPI(
    title="Study Music Cognitive API",
    version="2.0.0",
    docs_url="/docs",
    redoc_url=None
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Inclusión de Routers v2
app.include_router(auth_router, prefix="/api/v2")
app.include_router(pomodoro_router, prefix="/api/v2")
app.include_router(users_router, prefix="/api/v2")
app.include_router(feed_router, prefix="/api/v2")
app.include_router(tracks_router, prefix="/api/v2")

@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok", "version": "v2"}