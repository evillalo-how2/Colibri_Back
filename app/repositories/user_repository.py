import uuid
from datetime import datetime, timezone

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session
from sqlalchemy.sql.elements import ColumnElement

from app.models.user import User, UserType


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id: uuid.UUID) -> User | None:
        statement = select(User).where(User.id == user_id)
        return self.db.scalar(statement)

    def get_by_email(self, email: str) -> User | None:
        statement = select(User).where(User.email == email)
        return self.db.scalar(statement)

    def create(self, user: User) -> User:
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def list_users(
        self,
        *,
        search: str | None = None,
        user_type: UserType | None = None,
        is_active: bool | None = None,
        skip: int = 0,
        limit: int = 20,
    ) -> list[User]:
        conditions = self._build_filters(
            search=search,
            user_type=user_type,
            is_active=is_active,
        )

        statement = select(User)

        if conditions:
            statement = statement.where(*conditions)

        statement = (
            statement.order_by(User.created_at.desc())
            .offset(skip)
            .limit(limit)
        )

        return list(self.db.scalars(statement).all())

    def count(
        self,
        *,
        search: str | None = None,
        user_type: UserType | None = None,
        is_active: bool | None = None,
    ) -> int:
        conditions = self._build_filters(
            search=search,
            user_type=user_type,
            is_active=is_active,
        )

        statement = select(func.count()).select_from(User)

        if conditions:
            statement = statement.where(*conditions)

        return int(self.db.scalar(statement) or 0)

    def update(self, user: User) -> User:
        self.db.commit()
        self.db.refresh(user)
        return user

    def update_password_hash(
        self,
        *,
        user: User,
        password_hash: str,
    ) -> User:
        user.password_hash = password_hash
        user.password_changed_at = datetime.now(timezone.utc)

        self.db.commit()
        self.db.refresh(user)

        return user

    def _build_filters(
        self,
        *,
        search: str | None = None,
        user_type: UserType | None = None,
        is_active: bool | None = None,
    ) -> list[ColumnElement[bool]]:
        conditions: list[ColumnElement[bool]] = []

        if search:
            search_term = f"%{search.strip().lower()}%"
            conditions.append(
                or_(
                    func.lower(User.email).like(search_term),
                    func.lower(User.full_name).like(search_term),
                )
            )

        if user_type:
            conditions.append(User.user_type == user_type)

        if is_active is not None:
            conditions.append(User.is_active.is_(is_active))

        return conditions
    
    def count_active_superusers(self) -> int:
        statement = (
        select(func.count())
        .select_from(User)
        .where(
            User.is_superuser.is_(True),
            User.is_active.is_(True),
        )
    )

        return int(self.db.scalar(statement) or 0)