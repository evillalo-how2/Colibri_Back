import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.patient import PatientGender, PatientModality, PatientStatus


class PatientBase(BaseModel):
    full_name: str = Field(min_length=2, max_length=255)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, max_length=30)

    birth_date: date | None = None
    gender: PatientGender | None = None

    preferred_modality: PatientModality = PatientModality.UNSPECIFIED

    source: str | None = Field(default=None, max_length=100)
    initial_reason: str | None = None
    internal_notes: str | None = None


class PatientCreate(PatientBase):
    pass


class PatientUpdate(BaseModel):
    full_name: str | None = Field(default=None, min_length=2, max_length=255)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, max_length=30)

    birth_date: date | None = None
    gender: PatientGender | None = None

    preferred_modality: PatientModality | None = None

    source: str | None = Field(default=None, max_length=100)
    initial_reason: str | None = None
    internal_notes: str | None = None


class PatientStatusUpdate(BaseModel):
    status: PatientStatus
    status_note: str = Field(min_length=3, max_length=1000)


class PatientResponse(BaseModel):
    id: uuid.UUID
    full_name: str
    email: EmailStr | None
    phone: str | None
    birth_date: date | None
    gender: PatientGender | None
    preferred_modality: PatientModality
    status: PatientStatus
    status_note: str | None
    source: str | None
    initial_reason: str | None
    internal_notes: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PatientsListResponse(BaseModel):
    items: list[PatientResponse]
    total: int
    page: int
    limit: int