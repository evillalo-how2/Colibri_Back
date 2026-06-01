import uuid
from datetime import date, datetime, timezone
from enum import StrEnum

from sqlalchemy import Date, DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base


class EmploymentType(StrEnum):
    EMPLOYEE = "employee"
    CONTRACTOR = "contractor"
    EXTERNAL = "external"
    INTERN = "intern"


class EmployeeProfile(Base):
    __tablename__ = "employee_profiles"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        index=True,
        nullable=False,
    )

    legal_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    preferred_name: Mapped[str | None] = mapped_column(
        String(255),
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

    phone: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True,
    )

    emergency_contact_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    emergency_contact_phone: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True,
    )

    address_line: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    neighborhood: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True,
    )

    city: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True,
    )

    state: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True,
    )

    zip_code: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )

    country: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        default="México",
    )

    job_title: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True,
    )

    department: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True,
    )

    employment_type: Mapped[EmploymentType | None] = mapped_column(
        Enum(EmploymentType, name="employment_type"),
        nullable=True,
    )

    hire_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    termination_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    work_schedule: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    curp: Mapped[str | None] = mapped_column(
        String(18),
        index=True,
        nullable=True,
    )

    rfc: Mapped[str | None] = mapped_column(
        String(13),
        index=True,
        nullable=True,
    )

    nss: Mapped[str | None] = mapped_column(
        String(15),
        index=True,
        nullable=True,
    )

    professional_license: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    ine_document_note: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    curp_document_note: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    rfc_document_note: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    nss_document_note: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    proof_of_address_note: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    professional_license_note: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    contract_document_note: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    documents_notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    user = relationship("User")