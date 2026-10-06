from typing import Optional, List
from sqlmodel import Field, SQLModel, Relationship

# --- TABLA INTERMEDIA (AUDIOS DESBLOQUEADOS) ---
class UsuarioAudioLink(SQLModel, table=True):
    usuario_id: Optional[int] = Field(default=None, foreign_key="usuario.id", primary_key=True)
    audio_id: Optional[int] = Field(default=None, foreign_key="audio.id", primary_key=True)


# --- MODELOS DE USUARIO ---
class UsuarioBase(SQLModel):
    nombre: str
    email: str

class Usuario(UsuarioBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    puntos: int = 0
    rango: str = "Plata"
    
    audios_desbloqueados: List["Audio"] = Relationship(back_populates="usuarios", link_model=UsuarioAudioLink)

class UsuarioCreate(UsuarioBase):
    pass


# --- MODELOS DE AUDIO ---
class AudioBase(SQLModel):
    titulo: str
    tipo_sonido: str  # Ej: Ruido Blanco, Binaural, Sonido Neutro
    categoria: str     # Ej: Lectura, Estudio Profundo, Relax
    duracion: str
    url_audio: str
    puntos_requeridos: int = 0

class Audio(AudioBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    
    usuarios: List[Usuario] = Relationship(back_populates="audios_desbloqueados", link_model=UsuarioAudioLink)

class AudioCreate(AudioBase):
    pass


# --- MODELO DE SESIÓN DE ESTUDIO ---
class SesionEstudio(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    usuario_id: int = Field(foreign_key="usuario.id")
    minutos_estudiados: int
    puntos_obtenidos: int


# --- LÓGICA DE NEGOCIO / RANGOS ---
def calcular_rango(puntos: int) -> str:
    if puntos >= 1000:
        return "Diamante"
    elif puntos >= 500:
        return "Platino"
    elif puntos >= 200:
        return "Oro"
    return "Plata"