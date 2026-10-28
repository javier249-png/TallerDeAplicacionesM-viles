from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    accept_terms: bool
    data_processing_consent: bool
    consent_timestamp: Optional[datetime] = None  # Cumplimiento Ley N° 19.628

class UserLogin(BaseModel):
    email: EmailStr
    password: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class UserProfileUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    avatar_url: Optional[str] = Field(None, max_length=2048)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"