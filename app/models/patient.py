import uuid
from datetime import date, datetime, timezone
from enum import StrEnum

from sqlalchemy import Boolean, Date, DateTime, Enum, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import Base


class PatientStatus(StrEnum):
    NEW = "new"
    CONTACTED = "contacted"
    ACTIVE = "active"
    FOLLOW_UP = "follow_up"
    INACTIVE = "inactive"
    
class PatientGender(StrEnum):
    MALE = "male"
    FEMALE = "female"
    NON_BINARY = "non_binary"


class PatientModality(StrEnum):
    ONLINE = "online"
    IN_PERSON = "in_person"
    HYBRID = "hybrid"
    UNSPECIFIED = "unspecified"


class Patient(Base):
    __tablename__ = "patients"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    full_name: Mapped[str] = mapped_column(
        String(255),
        index=True,
        nullable=False,
    )

    email: Mapped[str | None] = mapped_column(
        String(255),
        index=True,
        nullable=True,
    )

    phone: Mapped[str | None] = mapped_column(
        String(30),
        index=True,
        nullable=True,
    )

    birth_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    gender: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    preferred_modality: Mapped[PatientModality] = mapped_column(
        Enum(PatientModality, name="patient_modality"),
        nullable=False,
        default=PatientModality.UNSPECIFIED,
        index=True,
    )

    status: Mapped[PatientStatus] = mapped_column(
        Enum(PatientStatus, name="patient_status"),
        nullable=False,
        default=PatientStatus.NEW,
        index=True,
    )
    
    status_note: Mapped[str | None] = mapped_column(
    Text,
    nullable=True,
    
    )
    

    source: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    initial_reason: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    internal_notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        index=True,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )