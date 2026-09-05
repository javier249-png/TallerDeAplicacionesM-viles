from typing import Optional, List
from sqlmodel import Field, SQLModel, Relationship

# Tabla intermedia para audios desbloqueados por usuario
class UsuarioAudioLink(SQLModel, table=True):
    usuario_id: Optional[int] = Field(default=None, foreign_key="usuario.id", primary_key=True)
    audio_id: Optional[int] = Field(default=None, foreign_key="audio.id", primary_key=True)

class Usuario(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str
    email: str
    puntos: int = 0
    rango: str = "Plata"  # Plata, Oro, Platino, Diamante
    
    audios_desbloqueados: List["Audio"] = Relationship(back_populates="usuarios", link_model=UsuarioAudioLink)

class Audio(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    titulo: str
    tipo_sonido: str  # Ej: Ruido Blanco, Binaural, Sonido Neutro
    categoria: str     # Ej: Lectura, Estudio Profundo, Relax
    duracion: str
    url_audio: str
    puntos_requeridos: int = 0  # 0 si es gratuito, >0 si requiere desbloqueo

    usuarios: List[Usuario] = Relationship(back_populates="audios_desbloqueados", link_model=UsuarioAudioLink)

class SesionEstudio(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    usuario_id: int = Field(foreign_key="usuario.id")
    minutos_estudiados: int
    puntos_obtenidos: int

def calcular_rango(puntos: int) -> str:
    if puntos >= 1000:
        return "Diamante"
    elif puntos >= 500:
        return "Platino"
    elif puntos >= 200:
        return "Oro"
    return "Plata"