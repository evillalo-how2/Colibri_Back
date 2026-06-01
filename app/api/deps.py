import uuid
from datetime import datetime, timezone
from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.exceptions import ForbiddenError, InactiveUserError, UnauthorizedError
from app.core.security import decode_token
from app.db.session import get_db
from app.models.user import User, UserType
from app.repositories.user_repository import UserRepository

bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: Annotated[
        HTTPAuthorizationCredentials | None,
        Depends(bearer_scheme),
    ],
    db: Annotated[Session, Depends(get_db)],
) -> User:
    if credentials is None:
        raise UnauthorizedError("Authentication credentials were not provided.")

    if credentials.scheme.lower() != "bearer":
        raise UnauthorizedError("Invalid authentication scheme.")

    token_payload = decode_token(credentials.credentials)

    if token_payload.get("type") != "access":
        raise UnauthorizedError("Invalid token type.")

    user_id = token_payload.get("sub")

    if not user_id:
        raise UnauthorizedError("Invalid token payload.")

    try:
        parsed_user_id = uuid.UUID(user_id)
    except ValueError as exc:
        raise UnauthorizedError("Invalid token subject.") from exc

    user_repository = UserRepository(db)
    user = user_repository.get_by_id(parsed_user_id)

    if not user:
        raise UnauthorizedError("User not found.")

    token_issued_at = token_payload.get("iat")

    if user.password_changed_at and token_issued_at:
        issued_at = datetime.fromtimestamp(
            int(token_issued_at),
            tz=timezone.utc,
        )

        if issued_at < user.password_changed_at:
            raise UnauthorizedError(
                "Token was issued before the last password change."
            )

    return user


def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    if not current_user.is_active:
        raise InactiveUserError("User account is inactive.")

    return current_user


def get_current_admin_user(
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> User:
    if current_user.is_superuser:
        return current_user

    if current_user.user_type == UserType.ADMIN:
        return current_user

    raise ForbiddenError("You do not have permission to perform this action.")

def get_current_staff_user(
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> User:
    if current_user.is_superuser:
        return current_user

    if current_user.user_type in {
        UserType.ADMIN,
        UserType.PSYCHOLOGIST,
        UserType.ASSISTANT,
    }:
        return current_user

    raise ForbiddenError("You do not have permission to perform this action.")

def get_current_catalog_manager_user(
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> User:
    if current_user.is_superuser:
        return current_user

    if current_user.user_type in {
        UserType.ADMIN,
        UserType.PSYCHOLOGIST,
    }:
        return current_user

    raise ForbiddenError("You do not have permission to perform this action.")