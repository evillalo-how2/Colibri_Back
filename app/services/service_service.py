import uuid
from typing import Any

from sqlalchemy.orm import Session

from app.core.exceptions import BadRequestError, NotFoundError
from app.models.service import (
    Currency,
    Service,
    ServiceModality,
    ServiceType,
    generate_slug,
    get_service_type_code_prefix,
)
from app.repositories.service_repository import ServiceRepository
from app.schemas.service import ServiceCreate, ServiceUpdate


class ServiceService:
    def __init__(self, db: Session):
        self.repository = ServiceRepository(db)

    def create_service(self, payload: ServiceCreate) -> Service:
        data = payload.model_dump()
        data = self._clean_payload_data(data)

        self._validate_service_rules(data)

        slug = self._generate_unique_slug(data["name"])
        catalog_code = self._generate_catalog_code(data["type"])

        service = Service(
            name=data["name"],
            slug=slug,
            catalog_code=catalog_code,
            short_description=data.get("short_description"),
            description=data.get("description"),
            type=data["type"],
            modality=data["modality"],
            price_cents=data["price_cents"],
            currency=data["currency"],
            duration_minutes=data.get("duration_minutes"),
            stock_quantity=data.get("stock_quantity"),
            is_stock_limited=data["is_stock_limited"],
            is_active=data["is_active"],
            is_public=data["is_public"],
            requires_appointment=data["requires_appointment"],
            display_order=data["display_order"],
            cover_image_url=data.get("cover_image_url"),
            metadata_=data.get("metadata"),
        )

        return self.repository.create(service)

    def list_services(
        self,
        *,
        search: str | None = None,
        service_type: ServiceType | None = None,
        modality: ServiceModality | None = None,
        is_active: bool | None = None,
        is_public: bool | None = None,
        requires_appointment: bool | None = None,
        page: int = 1,
        limit: int = 20,
    ) -> tuple[list[Service], int]:
        skip = (page - 1) * limit

        services = self.repository.list_services(
            search=search,
            service_type=service_type,
            modality=modality,
            is_active=is_active,
            is_public=is_public,
            requires_appointment=requires_appointment,
            skip=skip,
            limit=limit,
        )

        total = self.repository.count(
            search=search,
            service_type=service_type,
            modality=modality,
            is_active=is_active,
            is_public=is_public,
            requires_appointment=requires_appointment,
        )

        return services, total

    def get_service_by_id(self, service_id: uuid.UUID) -> Service:
        service = self.repository.get_by_id(service_id)

        if not service:
            raise NotFoundError("Service not found.")

        return service

    def update_service(
        self,
        *,
        service_id: uuid.UUID,
        payload: ServiceUpdate,
    ) -> Service:
        service = self.get_service_by_id(service_id)
        data = payload.model_dump(exclude_unset=True)
        data = self._clean_payload_data(data)

        final_data = self._build_final_data(
            service=service,
            patch_data=data,
        )

        self._validate_service_rules(final_data)

        if "name" in data and data["name"] != service.name:
            service.slug = self._generate_unique_slug(
                data["name"],
                current_service_id=service.id,
            )

        for field, value in data.items():
            if field == "metadata":
                service.metadata_ = value
                continue

            setattr(service, field, value)

        return self.repository.update(service)

    def activate_service(self, service_id: uuid.UUID) -> Service:
        service = self.get_service_by_id(service_id)
        service.is_active = True

        return self.repository.update(service)

    def deactivate_service(self, service_id: uuid.UUID) -> Service:
        service = self.get_service_by_id(service_id)
        service.is_active = False
        service.is_public = False

        return self.repository.update(service)

    def publish_service(self, service_id: uuid.UUID) -> Service:
        service = self.get_service_by_id(service_id)

        final_data = self._service_to_dict(service)
        final_data["is_public"] = True

        self._validate_service_rules(final_data)
        self._validate_public_service(final_data)

        service.is_public = True
        service.is_active = True

        return self.repository.update(service)

    def unpublish_service(self, service_id: uuid.UUID) -> Service:
        service = self.get_service_by_id(service_id)
        service.is_public = False

        return self.repository.update(service)

    def _generate_unique_slug(
        self,
        name: str,
        current_service_id: uuid.UUID | None = None,
    ) -> str:
        base_slug = generate_slug(name)
        slug = base_slug
        counter = 2

        while True:
            existing_service = self.repository.get_by_slug(slug)

            if not existing_service:
                return slug

            if current_service_id and existing_service.id == current_service_id:
                return slug

            slug = f"{base_slug}-{counter}"
            counter += 1

    def _generate_catalog_code(self, service_type: ServiceType) -> str:
        prefix = get_service_type_code_prefix(service_type)
        sequence = self.repository.count_all() + 1

        while True:
            catalog_code = f"PSI-{prefix}-{sequence:06d}"
            existing_service = self.repository.get_by_catalog_code(catalog_code)

            if not existing_service:
                return catalog_code

            sequence += 1

    def _clean_payload_data(self, data: dict[str, Any]) -> dict[str, Any]:
        cleaned_data: dict[str, Any] = {}

        for field, value in data.items():
            if isinstance(value, str):
                value = value.strip() or None

            cleaned_data[field] = value

        return cleaned_data

    def _build_final_data(
        self,
        *,
        service: Service,
        patch_data: dict[str, Any],
    ) -> dict[str, Any]:
        final_data = self._service_to_dict(service)
        final_data.update(patch_data)

        return final_data

    def _service_to_dict(self, service: Service) -> dict[str, Any]:
        return {
            "name": service.name,
            "slug": service.slug,
            "catalog_code": service.catalog_code,
            "short_description": service.short_description,
            "description": service.description,
            "type": service.type,
            "modality": service.modality,
            "price_cents": service.price_cents,
            "currency": service.currency,
            "duration_minutes": service.duration_minutes,
            "stock_quantity": service.stock_quantity,
            "is_stock_limited": service.is_stock_limited,
            "is_active": service.is_active,
            "is_public": service.is_public,
            "requires_appointment": service.requires_appointment,
            "display_order": service.display_order,
            "cover_image_url": service.cover_image_url,
            "metadata": service.metadata_,
        }

    def _validate_service_rules(self, data: dict[str, Any]) -> None:
        name = data.get("name")

        if not name or not name.strip():
            raise BadRequestError("Service name is required.")

        if len(name.strip()) < 3:
            raise BadRequestError(
                "Service name must contain at least 3 characters."
            )

        price_cents = data.get("price_cents")

        if price_cents is None or price_cents < 0:
            raise BadRequestError("Price must be greater than or equal to 0.")

        currency = data.get("currency")

        if currency not in {Currency.MXN, Currency.USD}:
            raise BadRequestError("Invalid currency.")

        duration_minutes = data.get("duration_minutes")

        if duration_minutes is not None and not 5 <= duration_minutes <= 1440:
            raise BadRequestError(
                "Duration must be between 5 and 1440 minutes."
            )

        stock_quantity = data.get("stock_quantity")

        if stock_quantity is not None and stock_quantity < 0:
            raise BadRequestError("Stock quantity cannot be negative.")

        if data.get("is_stock_limited") and stock_quantity is None:
            raise BadRequestError(
                "Stock quantity is required when stock is limited."
            )

        if data.get("requires_appointment") and duration_minutes is None:
            raise BadRequestError(
                "Duration is required when the service requires an appointment."
            )

        service_type = data.get("type")

        if service_type == ServiceType.THERAPY:
            if not data.get("requires_appointment"):
                raise BadRequestError(
                    "Therapy services must require an appointment."
                )

            if duration_minutes is None:
                raise BadRequestError(
                    "Therapy services must have a duration."
                )

            if data.get("is_stock_limited") or stock_quantity is not None:
                raise BadRequestError(
                    "Therapy services must not use stock quantity."
                )

        if service_type in {
            ServiceType.DIGITAL_PRODUCT,
        }:
            if data.get("requires_appointment"):
                raise BadRequestError(
                    "Digital products must not require an appointment."
                )

            if duration_minutes is not None:
                raise BadRequestError(
                    "Digital products must not have duration."
                )

            if data.get("is_stock_limited") or stock_quantity is not None:
                raise BadRequestError(
                    "Digital products must not use stock quantity."
                )

        if service_type in {
            ServiceType.BOOK,
            ServiceType.PHYSICAL_PRODUCT,
        }:
            if data.get("requires_appointment"):
                raise BadRequestError(
                    "Books and physical products must not require an appointment."
                )

            if duration_minutes is not None:
                raise BadRequestError(
                    "Books and physical products must not have duration."
                )

        if service_type == ServiceType.COURSE:
            if duration_minutes is not None and duration_minutes < 30:
                raise BadRequestError(
                    "Courses must have a duration of at least 30 minutes."
                )

    def _validate_public_service(self, data: dict[str, Any]) -> None:
        required_public_fields = {
            "name": data.get("name"),
            "short_description": data.get("short_description"),
            "description": data.get("description"),
        }

        missing_fields = [
            field
            for field, value in required_public_fields.items()
            if not value
        ]

        if missing_fields:
            raise BadRequestError(
                "Service cannot be published because required public "
                "information is missing."
            )

        if not data.get("is_active"):
            raise BadRequestError("Inactive services cannot be published.")