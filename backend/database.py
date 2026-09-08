import os
from dotenv import load_dotenv
from sqlmodel import SQLModel, create_engine, Session

# Cargar las variables del archivo .env
load_dotenv()

# Obtener la URL de conexión de Neon.tech desde el .env
DATABASE_URL = os.getenv("DATABASE_URL")

# Crear el motor de conexión apuntando a PostgreSQL en Neon
engine = create_engine(DATABASE_URL, echo=True)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session