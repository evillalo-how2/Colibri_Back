import uuid
from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_staff_user
from app.db.session import get_db
from app.models.appointment import (
    AppointmentCreatedSource,
    AppointmentModality,
    AppointmentStatus,
)
from app.models.user import User
from app.schemas.appointment import (
    AppointmentCancelRequest,
    AppointmentCreate,
    AppointmentNoShowRequest,
    AppointmentResponse,
    AppointmentRescheduleRequest,
    AppointmentsListResponse,
    AppointmentUpdate,
)
from app.services.appointment_service import AppointmentService

router = APIRouter()


@router.post(
    "",
    response_model=AppointmentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_appointment(
    payload: AppointmentCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_staff_user)],
) -> AppointmentResponse:
    appointment_service = AppointmentService(db)
    appointment = appointment_service.create_appointment(
        payload=payload,
        current_user=current_user,
    )

    return AppointmentResponse.model_validate(appointment)


@router.get(
    "",
    response_model=AppointmentsListResponse,
)
def list_appointments(
    db: Annotated[Session, Depends(get_db)],
    _current_user: Annotated[User, Depends(get_current_staff_user)],
    search: Annotated[
        str | None,
        Query(min_length=1, max_length=255),
    ] = None,
    patient_id: uuid.UUID | None = None,
    service_id: uuid.UUID | None = None,
    created_source: AppointmentCreatedSource | None = None,
    created_by_user_id: uuid.UUID | None = None,
    assigned_to_user_id: uuid.UUID | None = None,
    status: AppointmentStatus | None = None,
    modality: AppointmentModality | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    page: Annotated[int, Query(ge=1)] = 1,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
) -> AppointmentsListResponse:
    appointment_service = AppointmentService(db)
    appointments, total = appointment_service.list_appointments(
        search=search,
        patient_id=patient_id,
        service_id=service_id,
        created_source=created_source,
        created_by_user_id=created_by_user_id,
        assigned_to_user_id=assigned_to_user_id,
        status=status,
        modality=modality,
        date_from=date_from,
        date_to=date_to,
        page=page,
        limit=limit,
    )

    return AppointmentsListResponse(
        items=[
            AppointmentResponse.model_validate(appointment)
            for appointment in appointments
        ],
        total=total,
        page=page,
        limit=limit,
    )


@router.get(
    "/{appointment_id}",
    response_model=AppointmentResponse,
)
def get_appointment(
    appointment_id: uuid.UUID,
    db: Annotated[Session, Depends(get_db)],
    _current_user: Annotated[User, Depends(get_current_staff_user)],
) -> AppointmentResponse:
    appointment_service = AppointmentService(db)
    appointment = appointment_service.get_appointment_by_id(appointment_id)

    return AppointmentResponse.model_validate(appointment)


@router.patch(
    "/{appointment_id}",
    response_model=AppointmentResponse,
)
def update_appointment(
    appointment_id: uuid.UUID,
    payload: AppointmentUpdate,
    db: Annotated[Session, Depends(get_db)],
    _current_user: Annotated[User, Depends(get_current_staff_user)],
) -> AppointmentResponse:
    appointment_service = AppointmentService(db)
    appointment = appointment_service.update_appointment(
        appointment_id=appointment_id,
        payload=payload,
    )

    return AppointmentResponse.model_validate(appointment)


@router.patch(
    "/{appointment_id}/confirm",
    response_model=AppointmentResponse,
)
def confirm_appointment(
    appointment_id: uuid.UUID,
    db: Annotated[Session, Depends(get_db)],
    _current_user: Annotated[User, Depends(get_current_staff_user)],
) -> AppointmentResponse:
    appointment_service = AppointmentService(db)
    appointment = appointment_service.confirm_appointment(appointment_id)

    return AppointmentResponse.model_validate(appointment)


@router.patch(
    "/{appointment_id}/complete",
    response_model=AppointmentResponse,
)
def complete_appointment(
    appointment_id: uuid.UUID,
    db: Annotated[Session, Depends(get_db)],
    _current_user: Annotated[User, Depends(get_current_staff_user)],
) -> AppointmentResponse:
    appointment_service = AppointmentService(db)
    appointment = appointment_service.complete_appointment(appointment_id)

    return AppointmentResponse.model_validate(appointment)


@router.patch(
    "/{appointment_id}/cancel",
    response_model=AppointmentResponse,
)
def cancel_appointment(
    appointment_id: uuid.UUID,
    payload: AppointmentCancelRequest,
    db: Annotated[Session, Depends(get_db)],
    _current_user: Annotated[User, Depends(get_current_staff_user)],
) -> AppointmentResponse:
    appointment_service = AppointmentService(db)
    appointment = appointment_service.cancel_appointment(
        appointment_id=appointment_id,
        payload=payload,
    )

    return AppointmentResponse.model_validate(appointment)


@router.patch(
    "/{appointment_id}/no-show",
    response_model=AppointmentResponse,
)
def mark_no_show(
    appointment_id: uuid.UUID,
    payload: AppointmentNoShowRequest,
    db: Annotated[Session, Depends(get_db)],
    _current_user: Annotated[User, Depends(get_current_staff_user)],
) -> AppointmentResponse:
    appointment_service = AppointmentService(db)
    appointment = appointment_service.mark_no_show(
        appointment_id=appointment_id,
        payload=payload,
    )

    return AppointmentResponse.model_validate(appointment)


@router.patch(
    "/{appointment_id}/reschedule",
    response_model=AppointmentResponse,
)
def reschedule_appointment(
    appointment_id: uuid.UUID,
    payload: AppointmentRescheduleRequest,
    db: Annotated[Session, Depends(get_db)],
    _current_user: Annotated[User, Depends(get_current_staff_user)],
) -> AppointmentResponse:
    appointment_service = AppointmentService(db)
    appointment = appointment_service.reschedule_appointment(
        appointment_id=appointment_id,
        payload=payload,
    )

    return AppointmentResponse.model_validate(appointment)