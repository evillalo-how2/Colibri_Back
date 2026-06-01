import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_staff_user
from app.db.session import get_db
from app.models.patient import PatientModality, PatientStatus
from app.models.user import User
from app.schemas.patient import (
    PatientCreate,
    PatientResponse,
    PatientsListResponse,
    PatientStatusUpdate,
    PatientUpdate,
)
from app.services.patient_service import PatientService

router = APIRouter()


@router.post(
    "",
    response_model=PatientResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_patient(
    payload: PatientCreate,
    db: Annotated[Session, Depends(get_db)],
    _current_user: Annotated[User, Depends(get_current_staff_user)],
) -> PatientResponse:
    patient_service = PatientService(db)
    patient = patient_service.create_patient(payload)

    return PatientResponse.model_validate(patient)


@router.get(
    "",
    response_model=PatientsListResponse,
)
def list_patients(
    db: Annotated[Session, Depends(get_db)],
    _current_user: Annotated[User, Depends(get_current_staff_user)],
    search: Annotated[
        str | None,
        Query(min_length=1, max_length=255),
    ] = None,
    status: PatientStatus | None = None,
    preferred_modality: PatientModality | None = None,
    is_active: bool | None = None,
    page: Annotated[int, Query(ge=1)] = 1,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
) -> PatientsListResponse:
    patient_service = PatientService(db)
    patients, total = patient_service.list_patients(
        search=search,
        status=status,
        preferred_modality=preferred_modality,
        is_active=is_active,
        page=page,
        limit=limit,
    )

    return PatientsListResponse(
        items=[PatientResponse.model_validate(patient) for patient in patients],
        total=total,
        page=page,
        limit=limit,
    )


@router.get(
    "/{patient_id}",
    response_model=PatientResponse,
)
def get_patient(
    patient_id: uuid.UUID,
    db: Annotated[Session, Depends(get_db)],
    _current_user: Annotated[User, Depends(get_current_staff_user)],
) -> PatientResponse:
    patient_service = PatientService(db)
    patient = patient_service.get_patient_by_id(patient_id)

    return PatientResponse.model_validate(patient)


@router.patch(
    "/{patient_id}",
    response_model=PatientResponse,
)
def update_patient(
    patient_id: uuid.UUID,
    payload: PatientUpdate,
    db: Annotated[Session, Depends(get_db)],
    _current_user: Annotated[User, Depends(get_current_staff_user)],
) -> PatientResponse:
    patient_service = PatientService(db)
    patient = patient_service.update_patient(
        patient_id=patient_id,
        payload=payload,
    )

    return PatientResponse.model_validate(patient)


@router.patch(
    "/{patient_id}/status",
    response_model=PatientResponse,
)
def update_patient_status(
    patient_id: uuid.UUID,
    payload: PatientStatusUpdate,
    db: Annotated[Session, Depends(get_db)],
    _current_user: Annotated[User, Depends(get_current_staff_user)],
) -> PatientResponse:
    patient_service = PatientService(db)
    patient = patient_service.update_patient_status(
        patient_id=patient_id,
        payload=payload,
    )

    return PatientResponse.model_validate(patient)