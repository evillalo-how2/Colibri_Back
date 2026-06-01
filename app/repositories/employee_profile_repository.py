import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.employee_profile import EmployeeProfile


class EmployeeProfileRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_user_id(
        self,
        user_id: uuid.UUID,
    ) -> EmployeeProfile | None:
        statement = select(EmployeeProfile).where(
            EmployeeProfile.user_id == user_id
        )

        return self.db.scalar(statement)

    def create(
        self,
        *,
        user_id: uuid.UUID,
        data: dict[str, Any],
    ) -> EmployeeProfile:
        profile = EmployeeProfile(
            user_id=user_id,
            **data,
        )

        self.db.add(profile)
        self.db.commit()
        self.db.refresh(profile)

        return profile

    def update(
        self,
        *,
        profile: EmployeeProfile,
        data: dict[str, Any],
    ) -> EmployeeProfile:
        for field, value in data.items():
            setattr(profile, field, value)

        self.db.commit()
        self.db.refresh(profile)

        return profile

    def upsert(
        self,
        *,
        user_id: uuid.UUID,
        data: dict[str, Any],
    ) -> EmployeeProfile:
        profile = self.get_by_user_id(user_id)

        if profile:
            return self.update(
                profile=profile,
                data=data,
            )

        return self.create(
            user_id=user_id,
            data=data,
        )