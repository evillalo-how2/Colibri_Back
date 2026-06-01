import uuid
from typing import Any

from sqlalchemy.orm import Session

from app.core.exceptions import BadRequestError, NotFoundError
from app.models.user import UserType
from app.repositories.employee_profile_repository import (
    EmployeeProfileRepository,
)
from app.repositories.user_repository import UserRepository
from app.schemas.employee_profile import EmployeeProfileUpsert


INTERNAL_USER_TYPES = {
    UserType.ADMIN,
    UserType.PSYCHOLOGIST,
    UserType.ASSISTANT,
}


class EmployeeProfileService:
    def __init__(self, db: Session):
        self.user_repository = UserRepository(db)
        self.profile_repository = EmployeeProfileRepository(db)

    def get_profile_by_user_id(
        self,
        user_id: uuid.UUID,
    ):
        user = self.user_repository.get_by_id(user_id)

        if not user:
            raise NotFoundError("User not found.")

        self._validate_internal_user(user.user_type)

        profile = self.profile_repository.get_by_user_id(user_id)

        if not profile:
            raise NotFoundError("Employee profile not found.")

        return profile

    def upsert_profile(
        self,
        *,
        user_id: uuid.UUID,
        payload: EmployeeProfileUpsert,
    ):
        user = self.user_repository.get_by_id(user_id)

        if not user:
            raise NotFoundError("User not found.")

        self._validate_internal_user(user.user_type)

        data = self._clean_payload(payload)

        return self.profile_repository.upsert(
            user_id=user_id,
            data=data,
        )

    def _validate_internal_user(self, user_type: UserType) -> None:
        if user_type not in INTERNAL_USER_TYPES:
            raise BadRequestError(
                "Employee profile can only be assigned to internal users."
            )

    def _clean_payload(
        self,
        payload: EmployeeProfileUpsert,
    ) -> dict[str, Any]:
        data = payload.model_dump(exclude_unset=True)

        for field, value in data.items():
            if isinstance(value, str):
                data[field] = value.strip() or None

        return data