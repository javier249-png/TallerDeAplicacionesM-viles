import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import settings

# URL de conexión a MySQL obtenida de las variables de entorno / .env
# Formato: mysql+pymysql://usuario:contraseña@host:puerto/nombre_bd
DATABASE_URL = getattr(
    settings, 
    "DATABASE_URL", 
    f"mysql+pymysql://{os.getenv('DB_USER', 'app_user')}:{os.getenv('DB_PASSWORD', 'secret')}"
    f"@{os.getenv('DB_HOST', 'db')}:{os.getenv('DB_PORT', '3306')}/{os.getenv('DB_NAME', 'studyplay_db')}"
)

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True, # Verifica conexiones activas antes de ejecutar queries
    pool_recycle=3600   # Evita desconexiones automáticas de MySQL por inactividad
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependencia para inyectar la sesión de base de datos en las rutas de FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()