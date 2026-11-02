from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text, func

from db.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column("hashed_password", String(255), nullable=False)
    name = Column(String(255), nullable=True)
    avatar_url = Column(Text, nullable=True)
    xp = Column(Integer, nullable=False, default=0)
    level = Column(Integer, nullable=False, default=1)
    accept_terms = Column(Boolean, nullable=False, default=False)
    data_processing_consent = Column(Boolean, nullable=False, default=False)
    consent_timestamp = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
