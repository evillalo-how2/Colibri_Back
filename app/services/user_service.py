import uuid

from sqlalchemy.orm import Session

from app.core.exceptions import BadRequestError, ConflictError, ForbiddenError, NotFoundError
from app.core.password_policy import validate_password_strength
from app.core.security import hash_password, verify_password
from app.core.validators import normalize_email, validate_full_name

from app.models.user import User, UserType

from app.repositories.user_repository import UserRepository
from app.repositories.refresh_token_repository import RefreshTokenRepository

from app.schemas.user import UserCreate, UserRoleUpdate, UserUpdate


class UserService:
    def __init__(self, db: Session):
        self.repository = UserRepository(db)
        self.refresh_token_repository = RefreshTokenRepository(db)

    def create_user(self, payload: UserCreate) -> User:
        normalized_email = normalize_email(payload.email)

        if payload.full_name is None:
            raise BadRequestError("Full name is required.")

        normalized_full_name = payload.full_name.strip()

        validate_full_name(normalized_full_name)

        existing_user = self.repository.get_by_email(normalized_email)

        if existing_user:
            raise ConflictError("A user with this email already exists.")

        validate_password_strength(
            payload.password,
            email=normalized_email,
            full_name=normalized_full_name,
        )

        user = User(
            email=normalized_email,
            full_name=normalized_full_name,
            password_hash=hash_password(payload.password),
            user_type=payload.user_type,
            is_active=payload.is_active,
        )

        return self.repository.create(user)

    def get_user(self, user_id: uuid.UUID) -> User:
        user = self.repository.get_by_id(user_id)

        if not user:
            raise NotFoundError("User not found.")

        return user

    def list_users(
        self,
        *,
        search: str | None = None,
        user_type: UserType | None = None,
        is_active: bool | None = None,
        page: int = 1,
        limit: int = 20,
    ) -> tuple[list[User], int]:
        if page < 1:
            raise BadRequestError("Page must be greater than or equal to 1.")

        if limit < 1:
            raise BadRequestError("Limit must be greater than or equal to 1.")

        skip = (page - 1) * limit

        users = self.repository.list_users(
            search=search,
            user_type=user_type,
            is_active=is_active,
            skip=skip,
            limit=limit,
        )

        total = self.repository.count(
            search=search,
            user_type=user_type,
            is_active=is_active,
        )

        return users, total

    def update_user(
        self,
        *,
        user_id: uuid.UUID,
        payload: UserUpdate,
    ) -> User:
        user = self.get_user(user_id)

        if payload.email is not None:
            normalized_email = normalize_email(payload.email)

            existing_user = self.repository.get_by_email(normalized_email)

            if existing_user and existing_user.id != user.id:
                raise ConflictError("A user with this email already exists.")

            user.email = normalized_email

        if payload.full_name is not None:
            normalized_full_name = payload.full_name.strip()
            validate_full_name(normalized_full_name)
            user.full_name = normalized_full_name

        return self.repository.update(user)

    def update_user_role(
        self,
        *,
        actor: User,
        user_id: uuid.UUID,
        payload: UserRoleUpdate,
    ) -> User:
        user = self.get_user(user_id)

        if actor.id == user.id:
            raise BadRequestError("You cannot change your own role.")

        user.user_type = payload.user_type

        return self.repository.update(user)

    def update_user_password(
        self,
        *,
        user_id: uuid.UUID,
        new_password: str,
        current_user: User,
    ) -> None:
        user = self.get_user(user_id)

        if user.is_superuser and not current_user.is_superuser:
            raise ForbiddenError(
                "Only a superuser can update another superuser password."
            )

        if verify_password(new_password, user.password_hash):
            raise BadRequestError(
                "New password must be different from current password."
            )

        validate_password_strength(
            new_password,
            email=user.email,
            full_name=user.full_name,
        )

        self.repository.update_password_hash(
            user=user,
            password_hash=hash_password(new_password),
        )

        self.refresh_token_repository.revoke_all_for_user(user.id)

    def activate_user(
        self,
        *,
        user_id: uuid.UUID,
    ) -> User:
        user = self.get_user(user_id)

        user.is_active = True

        return self.repository.update(user)

    def deactivate_user(
        self,
        *,
        actor: User,
        user_id: uuid.UUID,
    ) -> User:
        user = self.get_user(user_id)

        if actor.id == user.id:
            raise ForbiddenError("You cannot deactivate your own account.")

        if user.is_superuser and not actor.is_superuser:
            raise ForbiddenError(
                "Only a superuser can deactivate another superuser."
            )

        if user.is_superuser:
            active_superuser_count = self.repository.count_active_superusers()

            if active_superuser_count <= 1:
                raise ForbiddenError(
                    "Cannot deactivate the last active superuser."
                )

        user.is_active = False

        return self.repository.update(user)