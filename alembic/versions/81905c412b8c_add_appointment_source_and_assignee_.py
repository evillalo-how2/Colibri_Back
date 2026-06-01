"""add appointment source and assignee fields

Revision ID: 81905c412b8c
Revises: 29d813f08440
Create Date: 2026-05-22 09:35:22.160547

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "81905c412b8c"
down_revision: Union[str, Sequence[str], None] = "29d813f08440"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


appointment_created_source_enum = sa.Enum(
    "STAFF",
    "PATIENT",
    "BOT",
    "SYSTEM",
    name="appointment_created_source",
)


def upgrade() -> None:
    appointment_created_source_enum.create(op.get_bind(), checkfirst=True)

    op.add_column(
        "appointments",
        sa.Column(
            "created_source",
            appointment_created_source_enum,
            nullable=True,
        ),
    )

    op.add_column(
        "appointments",
        sa.Column("created_by_user_id", sa.UUID(), nullable=True),
    )

    op.add_column(
        "appointments",
        sa.Column("assigned_to_user_id", sa.UUID(), nullable=True),
    )

    op.execute("UPDATE appointments SET created_source = 'STAFF'")

    op.alter_column(
        "appointments",
        "created_source",
        existing_type=appointment_created_source_enum,
        nullable=False,
    )

    op.create_index(
        op.f("ix_appointments_created_source"),
        "appointments",
        ["created_source"],
        unique=False,
    )

    op.create_index(
        op.f("ix_appointments_created_by_user_id"),
        "appointments",
        ["created_by_user_id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_appointments_assigned_to_user_id"),
        "appointments",
        ["assigned_to_user_id"],
        unique=False,
    )

    op.create_foreign_key(
        "fk_appointments_created_by_user_id_users",
        "appointments",
        "users",
        ["created_by_user_id"],
        ["id"],
        ondelete="SET NULL",
    )

    op.create_foreign_key(
        "fk_appointments_assigned_to_user_id_users",
        "appointments",
        "users",
        ["assigned_to_user_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint(
        "fk_appointments_assigned_to_user_id_users",
        "appointments",
        type_="foreignkey",
    )

    op.drop_constraint(
        "fk_appointments_created_by_user_id_users",
        "appointments",
        type_="foreignkey",
    )

    op.drop_index(
        op.f("ix_appointments_assigned_to_user_id"),
        table_name="appointments",
    )

    op.drop_index(
        op.f("ix_appointments_created_by_user_id"),
        table_name="appointments",
    )

    op.drop_index(
        op.f("ix_appointments_created_source"),
        table_name="appointments",
    )

    op.drop_column("appointments", "assigned_to_user_id")
    op.drop_column("appointments", "created_by_user_id")
    op.drop_column("appointments", "created_source")

    appointment_created_source_enum.drop(op.get_bind(), checkfirst=True)