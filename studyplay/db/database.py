from collections.abc import AsyncIterator

from sqlalchemy import URL, make_url
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.ext.declarative import declarative_base

from config import settings


def build_database_url() -> URL:
    if settings.DATABASE_URL:
        database_url = make_url(settings.DATABASE_URL)
        if database_url.drivername in {"mysql", "mysql+pymysql"}:
            return database_url.set(drivername="mysql+aiomysql")
        if database_url.drivername == "sqlite":
            return database_url.set(drivername="sqlite+aiosqlite")
        return database_url

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
        "mysql+aiomysql",
        username=settings.DB_USER,
        password=settings.DB_PASSWORD,
        host=settings.DB_HOST,
        port=settings.DB_PORT,
        database=settings.DB_NAME,
    )


DATABASE_URL = build_database_url()

engine = create_async_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=3600,
)

SessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

Base = declarative_base()


async def get_db() -> AsyncIterator[AsyncSession]:
    async with SessionLocal() as db:
        yield db