from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional

class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    accept_terms: bool
    data_processing_consent: bool
    consent_timestamp: Optional[datetime] = None  # Marca de tiempo para cumplimiento de Ley N° 19.628