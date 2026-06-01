import uuid

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session
from sqlalchemy.sql.elements import ColumnElement

from app.models.service import Service, ServiceModality, ServiceType


class ServiceRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, service_id: uuid.UUID) -> Service | None:
        statement = select(Service).where(Service.id == service_id)
        return self.db.scalar(statement)

    def get_by_slug(self, slug: str) -> Service | None:
        statement = select(Service).where(Service.slug == slug)
        return self.db.scalar(statement)

    def get_by_catalog_code(self, catalog_code: str) -> Service | None:
        statement = select(Service).where(Service.catalog_code == catalog_code)
        return self.db.scalar(statement)

    def list_services(
        self,
        *,
        search: str | None = None,
        service_type: ServiceType | None = None,
        modality: ServiceModality | None = None,
        is_active: bool | None = None,
        is_public: bool | None = None,
        requires_appointment: bool | None = None,
        skip: int = 0,
        limit: int = 20,
    ) -> list[Service]:
        conditions = self._build_filters(
            search=search,
            service_type=service_type,
            modality=modality,
            is_active=is_active,
            is_public=is_public,
            requires_appointment=requires_appointment,
        )

        statement = select(Service)

        if conditions:
            statement = statement.where(*conditions)

        statement = (
            statement.order_by(
                Service.display_order.asc(),
                Service.created_at.desc(),
            )
            .offset(skip)
            .limit(limit)
        )

        return list(self.db.scalars(statement).all())

    def count(
        self,
        *,
        search: str | None = None,
        service_type: ServiceType | None = None,
        modality: ServiceModality | None = None,
        is_active: bool | None = None,
        is_public: bool | None = None,
        requires_appointment: bool | None = None,
    ) -> int:
        conditions = self._build_filters(
            search=search,
            service_type=service_type,
            modality=modality,
            is_active=is_active,
            is_public=is_public,
            requires_appointment=requires_appointment,
        )

        statement = select(func.count()).select_from(Service)

        if conditions:
            statement = statement.where(*conditions)

        return int(self.db.scalar(statement) or 0)

    def count_all(self) -> int:
        statement = select(func.count()).select_from(Service)
        return int(self.db.scalar(statement) or 0)

    def create(self, service: Service) -> Service:
        self.db.add(service)
        self.db.commit()
        self.db.refresh(service)

        return service

    def update(self, service: Service) -> Service:
        self.db.commit()
        self.db.refresh(service)

        return service

    def _build_filters(
        self,
        *,
        search: str | None = None,
        service_type: ServiceType | None = None,
        modality: ServiceModality | None = None,
        is_active: bool | None = None,
        is_public: bool | None = None,
        requires_appointment: bool | None = None,
    ) -> list[ColumnElement[bool]]:
        conditions: list[ColumnElement[bool]] = []

        if search:
            search_term = f"%{search.strip().lower()}%"
            conditions.append(
                or_(
                    func.lower(Service.catalog_code).like(search_term),
                    func.lower(Service.name).like(search_term),
                    func.lower(Service.slug).like(search_term),
                    func.lower(Service.short_description).like(search_term),
                    func.lower(Service.description).like(search_term),
                )
            )

        if service_type:
            conditions.append(Service.type == service_type)

        if modality:
            conditions.append(Service.modality == modality)

        if is_active is not None:
            conditions.append(Service.is_active.is_(is_active))

        if is_public is not None:
            conditions.append(Service.is_public.is_(is_public))

        if requires_appointment is not None:
            conditions.append(
                Service.requires_appointment.is_(requires_appointment)
            )

        return conditions