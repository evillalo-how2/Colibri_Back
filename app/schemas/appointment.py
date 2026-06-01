import uuid
from datetime import datetime
from urllib.parse import urlparse

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.appointment import (
    AppointmentCreatedSource,
    AppointmentModality,
    AppointmentStatus,
)
from app.models.user import UserType
from app.models.service import Currency


DEFAULT_TIMEZONE = "America/Mexico_City"


class AppointmentPatientSummary(BaseModel):
    id: uuid.UUID
    full_name: str
    email: str | None
    phone: str | None

    model_config = ConfigDict(from_attributes=True)

class AppointmentServiceSummary(BaseModel):
    id: uuid.UUID
    name: str
    catalog_code: str
    duration_minutes: int | None
    price_cents: int
    currency: Currency

    model_config = ConfigDict(from_attributes=True)
    
class AppointmentUserSummary(BaseModel):
    id: uuid.UUID
    full_name: str
    email: str
    user_type: UserType

    model_config = ConfigDict(from_attributes=True)


class AppointmentCreate(BaseModel):
    patient_id: uuid.UUID
    service_id: uuid.UUID
    assigned_to_user_id: uuid.UUID | None = None
    scheduled_start: datetime
    timezone: str = Field(default=DEFAULT_TIMEZONE, max_length=100)
    modality: AppointmentModality = AppointmentModality.UNSPECIFIED
    location: str | None = Field(default=None, max_length=255)
    meeting_url: str | None = Field(default=None, max_length=1000)
    notes: str | None = Field(default=None, max_length=2000)

    model_config = ConfigDict(extra="forbid")

    @field_validator("location", "meeting_url", "notes", mode="before")
    @classmethod
    def clean_optional_strings(cls, value):
        if value is None:
            return None

        if isinstance(value, str):
            value = value.strip()
            return value or None

        return value

    @field_validator("meeting_url")
    @classmethod
    def validate_meeting_url(cls, value: str | None) -> str | None:
        if value is None:
            return None

        parsed_url = urlparse(value)

        if parsed_url.scheme not in {"http", "https"} or not parsed_url.netloc:
            raise ValueError("Meeting URL must be a valid URL.")

        return value


class AppointmentUpdate(BaseModel):
    patient_id: uuid.UUID | None = None
    service_id: uuid.UUID | None = None
    assigned_to_user_id: uuid.UUID | None = None
    scheduled_start: datetime | None = None
    timezone: str | None = Field(default=None, max_length=100)
    modality: AppointmentModality | None = None
    location: str | None = Field(default=None, max_length=255)
    meeting_url: str | None = Field(default=None, max_length=1000)
    notes: str | None = Field(default=None, max_length=2000)

    model_config = ConfigDict(extra="forbid")

    @field_validator("location", "meeting_url", "notes", "timezone", mode="before")
    @classmethod
    def clean_optional_strings(cls, value):
        if value is None:
            return None

        if isinstance(value, str):
            value = value.strip()
            return value or None

        return value

    @field_validator("meeting_url")
    @classmethod
    def validate_meeting_url(cls, value: str | None) -> str | None:
        if value is None:
            return None

        parsed_url = urlparse(value)

        if parsed_url.scheme not in {"http", "https"} or not parsed_url.netloc:
            raise ValueError("Meeting URL must be a valid URL.")

        return value


class AppointmentCancelRequest(BaseModel):
    cancellation_reason: str = Field(min_length=3, max_length=1000)

    model_config = ConfigDict(extra="forbid")


class AppointmentNoShowRequest(BaseModel):
    notes: str | None = Field(default=None, max_length=2000)

    model_config = ConfigDict(extra="forbid")


class AppointmentRescheduleRequest(BaseModel):
    scheduled_start: datetime
    reschedule_reason: str = Field(min_length=3, max_length=1000)

    model_config = ConfigDict(extra="forbid")


class AppointmentResponse(BaseModel):
    id: uuid.UUID

    patient_id: uuid.UUID
    patient: AppointmentPatientSummary

    service_id: uuid.UUID
    service: AppointmentServiceSummary

    created_source: AppointmentCreatedSource

    created_by_user_id: uuid.UUID | None
    created_by_user: AppointmentUserSummary | None

    assigned_to_user_id: uuid.UUID | None
    assigned_to_user: AppointmentUserSummary | None

    scheduled_start: datetime
    scheduled_end: datetime
    timezone: str
    status: AppointmentStatus
    modality: AppointmentModality
    location: str | None
    meeting_url: str | None
    notes: str | None
    cancellation_reason: str | None
    reschedule_reason: str | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AppointmentsListResponse(BaseModel):
    items: list[AppointmentResponse]
    total: int
    page: int
    limit: int