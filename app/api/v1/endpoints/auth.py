from typing import Annotated

from fastapi import APIRouter, Depends, Request, Response, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user
from app.core.config import settings
from app.core.cookies import (
    clear_refresh_cookie,
    get_refresh_token_from_cookie,
    set_refresh_cookie,
)
from app.core.exceptions import TooManyRequestsError
from app.core.rate_limit import rate_limiter
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import (
    AccessTokenResponse,
    ChangePasswordRequest,
    LoginRequest,
    TokenResponse,
)
from app.schemas.common import MessageResponse
from app.schemas.user import UserRead
from app.services.auth_service import AuthService

router = APIRouter()


def _get_client_ip(request: Request) -> str:
    if request.client:
        return request.client.host

    return "unknown"


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
)
def login(
    payload: LoginRequest,
    request: Request,
    response: Response,
    db: Annotated[Session, Depends(get_db)],
) -> TokenResponse:
    client_ip = _get_client_ip(request)
    rate_limit_key = f"login:{client_ip}"

    is_allowed = rate_limiter.is_allowed(
        key=rate_limit_key,
        limit=settings.LOGIN_RATE_LIMIT_MAX_ATTEMPTS,
        window_seconds=settings.LOGIN_RATE_LIMIT_WINDOW_SECONDS,
    )

    if not is_allowed:
        raise TooManyRequestsError(
            "Too many login attempts. Please try again later."
        )

    auth_service = AuthService(db)
    token_response, refresh_token = auth_service.login(payload)

    set_refresh_cookie(response, refresh_token)

    rate_limiter.reset(key=rate_limit_key)

    return token_response


@router.post(
    "/refresh",
    response_model=AccessTokenResponse,
    status_code=status.HTTP_200_OK,
)
def refresh_token(
    request: Request,
    db: Annotated[Session, Depends(get_db)],
) -> AccessTokenResponse:
    refresh_token_value = get_refresh_token_from_cookie(request)

    auth_service = AuthService(db)

    return auth_service.refresh_access_token(refresh_token_value)


@router.post(
    "/logout",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
)
def logout(
    request: Request,
    response: Response,
    db: Annotated[Session, Depends(get_db)],
) -> MessageResponse:
    refresh_token_value = request.cookies.get(settings.REFRESH_COOKIE_NAME)

    auth_service = AuthService(db)
    auth_service.logout(refresh_token_value)

    clear_refresh_cookie(response)

    return MessageResponse(message="Session closed successfully.")


@router.post(
    "/logout-all",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
)
def logout_all_sessions(
    response: Response,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)],
) -> MessageResponse:
    auth_service = AuthService(db)
    auth_service.logout_all_sessions(user=current_user)

    clear_refresh_cookie(response)

    return MessageResponse(message="All sessions closed successfully.")


@router.post(
    "/change-password",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
)
def change_password(
    payload: ChangePasswordRequest,
    response: Response,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)],
) -> MessageResponse:
    auth_service = AuthService(db)
    auth_service.change_password(
        user=current_user,
        payload=payload,
    )

    clear_refresh_cookie(response)

    return MessageResponse(message="Password changed successfully.")


@router.get(
    "/me",
    response_model=UserRead,
    status_code=status.HTTP_200_OK,
)
def get_me(
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> UserRead:
    return UserRead.model_validate(current_user)