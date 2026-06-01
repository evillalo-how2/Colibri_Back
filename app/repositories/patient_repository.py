import uuid

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session
from sqlalchemy.sql.elements import ColumnElement

from app.models.patient import Patient, PatientModality, PatientStatus


class PatientRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, patient_id: uuid.UUID) -> Patient | None:
        statement = select(Patient).where(Patient.id == patient_id)
        return self.db.scalar(statement)

    def list_patients(
        self,
        *,
        search: str | None = None,
        status: PatientStatus | None = None,
        preferred_modality: PatientModality | None = None,
        is_active: bool | None = None,
        skip: int = 0,
        limit: int = 20,
    ) -> list[Patient]:
        conditions = self._build_filters(
            search=search,
            status=status,
            preferred_modality=preferred_modality,
            is_active=is_active,
        )

        statement = select(Patient)

        if conditions:
            statement = statement.where(*conditions)

        statement = (
            statement.order_by(Patient.created_at.desc())
            .offset(skip)
            .limit(limit)
        )

        return list(self.db.scalars(statement).all())

    def count(
        self,
        *,
        search: str | None = None,
        status: PatientStatus | None = None,
        preferred_modality: PatientModality | None = None,
        is_active: bool | None = None,
    ) -> int:
        conditions = self._build_filters(
            search=search,
            status=status,
            preferred_modality=preferred_modality,
            is_active=is_active,
        )

        statement = select(func.count()).select_from(Patient)

        if conditions:
            statement = statement.where(*conditions)

        return int(self.db.scalar(statement) or 0)

    def create(self, patient: Patient) -> Patient:
        self.db.add(patient)
        self.db.commit()
        self.db.refresh(patient)

        return patient

    def update(self, patient: Patient) -> Patient:
        self.db.commit()
        self.db.refresh(patient)

        return patient

    def _build_filters(
        self,
        *,
        search: str | None = None,
        status: PatientStatus | None = None,
        preferred_modality: PatientModality | None = None,
        is_active: bool | None = None,
    ) -> list[ColumnElement[bool]]:
        conditions: list[ColumnElement[bool]] = []

        if search:
            search_term = f"%{search.strip().lower()}%"
            conditions.append(
                or_(
                    func.lower(Patient.full_name).like(search_term),
                    func.lower(Patient.email).like(search_term),
                    func.lower(Patient.phone).like(search_term),
                )
            )

        if status:
            conditions.append(Patient.status == status)

        if preferred_modality:
            conditions.append(
                Patient.preferred_modality == preferred_modality
            )

        if is_active is not None:
            conditions.append(Patient.is_active.is_(is_active))

        return conditions