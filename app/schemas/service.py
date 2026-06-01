import uuid
from datetime import datetime
from typing import Any
from urllib.parse import urlparse

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.service import Currency, ServiceModality, ServiceType


MAX_PRICE_CENTS = 99_999_999


class ServiceBase(BaseModel):
    name: str = Field(min_length=3, max_length=120)
    short_description: str | None = Field(default=None, max_length=240)
    description: str | None = Field(default=None, max_length=5000)

    type: ServiceType
    modality: ServiceModality = ServiceModality.UNSPECIFIED

    price_cents: int = Field(ge=0, le=MAX_PRICE_CENTS)
    currency: Currency = Currency.MXN

    duration_minutes: int | None = Field(default=None, ge=5, le=1440)

    stock_quantity: int | None = Field(default=None, ge=0)
    is_stock_limited: bool = False

    is_active: bool = True
    is_public: bool = False
    requires_appointment: bool = False

    display_order: int = Field(default=0, ge=0)
    cover_image_url: str | None = Field(default=None, max_length=1000)
    metadata: dict[str, Any] | None = None

    model_config = ConfigDict(extra="forbid")

    @field_validator(
        "name",
        "short_description",
        "description",
        "cover_image_url",
        mode="before",
    )
    @classmethod
    def clean_optional_strings(cls, value: Any) -> Any:
        if value is None:
            return None

        if isinstance(value, str):
            value = value.strip()
            return value or None

        return value

    @field_validator("cover_image_url")
    @classmethod
    def validate_cover_image_url(cls, value: str | None) -> str | None:
        if value is None:
            return None

        parsed_url = urlparse(value)

        if parsed_url.scheme not in {"http", "https"} or not parsed_url.netloc:
            raise ValueError("Cover image URL must be a valid URL.")

        return value


class ServiceCreate(ServiceBase):
    pass


class ServiceUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=3, max_length=120)
    short_description: str | None = Field(default=None, max_length=240)
    description: str | None = Field(default=None, max_length=5000)

    type: ServiceType | None = None
    modality: ServiceModality | None = None

    price_cents: int | None = Field(default=None, ge=0, le=MAX_PRICE_CENTS)
    currency: Currency | None = None

    duration_minutes: int | None = Field(default=None, ge=5, le=1440)

    stock_quantity: int | None = Field(default=None, ge=0)
    is_stock_limited: bool | None = None

    is_active: bool | None = None
    is_public: bool | None = None
    requires_appointment: bool | None = None

    display_order: int | None = Field(default=None, ge=0)
    cover_image_url: str | None = Field(default=None, max_length=1000)
    metadata: dict[str, Any] | None = None

    model_config = ConfigDict(extra="forbid")

    @field_validator(
        "name",
        "short_description",
        "description",
        "cover_image_url",
        mode="before",
    )
    @classmethod
    def clean_optional_strings(cls, value: Any) -> Any:
        if value is None:
            return None

        if isinstance(value, str):
            value = value.strip()
            return value or None

        return value

    @field_validator("cover_image_url")
    @classmethod
    def validate_cover_image_url(cls, value: str | None) -> str | None:
        if value is None:
            return None

        parsed_url = urlparse(value)

        if parsed_url.scheme not in {"http", "https"} or not parsed_url.netloc:
            raise ValueError("Cover image URL must be a valid URL.")

        return value


class ServiceResponse(BaseModel):
    id: uuid.UUID
    name: str
    slug: str
    catalog_code: str
    short_description: str | None
    description: str | None
    type: ServiceType
    modality: ServiceModality
    price_cents: int
    currency: Currency
    duration_minutes: int | None
    stock_quantity: int | None
    is_stock_limited: bool
    is_active: bool
    is_public: bool
    requires_appointment: bool
    display_order: int
    cover_image_url: str | None
    metadata: dict[str, Any] | None = Field(
        default=None,
        validation_alias="metadata_",
        serialization_alias="metadata",
    )
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )


class ServicesListResponse(BaseModel):
    items: list[ServiceResponse]
    total: int
    page: int
    limit: int