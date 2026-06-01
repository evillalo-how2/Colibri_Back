from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.refresh_token import RefreshToken


class RefreshTokenRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, refresh_token: RefreshToken) -> RefreshToken:
        self.db.add(refresh_token)
        self.db.commit()
        self.db.refresh(refresh_token)
        return refresh_token

    def get_by_token_id(self, token_id: str) -> RefreshToken | None:
        statement = select(RefreshToken).where(
            RefreshToken.token_id == token_id
        )
        return self.db.scalar(statement)

    def revoke(self, refresh_token: RefreshToken) -> RefreshToken:
        refresh_token.is_revoked = True
        refresh_token.revoked_at = datetime.now(timezone.utc)

        self.db.commit()
        self.db.refresh(refresh_token)

        return refresh_token

    def revoke_all_for_user(self, user_id: UUID) -> None:
        statement = select(RefreshToken).where(
            RefreshToken.user_id == user_id,
            RefreshToken.is_revoked.is_(False),
        )

        refresh_tokens = self.db.scalars(statement).all()
        now = datetime.now(timezone.utc)

        for refresh_token in refresh_tokens:
            refresh_token.is_revoked = True
            refresh_token.revoked_at = now

        self.db.commit()