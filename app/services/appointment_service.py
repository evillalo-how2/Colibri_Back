import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.core.exceptions import BadRequestError, NotFoundError
from app.models.appointment import (
    Appointment,
    AppointmentCreatedSource,
    AppointmentModality,
    AppointmentStatus,
)
from app.models.service import ServiceModality
from app.models.user import User, UserType
from app.repositories.appointment_repository import AppointmentRepository
from app.repositories.patient_repository import PatientRepository
from app.repositories.service_repository import ServiceRepository
from app.repositories.user_repository import UserRepository
from app.schemas.appointment import (
    AppointmentCancelRequest,
    AppointmentCreate,
    AppointmentNoShowRequest,
    AppointmentRescheduleRequest,
    AppointmentUpdate,
)


DEFAULT_TIMEZONE = "America/Mexico_City"


class AppointmentService:
    def __init__(self, db: Session):
        self.repository = AppointmentRepository(db)
        self.patient_repository = PatientRepository(db)
        self.service_repository = ServiceRepository(db)
        self.user_repository = UserRepository(db)

    def create_appointment(
        self,
        *,
        payload: AppointmentCreate,
        current_user: User,
    ) -> Appointment:
        patient = self._get_active_patient(payload.patient_id)
        service = self._get_schedulable_service(payload.service_id)

        assigned_to_user = self._resolve_assigned_user(
            assigned_to_user_id=payload.assigned_to_user_id,
            current_user=current_user,
        )

        scheduled_start = self._normalize_datetime(payload.scheduled_start)
        self._validate_not_past(scheduled_start)

        scheduled_end = self._calculate_scheduled_end(
            scheduled_start=scheduled_start,
            duration_minutes=service.duration_minutes,
        )

        self._validate_no_overlap(
            scheduled_start=scheduled_start,
            scheduled_end=scheduled_end,
        )

        appointment = Appointment(
            patient_id=patient.id,
            service_id=service.id,
            created_source=AppointmentCreatedSource.STAFF,
            created_by_user_id=current_user.id,
            assigned_to_user_id=(
                assigned_to_user.id if assigned_to_user else None
            ),
            scheduled_start=scheduled_start,
            scheduled_end=scheduled_end,
            timezone=payload.timezone or DEFAULT_TIMEZONE,
            status=AppointmentStatus.SCHEDULED,
            modality=self._resolve_modality(
                payload_modality=payload.modality,
                service_modality=service.modality,
            ),
            location=self._clean_optional_string(payload.location),
            meeting_url=self._clean_optional_string(payload.meeting_url),
            notes=self._clean_optional_string(payload.notes),
        )

        return self.repository.create(appointment)

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
        page: int = 1,
        limit: int = 20,
    ) -> tuple[list[Appointment], int]:
        normalized_date_from = (
            self._normalize_datetime(date_from) if date_from else None
        )
        normalized_date_to = (
            self._normalize_datetime(date_to) if date_to else None
        )

        skip = (page - 1) * limit

        appointments = self.repository.list_appointments(
            search=search,
            patient_id=patient_id,
            service_id=service_id,
            status=status,
            modality=modality,
            created_source=created_source,
            created_by_user_id=created_by_user_id,
            assigned_to_user_id=assigned_to_user_id,
            date_from=normalized_date_from,
            date_to=normalized_date_to,
            skip=skip,
            limit=limit,
        )

        total = self.repository.count(
            search=search,
            patient_id=patient_id,
            service_id=service_id,
            status=status,
            modality=modality,
            created_source=created_source,
            created_by_user_id=created_by_user_id,
            assigned_to_user_id=assigned_to_user_id,
            date_from=normalized_date_from,
            date_to=normalized_date_to,
        )

        return appointments, total

    def get_appointment_by_id(
        self,
        appointment_id: uuid.UUID,
    ) -> Appointment:
        appointment = self.repository.get_by_id(appointment_id)

        if not appointment:
            raise NotFoundError("Appointment not found.")

        return appointment

    def update_appointment(
        self,
        *,
        appointment_id: uuid.UUID,
        payload: AppointmentUpdate,
    ) -> Appointment:
        appointment = self.get_appointment_by_id(appointment_id)

        if appointment.status in {
            AppointmentStatus.CANCELLED,
            AppointmentStatus.COMPLETED,
            AppointmentStatus.NO_SHOW,
        }:
            raise BadRequestError(
                "This appointment can no longer be edited."
            )

        data = payload.model_dump(exclude_unset=True)

        patient_id = data.get("patient_id", appointment.patient_id)
        service_id = data.get("service_id", appointment.service_id)

        patient = self._get_active_patient(patient_id)
        service = self._get_schedulable_service(service_id)

        if "assigned_to_user_id" in data:
            assigned_to_user = self._resolve_assigned_user(
                assigned_to_user_id=data["assigned_to_user_id"],
                current_user=None,
            )
            appointment.assigned_to_user_id = (
                assigned_to_user.id if assigned_to_user else None
            )

        scheduled_start = data.get(
            "scheduled_start",
            appointment.scheduled_start,
        )
        scheduled_start = self._normalize_datetime(scheduled_start)

        self._validate_not_past(scheduled_start)

        scheduled_end = self._calculate_scheduled_end(
            scheduled_start=scheduled_start,
            duration_minutes=service.duration_minutes,
        )

        self._validate_no_overlap(
            scheduled_start=scheduled_start,
            scheduled_end=scheduled_end,
            exclude_appointment_id=appointment.id,
        )

        appointment.patient_id = patient.id
        appointment.service_id = service.id
        appointment.scheduled_start = scheduled_start
        appointment.scheduled_end = scheduled_end

        if "timezone" in data:
            appointment.timezone = data["timezone"] or DEFAULT_TIMEZONE

        if "modality" in data:
            appointment.modality = data["modality"]

        if "location" in data:
            appointment.location = self._clean_optional_string(
                data["location"]
            )

        if "meeting_url" in data:
            appointment.meeting_url = self._clean_optional_string(
                data["meeting_url"]
            )

        if "notes" in data:
            appointment.notes = self._clean_optional_string(data["notes"])

        return self.repository.update(appointment)

    def confirm_appointment(self, appointment_id: uuid.UUID) -> Appointment:
        appointment = self.get_appointment_by_id(appointment_id)

        self._ensure_status_transition_allowed(
            appointment=appointment,
            allowed_statuses={
                AppointmentStatus.SCHEDULED,
                AppointmentStatus.RESCHEDULED,
            },
            action="confirm",
        )

        appointment.status = AppointmentStatus.CONFIRMED

        return self.repository.update(appointment)

    def complete_appointment(self, appointment_id: uuid.UUID) -> Appointment:
        appointment = self.get_appointment_by_id(appointment_id)

        self._ensure_status_transition_allowed(
            appointment=appointment,
            allowed_statuses={
                AppointmentStatus.SCHEDULED,
                AppointmentStatus.CONFIRMED,
                AppointmentStatus.RESCHEDULED,
            },
            action="complete",
        )

        appointment.status = AppointmentStatus.COMPLETED

        return self.repository.update(appointment)

    def cancel_appointment(
        self,
        *,
        appointment_id: uuid.UUID,
        payload: AppointmentCancelRequest,
    ) -> Appointment:
        appointment = self.get_appointment_by_id(appointment_id)

        self._ensure_status_transition_allowed(
            appointment=appointment,
            allowed_statuses={
                AppointmentStatus.SCHEDULED,
                AppointmentStatus.CONFIRMED,
                AppointmentStatus.RESCHEDULED,
            },
            action="cancel",
        )

        appointment.status = AppointmentStatus.CANCELLED
        appointment.cancellation_reason = payload.cancellation_reason.strip()

        return self.repository.update(appointment)

    def mark_no_show(
        self,
        *,
        appointment_id: uuid.UUID,
        payload: AppointmentNoShowRequest,
    ) -> Appointment:
        appointment = self.get_appointment_by_id(appointment_id)

        self._ensure_status_transition_allowed(
            appointment=appointment,
            allowed_statuses={
                AppointmentStatus.SCHEDULED,
                AppointmentStatus.CONFIRMED,
                AppointmentStatus.RESCHEDULED,
            },
            action="mark as no-show",
        )

        appointment.status = AppointmentStatus.NO_SHOW

        if payload.notes:
            appointment.notes = payload.notes.strip()

        return self.repository.update(appointment)

    def reschedule_appointment(
        self,
        *,
        appointment_id: uuid.UUID,
        payload: AppointmentRescheduleRequest,
    ) -> Appointment:
        appointment = self.get_appointment_by_id(appointment_id)

        self._ensure_status_transition_allowed(
            appointment=appointment,
            allowed_statuses={
                AppointmentStatus.SCHEDULED,
                AppointmentStatus.CONFIRMED,
                AppointmentStatus.RESCHEDULED,
            },
            action="reschedule",
        )

        service = self._get_schedulable_service(appointment.service_id)

        scheduled_start = self._normalize_datetime(payload.scheduled_start)
        self._validate_not_past(scheduled_start)

        scheduled_end = self._calculate_scheduled_end(
            scheduled_start=scheduled_start,
            duration_minutes=service.duration_minutes,
        )

        self._validate_no_overlap(
            scheduled_start=scheduled_start,
            scheduled_end=scheduled_end,
            exclude_appointment_id=appointment.id,
        )

        appointment.scheduled_start = scheduled_start
        appointment.scheduled_end = scheduled_end
        appointment.status = AppointmentStatus.RESCHEDULED
        appointment.reschedule_reason = payload.reschedule_reason.strip()

        return self.repository.update(appointment)

    def _resolve_assigned_user(
        self,
        *,
        assigned_to_user_id: uuid.UUID | None,
        current_user: User | None = None,
    ) -> User | None:
        if assigned_to_user_id:
            return self._get_active_internal_user(assigned_to_user_id)

        if current_user and current_user.user_type == UserType.PSYCHOLOGIST:
            return current_user

        return None

    def _get_active_internal_user(self, user_id: uuid.UUID) -> User:
        user = self.user_repository.get_by_id(user_id)

        if not user:
            raise NotFoundError("Assigned user not found.")

        if not user.is_active:
            raise BadRequestError("Assigned user is inactive.")

        if user.is_superuser:
            return user

        if user.user_type not in {
            UserType.ADMIN,
            UserType.PSYCHOLOGIST,
            UserType.ASSISTANT,
        }:
            raise BadRequestError("Assigned user must be an internal user.")

        return user

    def _get_active_patient(self, patient_id: uuid.UUID):
        patient = self.patient_repository.get_by_id(patient_id)

        if not patient:
            raise NotFoundError("Patient not found.")

        if not patient.is_active:
            raise BadRequestError("Patient is inactive.")

        return patient

    def _get_schedulable_service(self, service_id: uuid.UUID):
        service = self.service_repository.get_by_id(service_id)

        if not service:
            raise NotFoundError("Service not found.")

        if not service.is_active:
            raise BadRequestError("Service is inactive.")

        if not service.requires_appointment:
            raise BadRequestError(
                "Service does not require an appointment."
            )

        if service.duration_minutes is None:
            raise BadRequestError(
                "Service duration is required for appointments."
            )

        return service

    def _calculate_scheduled_end(
        self,
        *,
        scheduled_start: datetime,
        duration_minutes: int | None,
    ) -> datetime:
        if duration_minutes is None:
            raise BadRequestError(
                "Service duration is required for appointments."
            )

        return scheduled_start + timedelta(minutes=duration_minutes)

    def _validate_no_overlap(
        self,
        *,
        scheduled_start: datetime,
        scheduled_end: datetime,
        exclude_appointment_id: uuid.UUID | None = None,
    ) -> None:
        has_overlap = self.repository.has_overlap(
            scheduled_start=scheduled_start,
            scheduled_end=scheduled_end,
            exclude_appointment_id=exclude_appointment_id,
        )

        if has_overlap:
            raise BadRequestError(
                "There is already an appointment scheduled in this time range."
            )

    def _validate_not_past(self, scheduled_start: datetime) -> None:
        now = datetime.now(timezone.utc)

        if scheduled_start < now:
            raise BadRequestError("Appointment cannot be scheduled in the past.")

    def _normalize_datetime(self, value: datetime) -> datetime:
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)

        return value.astimezone(timezone.utc)

    def _resolve_modality(
        self,
        *,
        payload_modality: AppointmentModality,
        service_modality: ServiceModality,
    ) -> AppointmentModality:
        if payload_modality != AppointmentModality.UNSPECIFIED:
            return payload_modality

        modality_map = {
            ServiceModality.ONLINE: AppointmentModality.ONLINE,
            ServiceModality.IN_PERSON: AppointmentModality.IN_PERSON,
            ServiceModality.HYBRID: AppointmentModality.HYBRID,
        }

        return modality_map.get(
            service_modality,
            AppointmentModality.UNSPECIFIED,
        )

    def _ensure_status_transition_allowed(
        self,
        *,
        appointment: Appointment,
        allowed_statuses: set[AppointmentStatus],
        action: str,
    ) -> None:
        if appointment.status not in allowed_statuses:
            raise BadRequestError(
                f"Appointment cannot be {action} from current status."
            )

    def _clean_optional_string(self, value: str | None) -> str | None:
        if value is None:
            return None

        return value.strip() or None