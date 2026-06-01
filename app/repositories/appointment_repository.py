import uuid
from datetime import datetime

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.sql.elements import ColumnElement

from app.models.appointment import (
    Appointment,
    AppointmentCreatedSource,
    AppointmentModality,
    AppointmentStatus,
)


BLOCKING_STATUSES = {
    AppointmentStatus.SCHEDULED,
    AppointmentStatus.CONFIRMED,
    AppointmentStatus.RESCHEDULED,
}


class AppointmentRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, appointment_id: uuid.UUID) -> Appointment | None:
        statement = (
            select(Appointment)
            .options(
                joinedload(Appointment.patient),
                joinedload(Appointment.service),
                joinedload(Appointment.created_by_user),
                joinedload(Appointment.assigned_to_user),
            )
            .where(Appointment.id == appointment_id)
        )

        return self.db.scalar(statement)

    def list_appointments(
        self,
        *,
        search: str | None = None,
        patient_id: uuid.UUID | None = None,
        service_id: uuid.UUID | None = None,
        status: AppointmentStatus | None = None,
        modality: AppointmentModality | None = None,
        created_source: AppointmentCreatedSource | None = None,
        created_by_user_id: uuid.UUID | None = None,
        assigned_to_user_id: uuid.UUID | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
        skip: int = 0,
        limit: int = 20,
    ) -> list[Appointment]:
        conditions = self._build_filters(
            search=search,
            patient_id=patient_id,
            service_id=service_id,
            status=status,
            modality=modality,
            created_source=created_source,
            created_by_user_id=created_by_user_id,
            assigned_to_user_id=assigned_to_user_id,
            date_from=date_from,
            date_to=date_to,
        )

        statement = select(Appointment).options(
            joinedload(Appointment.patient),
            joinedload(Appointment.service),
            joinedload(Appointment.created_by_user),
            joinedload(Appointment.assigned_to_user),
        )

        if conditions:
            statement = statement.where(*conditions)

        statement = (
            statement.order_by(Appointment.scheduled_start.asc())
            .offset(skip)
            .limit(limit)
        )

        return list(self.db.scalars(statement).all())

    def count(
        self,
        *,
        search: str | None = None,
        patient_id: uuid.UUID | None = None,
        service_id: uuid.UUID | None = None,
        status: AppointmentStatus | None = None,
        modality: AppointmentModality | None = None,
        created_source: AppointmentCreatedSource | None = None,
        created_by_user_id: uuid.UUID | None = None,
        assigned_to_user_id: uuid.UUID | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
    ) -> int:
        conditions = self._build_filters(
            search=search,
            patient_id=patient_id,
            service_id=service_id,
            status=status,
            modality=modality,
            created_source=created_source,
            created_by_user_id=created_by_user_id,
            assigned_to_user_id=assigned_to_user_id,
            date_from=date_from,
            date_to=date_to,
        )

        statement = select(func.count()).select_from(Appointment)

        if conditions:
            statement = statement.where(*conditions)

        return int(self.db.scalar(statement) or 0)

    def has_overlap(
        self,
        *,
        scheduled_start: datetime,
        scheduled_end: datetime,
        exclude_appointment_id: uuid.UUID | None = None,
    ) -> bool:
        statement = select(Appointment.id).where(
            Appointment.status.in_(BLOCKING_STATUSES),
            Appointment.scheduled_start < scheduled_end,
            Appointment.scheduled_end > scheduled_start,
        )

        if exclude_appointment_id:
            statement = statement.where(
                Appointment.id != exclude_appointment_id,
            )

        return self.db.scalar(statement) is not None

    def create(self, appointment: Appointment) -> Appointment:
        self.db.add(appointment)
        self.db.commit()
        self.db.refresh(appointment)

        return self.get_by_id(appointment.id) or appointment

    def update(self, appointment: Appointment) -> Appointment:
        self.db.commit()
        self.db.refresh(appointment)

        return self.get_by_id(appointment.id) or appointment

    def _build_filters(
        self,
        *,
        search: str | None = None,
        patient_id: uuid.UUID | None = None,
        service_id: uuid.UUID | None = None,
        status: AppointmentStatus | None = None,
        modality: AppointmentModality | None = None,
        created_source: AppointmentCreatedSource | None = None,
        created_by_user_id: uuid.UUID | None = None,
        assigned_to_user_id: uuid.UUID | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
    ) -> list[ColumnElement[bool]]:
        conditions: list[ColumnElement[bool]] = []

        if search:
            search_term = f"%{search.strip().lower()}%"
            conditions.append(
                or_(
                    func.lower(Appointment.notes).like(search_term),
                    func.lower(Appointment.location).like(search_term),
                    func.lower(Appointment.meeting_url).like(search_term),
                )
            )

        if patient_id:
            conditions.append(Appointment.patient_id == patient_id)

        if service_id:
            conditions.append(Appointment.service_id == service_id)

        if status:
            conditions.append(Appointment.status == status)

        if modality:
            conditions.append(Appointment.modality == modality)

        if created_source:
            conditions.append(Appointment.created_source == created_source)

        if created_by_user_id:
            conditions.append(
                Appointment.created_by_user_id == created_by_user_id,
            )

        if assigned_to_user_id:
            conditions.append(
                Appointment.assigned_to_user_id == assigned_to_user_id,
            )

        if date_from:
            conditions.append(Appointment.scheduled_start >= date_from)

        if date_to:
            conditions.append(Appointment.scheduled_start <= date_to)

        return conditions