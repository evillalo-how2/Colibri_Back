from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.exceptions import BadRequestError, UnauthorizedError,InactiveUserError, UnauthorizedError
from app.core.password_policy import validate_password_strength
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    hash_token,
    verify_password,
    verify_token_hash,
)

from app.models.refresh_token import RefreshToken
from app.models.user import User
from app.repositories.refresh_token_repository import RefreshTokenRepository
from app.repositories.user_repository import UserRepository
from app.schemas.auth import (
    AccessTokenResponse,
    ChangePasswordRequest,
    LoginRequest,
    TokenResponse,
)


class AuthService:
    def __init__(self, db: Session):
        self.user_repository = UserRepository(db)
        self.refresh_token_repository = RefreshTokenRepository(db)

    def login(self, payload: LoginRequest) -> tuple[TokenResponse, str]:
        user = self.user_repository.get_by_email(payload.email)

        if not user:
            raise UnauthorizedError("Invalid email or password.")

        if not verify_password(payload.password, user.password_hash):
            raise UnauthorizedError("Invalid email or password.")

        if not user.is_active:
            raise InactiveUserError("User account is inactive.")

        access_token = self._create_user_access_token(user)
        refresh_token, token_id, expires_at = create_refresh_token(
            subject=str(user.id)
        )

        refresh_token_record = RefreshToken(
            user_id=user.id,
            token_id=token_id,
            token_hash=hash_token(refresh_token),
            expires_at=expires_at,
        )

        self.refresh_token_repository.create(refresh_token_record)

        return (
            TokenResponse(
                access_token=access_token,
                token_type="bearer",
            ),
            refresh_token,
        )

    def refresh_access_token(
        self,
        refresh_token: str,
    ) -> AccessTokenResponse:
        token_payload = decode_token(refresh_token)

        if token_payload.get("type") != "refresh":
            raise UnauthorizedError("Invalid token type.")

        token_id = token_payload.get("jti")
        user_id = token_payload.get("sub")

        if not token_id or not user_id:
            raise UnauthorizedError("Invalid refresh token.")

        refresh_token_record = self.refresh_token_repository.get_by_token_id(
            token_id
        )

        if not refresh_token_record:
            raise UnauthorizedError("Invalid refresh token.")

        if refresh_token_record.is_revoked:
            raise UnauthorizedError("Refresh token has been revoked.")

        if refresh_token_record.expires_at <= datetime.now(timezone.utc):
            raise UnauthorizedError("Refresh token has expired.")

        if not verify_token_hash(
            refresh_token,
            refresh_token_record.token_hash,
        ):
            raise UnauthorizedError("Invalid refresh token.")

        user = self.user_repository.get_by_id(UUID(user_id))

        if not user:
            raise UnauthorizedError("User not found.")

        if not user.is_active:
            raise UnauthorizedError("User account is inactive.")

        access_token = self._create_user_access_token(user)

        return AccessTokenResponse(
            access_token=access_token,
            token_type="bearer",
        )

    def logout(self, refresh_token: str | None) -> None:
        if not refresh_token:
            return

        try:
            token_payload = decode_token(refresh_token)

            if token_payload.get("type") != "refresh":
                return

            token_id = token_payload.get("jti")

            if not token_id:
                return

            refresh_token_record = (
                self.refresh_token_repository.get_by_token_id(token_id)
            )

            if not refresh_token_record:
                return

            if not verify_token_hash(
                refresh_token,
                refresh_token_record.token_hash,
            ):
                return

            if not refresh_token_record.is_revoked:
                self.refresh_token_repository.revoke(refresh_token_record)

        except UnauthorizedError:
            return

    def change_password(
        self,
        *,
        user: User,
        payload: ChangePasswordRequest,
    ) -> None:
        if not verify_password(payload.current_password, user.password_hash):
            raise UnauthorizedError("Current password is incorrect.")

        if verify_password(payload.new_password, user.password_hash):
            raise BadRequestError(
                "New password must be different from current password."
            )

        validate_password_strength(
            payload.new_password,
            email=user.email,
            full_name=user.full_name,
        )

        self.user_repository.update_password_hash(
            user=user,
            password_hash=hash_password(payload.new_password),
        )

        self.refresh_token_repository.revoke_all_for_user(user.id)

    def logout_all_sessions(self, *, user: User) -> None:
        self.refresh_token_repository.revoke_all_for_user(user.id)

    def _create_user_access_token(self, user: User) -> str:
        return create_access_token(
            subject=str(user.id),
            additional_claims={
                "email": user.email,
                "user_type": user.user_type.value,
                "is_superuser": user.is_superuser,
            },
        )