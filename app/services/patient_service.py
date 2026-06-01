import uuid
from typing import Any

from sqlalchemy.orm import Session

from app.core.exceptions import BadRequestError, NotFoundError
from app.core.validators import (
    normalize_mexican_phone,
    normalize_patient_gender,
    validate_birth_date,
    validate_full_name,
    validate_realistic_email,
)
from app.models.patient import Patient, PatientModality, PatientStatus
from app.repositories.patient_repository import PatientRepository
from app.schemas.patient import (
    PatientCreate,
    PatientStatusUpdate,
    PatientUpdate,
)


class PatientService:
    def __init__(self, db: Session):
        self.repository = PatientRepository(db)

    def create_patient(self, payload: PatientCreate) -> Patient:
        normalized_full_name = payload.full_name.strip()
        validate_full_name(normalized_full_name)

        normalized_email = validate_realistic_email(payload.email)
        normalized_phone = normalize_mexican_phone(payload.phone)

        self._validate_contact_method(
            email=normalized_email,
            phone=normalized_phone,
        )

        patient = Patient(
            full_name=normalized_full_name,
            email=normalized_email,
            phone=normalized_phone,
            birth_date=validate_birth_date(payload.birth_date),
            gender=normalize_patient_gender(payload.gender),
            preferred_modality=payload.preferred_modality,
            status=PatientStatus.NEW,
            status_note=None,
            source=self._clean_optional_string(payload.source),
            initial_reason=self._clean_optional_string(payload.initial_reason),
            internal_notes=self._clean_optional_string(payload.internal_notes),
            is_active=True,
        )

        return self.repository.create(patient)

    def list_patients(
        self,
        *,
        search: str | None = None,
        status: PatientStatus | None = None,
        preferred_modality: PatientModality | None = None,
        is_active: bool | None = None,
        page: int = 1,
        limit: int = 20,
    ) -> tuple[list[Patient], int]:
        skip = (page - 1) * limit

        patients = self.repository.list_patients(
            search=search,
            status=status,
            preferred_modality=preferred_modality,
            is_active=is_active,
            skip=skip,
            limit=limit,
        )

        total = self.repository.count(
            search=search,
            status=status,
            preferred_modality=preferred_modality,
            is_active=is_active,
        )

        return patients, total

    def get_patient_by_id(self, patient_id: uuid.UUID) -> Patient:
        patient = self.repository.get_by_id(patient_id)

        if not patient:
            raise NotFoundError("Patient not found.")

        return patient

    def update_patient(
        self,
        *,
        patient_id: uuid.UUID,
        payload: PatientUpdate,
        ) -> Patient:
        patient = self.get_patient_by_id(patient_id)
        data = payload.model_dump(exclude_unset=True)

        if "full_name" in data and data["full_name"] is not None:
            normalized_full_name = data["full_name"].strip()
            validate_full_name(normalized_full_name)
            patient.full_name = normalized_full_name

        if "email" in data:
            patient.email = validate_realistic_email(data["email"])

        if "phone" in data:
            patient.phone = normalize_mexican_phone(data["phone"])

        if "birth_date" in data:
            patient.birth_date = validate_birth_date(data["birth_date"])

        if "gender" in data:
            patient.gender = normalize_patient_gender(data["gender"])

        self._assign_optional_fields(
            patient=patient,
            data=data,
            excluded_fields={
                "full_name",
                "email",
                "phone",
                "birth_date",
                "gender",
            },
        )

        self._validate_contact_method(
            email=patient.email,
            phone=patient.phone,
        )

        return self.repository.update(patient)

    def update_patient_status(
        self,
        *,
        patient_id: uuid.UUID,
        payload: PatientStatusUpdate,
    ) -> Patient:
        patient = self.get_patient_by_id(patient_id)

        patient.status = payload.status
        patient.status_note = payload.status_note.strip()

        if payload.status == PatientStatus.INACTIVE:
            patient.is_active = False
        else:
            patient.is_active = True

        return self.repository.update(patient)

    def _assign_optional_fields(
        self,
        *,
        patient: Patient,
        data: dict[str, Any],
        excluded_fields: set[str],
    ) -> None:
        for field, value in data.items():
            if field in excluded_fields:
                continue

            if isinstance(value, str):
                value = value.strip() or None

            setattr(patient, field, value)

    def _clean_optional_string(self, value: str | None) -> str | None:
        if value is None:
            return None

        return value.strip() or None

    def _validate_contact_method(
        self,
        *,
        email: str | None,
        phone: str | None,
    ) -> None:
        has_email = bool(email and email.strip())
        has_phone = bool(phone and phone.strip())

        if not has_email and not has_phone:
            raise BadRequestError(
                "At least one contact method is required: email or phone."
            )