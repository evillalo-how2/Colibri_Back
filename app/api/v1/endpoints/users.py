import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_admin_user
from app.db.session import get_db
from app.models.user import User, UserType
from app.schemas.user import (
    UserCreate,
    UserListResponse,
    UserPasswordUpdate,
    UserRead,
    UserRoleUpdate,
    UserUpdate,
)
from app.schemas.employee_profile import (
    EmployeeProfileResponse,
    EmployeeProfileUpsert,
)
from app.services.employee_profile_service import EmployeeProfileService
from app.services.user_service import UserService

from app.schemas.common import MessageResponse

router = APIRouter()


@router.post(
    "",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
)
def create_user(
    payload: UserCreate,
    db: Annotated[Session, Depends(get_db)],
    _current_user: Annotated[User, Depends(get_current_admin_user)],
) -> UserRead:
    user_service = UserService(db)
    user = user_service.create_user(payload)

    return UserRead.model_validate(user)


@router.get(
    "",
    response_model=UserListResponse,
)
def list_users(
    db: Annotated[Session, Depends(get_db)],
    _current_user: Annotated[User, Depends(get_current_admin_user)],
    search: Annotated[
        str | None,
        Query(min_length=1, max_length=255),
    ] = None,
    user_type: UserType | None = None,
    is_active: bool | None = None,
    page: Annotated[int, Query(ge=1)] = 1,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
) -> UserListResponse:
    user_service = UserService(db)
    users, total = user_service.list_users(
        search=search,
        user_type=user_type,
        is_active=is_active,
        page=page,
        limit=limit,
    )

    return UserListResponse(
        items=[UserRead.model_validate(user) for user in users],
        total=total,
        page=page,
        limit=limit,
    )


@router.get(
    "/{user_id}",
    response_model=UserRead,
)
def get_user(
    user_id: uuid.UUID,
    db: Annotated[Session, Depends(get_db)],
    _current_user: Annotated[User, Depends(get_current_admin_user)],
) -> UserRead:
    user_service = UserService(db)
    user = user_service.get_user(user_id)

    return UserRead.model_validate(user)


@router.patch(
    "/{user_id}",
    response_model=UserRead,
)
def update_user(
    user_id: uuid.UUID,
    payload: UserUpdate,
    db: Annotated[Session, Depends(get_db)],
    _current_user: Annotated[User, Depends(get_current_admin_user)],
) -> UserRead:
    user_service = UserService(db)
    user = user_service.update_user(
        user_id=user_id,
        payload=payload,
    )

    return UserRead.model_validate(user)


@router.patch(
    "/{user_id}/role",
    response_model=UserRead,
)
def update_user_role(
    user_id: uuid.UUID,
    payload: UserRoleUpdate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_admin_user)],
) -> UserRead:
    user_service = UserService(db)
    user = user_service.update_user_role(
        actor=current_user,
        user_id=user_id,
        payload=payload,
    )

    return UserRead.model_validate(user)


@router.patch(
    "/{user_id}/activate",
    response_model=UserRead,
)
def activate_user(
    user_id: uuid.UUID,
    db: Annotated[Session, Depends(get_db)],
    _current_user: Annotated[User, Depends(get_current_admin_user)],
) -> UserRead:
    user_service = UserService(db)
    user = user_service.activate_user(user_id=user_id)

    return UserRead.model_validate(user)


@router.patch(
    "/{user_id}/deactivate",
    response_model=UserRead,
)
def deactivate_user(
    user_id: uuid.UUID,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_admin_user)],
) -> UserRead:
    user_service = UserService(db)
    user = user_service.deactivate_user(
        actor=current_user,
        user_id=user_id,
    )

    return UserRead.model_validate(user)

@router.get(
    "/{user_id}/profile",
    response_model=EmployeeProfileResponse,
)
def get_employee_profile(
    user_id: uuid.UUID,
    db: Annotated[Session, Depends(get_db)],
    _current_user: Annotated[User, Depends(get_current_admin_user)],
) -> EmployeeProfileResponse:
    profile_service = EmployeeProfileService(db)
    profile = profile_service.get_profile_by_user_id(user_id)

    return EmployeeProfileResponse.model_validate(profile)


@router.put(
    "/{user_id}/profile",
    response_model=EmployeeProfileResponse,
)
def upsert_employee_profile(
    user_id: uuid.UUID,
    payload: EmployeeProfileUpsert,
    db: Annotated[Session, Depends(get_db)],
    _current_user: Annotated[User, Depends(get_current_admin_user)],
) -> EmployeeProfileResponse:
    profile_service = EmployeeProfileService(db)
    profile = profile_service.upsert_profile(
        user_id=user_id,
        payload=payload,
    )

    return EmployeeProfileResponse.model_validate(profile)

@router.patch(
    "/{user_id}/password",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
)
def update_user_password(
    user_id: uuid.UUID,
    payload: UserPasswordUpdate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_admin_user)],
) -> MessageResponse:
    user_service = UserService(db)
    user_service.update_user_password(
        user_id=user_id,
        new_password=payload.new_password,
        current_user=current_user,
    )

    return MessageResponse(message="User password updated successfully.")