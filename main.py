from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException, Query, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import selectinload
import aiofiles

from database import create_db_and_tables, get_session
from models import Usuario, UsuarioCreate, Audio, AudioCreate, SesionEstudio, calcular_rango

app = FastAPI(title="API Sonidos de Concentración")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.on_event("startup")
async def on_startup():
    await create_db_and_tables()

@app.get("/")
async def inicio():
    return {"mensaje": "API Sonidos de Concentración activa"}


# --- GESTIÓN DE USUARIOS ---

@app.post("/usuarios", response_model=Usuario)
async def crear_usuario(usuario: UsuarioCreate, session: AsyncSession = Depends(get_session)):
    db_usuario = Usuario.model_validate(usuario)
    session.add(db_usuario)
    await session.commit()
    await session.refresh(db_usuario)
    return db_usuario

@app.get("/usuarios/{usuario_id}", response_model=Usuario)
async def obtener_usuario(usuario_id: int, session: AsyncSession = Depends(get_session)):
    usuario = await session.get(Usuario, usuario_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return usuario


# --- CATÁLOGO Y REGISTRO DE AUDIOS ---

@app.get("/audios", response_model=List[Audio])
async def listar_audios(
    categoria: Optional[str] = Query(None, description="Filtrar por Lectura, Estudio Profundo, Relax"),
    tipo_sonido: Optional[str] = Query(None, description="Filtrar por Ruido Blanco, Binaural, Sonido Neutro"),
    session: AsyncSession = Depends(get_session)
):
    query = select(Audio)
    if categoria:
        query = query.where(Audio.categoria == categoria)
    if tipo_sonido:
        query = query.where(Audio.tipo_sonido == tipo_sonido)
        
    resultado = await session.exec(query)
    return resultado.all()

@app.post("/audios", response_model=Audio)
async def crear_audio(audio: AudioCreate, session: AsyncSession = Depends(get_session)):
    db_audio = Audio.model_validate(audio)
    session.add(db_audio)
    await session.commit()
    await session.refresh(db_audio)
    return db_audio

@app.post("/audios/subir-audio/")
async def subir_audio(file: UploadFile = File(...)):
    ruta_archivo = f"static/audio/{file.filename}"
    
    # Escritura asíncrona de archivos
    async with aiofiles.open(ruta_archivo, "wb") as buffer:
        contenido = await file.read()
        await buffer.write(contenido)
        
    url_publica = f"/static/audio/{file.filename}"
    return {"mensaje": "Archivo subido con éxito", "url_audio": url_publica}


# --- TEMPORIZADOR POMODORO Y SISTEMA DE PUNTOS ---

@app.post("/pomodoro/completar")
async def registrar_pomodoro(
    usuario_id: int, 
    minutos: int, 
    session: AsyncSession = Depends(get_session)
):
    usuario = await session.get(Usuario, usuario_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    puntos_ganados = minutos * 2
    usuario.puntos += puntos_ganados
    usuario.rango = calcular_rango(usuario.puntos)
    
    nueva_sesion = SesionEstudio(
        usuario_id=usuario_id, 
        minutos_estudiados=minutos, 
        puntos_obtenidos=puntos_ganados
    )
    
    session.add(usuario)
    session.add(nueva_sesion)
    await session.commit()
    await session.refresh(usuario)
    
    return {
        "mensaje": "Sesión registrada",
        "puntos_ganados": puntos_ganados,
        "total_puntos": usuario.puntos,
        "rango_actual": usuario.rango
    }


# --- DESBLOQUEO DE AUDIOS CON PUNTOS ---

@app.post("/audios/{audio_id}/desbloquear")
async def desbloquear_audio(
    audio_id: int, 
    usuario_id: int, 
    session: AsyncSession = Depends(get_session)
):
    # Carga explícita de relación para evitar bloqueos asíncronos (lazy loading)
    query_usuario = select(Usuario).where(Usuario.id == usuario_id).options(selectinload(Usuario.audios_desbloqueados))
    res_usuario = await session.exec(query_usuario)
    usuario = res_usuario.first()

    audio = await session.get(Audio, audio_id)
    
    if not usuario or not audio:
        raise HTTPException(status_code=404, detail="Usuario o Audio no encontrado")
    
    if audio in usuario.audios_desbloqueados:
        return {"mensaje": "El audio ya se encuentra desbloqueado"}
        
    if usuario.puntos < audio.puntos_requeridos:
        raise HTTPException(status_code=400, detail="Puntos insuficientes para desbloquear este audio")
        
    usuario.puntos -= audio.puntos_requeridos
    usuario.audios_desbloqueados.append(audio)
    
    session.add(usuario)
    await session.commit()
    
    return {"mensaje": "Audio desbloqueado con éxito", "puntos_restantes": usuario.puntos}