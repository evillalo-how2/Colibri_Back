import re
import unicodedata
import uuid
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any

from sqlalchemy import Boolean, DateTime, Enum, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import Base


class Currency(StrEnum):
    MXN = "MXN"
    USD = "USD"


class ServiceType(StrEnum):
    THERAPY = "therapy"
    WORKSHOP = "workshop"
    COURSE = "course"
    BOOK = "book"
    DIGITAL_PRODUCT = "digital_product"
    PHYSICAL_PRODUCT = "physical_product"
    ACTIVITY = "activity"
    EVENT = "event"
    RETREAT = "retreat"
    OTHER = "other"


class ServiceModality(StrEnum):
    ONLINE = "online"
    IN_PERSON = "in_person"
    HYBRID = "hybrid"
    DIGITAL = "digital"
    NOT_APPLICABLE = "not_applicable"
    UNSPECIFIED = "unspecified"


class Service(Base):
    __tablename__ = "services"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    name: Mapped[str] = mapped_column(
        String(120),
        nullable=False,
        index=True,
    )

    slug: Mapped[str] = mapped_column(
        String(160),
        unique=True,
        index=True,
        nullable=False,
    )
    
    catalog_code: Mapped[str] = mapped_column(
    String(32),
    unique=True,
    index=True,
    nullable=False,
    )

    short_description: Mapped[str | None] = mapped_column(
        String(240),
        nullable=True,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    type: Mapped[ServiceType] = mapped_column(
        Enum(ServiceType, name="service_type"),
        nullable=False,
        index=True,
    )

    modality: Mapped[ServiceModality] = mapped_column(
        Enum(ServiceModality, name="service_modality"),
        nullable=False,
        default=ServiceModality.UNSPECIFIED,
        index=True,
    )

    price_cents: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    currency: Mapped[Currency] = mapped_column(
        Enum(Currency, name="currency"),
        nullable=False,
        default=Currency.MXN,
        index=True,
    )

    duration_minutes: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    stock_quantity: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    is_stock_limited: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        index=True,
    )

    is_public: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        index=True,
    )

    requires_appointment: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        index=True,
    )

    display_order: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    cover_image_url: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True,
    )

    metadata_: Mapped[dict[str, Any] | None] = mapped_column(
        "metadata",
        JSONB,
        nullable=True,
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

SERVICE_TYPE_CODE_PREFIX = {
    ServiceType.THERAPY: "TER",
    ServiceType.WORKSHOP: "WKS",
    ServiceType.COURSE: "CUR",
    ServiceType.BOOK: "LIB",
    ServiceType.DIGITAL_PRODUCT: "DIG",
    ServiceType.PHYSICAL_PRODUCT: "PHY",
    ServiceType.ACTIVITY: "ACT",
    ServiceType.EVENT: "EVT",
    ServiceType.RETREAT: "RET",
    ServiceType.OTHER: "OTH",
}


def get_service_type_code_prefix(service_type: ServiceType) -> str:
    return SERVICE_TYPE_CODE_PREFIX[service_type]

def generate_slug(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    ascii_value = normalized.encode("ascii", "ignore").decode("ascii")
    lower_value = ascii_value.lower().strip()

    slug = re.sub(r"[^a-z0-9]+", "-", lower_value)
    slug = slug.strip("-")

    return slug or "service"