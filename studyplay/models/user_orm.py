from sqlalchemy import Boolean, Column, DateTime, Integer, String, func

from db.database import Base


class UserORM(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(320), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(100), nullable=False, default="Estudiante StudyPlay")
    avatar_url = Column(String(2048), nullable=True)
    xp = Column(Integer, nullable=False, default=0)
    level = Column(Integer, nullable=False, default=1)
    accept_terms = Column(Boolean, nullable=False, default=False)
    data_processing_consent = Column(Boolean, nullable=False, default=False)
    consent_timestamp = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
