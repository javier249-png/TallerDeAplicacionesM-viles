import shutil
from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException, Query, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlmodel import Session, select

from database import create_db_and_tables, get_session
from models import Usuario, Audio, SesionEstudio, calcular_rango

app = FastAPI(title="API Sonidos de Concentración")

# Permite peticiones desde la aplicación móvil (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Servir archivos de audio e imágenes localmente
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

@app.get("/")
def inicio():
    return {"mensaje": "API Sonidos de Concentración activa"}

# --- CATÁLOGO DE MÚSICA Y FILTROS ---

@app.get("/audios", response_model=List[Audio])
def listar_audios(
    categoria: Optional[str] = Query(None, description="Filtrar por Lectura, Estudio, Relax"),
    tipo_sonido: Optional[str] = Query(None, description="Filtrar por Ruido Blanco, Binaural, Neutro"),
    session: Session = Depends(get_session)
):
    query = select(Audio)
    if categoria:
        query = query.where(Audio.categoria == categoria)
    if tipo_sonido:
        query = query.where(Audio.tipo_sonido == tipo_sonido)
    return session.exec(query).all()

@app.post("/audios/subir-audio/")
def subir_audio(file: UploadFile = File(...)):
    ruta_archivo = f"static/audio/{file.filename}"
    with open(ruta_archivo, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    url_publica = f"http://127.0.0.1:8000/static/audio/{file.filename}"
    return {"mensaje": "Archivo subido con éxito", "url_audio": url_publica}

# --- POMODORO Y PUNTOS ---

@app.post("/pomodoro/completar")
def registrar_pomodoro(
    usuario_id: int, 
    minutos: int, 
    session: Session = Depends(get_session)
):
    usuario = session.get(Usuario, usuario_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    # Regla: 1 minuto de estudio = 2 puntos
    puntos_ganados = minutos * 2
    usuario.puntos += puntos_ganados
    usuario.rango = calcular_rango(usuario.puntos)
    
    nueva_sesion = SesionEstudio(usuario_id=usuario_id, minutos_estudiados=minutos, puntos_obtenidos=puntos_ganados)
    
    session.add(usuario)
    session.add(nueva_sesion)
    session.commit()
    session.refresh(usuario)
    
    return {
        "mensaje": "Sesión registrada",
        "puntos_ganados": puntos_ganados,
        "total_puntos": usuario.puntos,
        "rango_actual": usuario.rango
    }

# --- DESBLOQUEO DE MÚSICA ---

@app.post("/audios/{audio_id}/desbloquear")
def desbloquear_audio(
    audio_id: int, 
    usuario_id: int, 
    session: Session = Depends(get_session)
):
    usuario = session.get(Usuario, usuario_id)
    audio = session.get(Audio, audio_id)
    
    if not usuario or not audio:
        raise HTTPException(status_code=404, detail="Usuario o Audio no encontrado")
    
    if audio in usuario.audios_desbloqueados:
        return {"mensaje": "El audio ya está desbloqueado"}
        
    if usuario.puntos < audio.puntos_requeridos:
        raise HTTPException(status_code=400, detail="Puntos insuficientes")
        
    usuario.puntos -= audio.puntos_requeridos
    usuario.audios_desbloqueados.append(audio)
    
    session.add(usuario)
    session.commit()
    
    return {"mensaje": "Audio desbloqueado con éxito", "puntos_restantes": usuario.puntos}