from sqlalchemy import URL, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import settings

def build_database_url() -> str | URL:
    if settings.DATABASE_URL:
        return settings.DATABASE_URL

    required_settings = {
        "DB_HOST": settings.DB_HOST,
        "DB_NAME": settings.DB_NAME,
        "DB_USER": settings.DB_USER,
        "DB_PASSWORD": settings.DB_PASSWORD,
    }
    missing_settings = [name for name, value in required_settings.items() if not value]
    if missing_settings:
        missing = ", ".join(missing_settings)
        raise ValueError(
            f"Database configuration is incomplete. Set DATABASE_URL or provide: {missing}."
        )

    return URL.create(
        "mysql+pymysql",
        username=settings.DB_USER,
        password=settings.DB_PASSWORD,
        host=settings.DB_HOST,
        port=settings.DB_PORT,
        database=settings.DB_NAME,
    )


DATABASE_URL = build_database_url()

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=3600,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()