"""add catalog code to services

Revision ID: b602637e5c89
Revises: 250dd9540b8c
Create Date: 2026-05-20 10:30:17.675019

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "b602637e5c89"
down_revision: Union[str, Sequence[str], None] = "250dd9540b8c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


SERVICE_TYPE_CODE_PREFIX = {
    "THERAPY": "TER",
    "WORKSHOP": "WKS",
    "COURSE": "CUR",
    "BOOK": "LIB",
    "DIGITAL_PRODUCT": "DIG",
    "PHYSICAL_PRODUCT": "PHY",
    "ACTIVITY": "ACT",
    "EVENT": "EVT",
    "RETREAT": "RET",
    "OTHER": "OTH",
    "therapy": "TER",
    "workshop": "WKS",
    "course": "CUR",
    "book": "LIB",
    "digital_product": "DIG",
    "physical_product": "PHY",
    "activity": "ACT",
    "event": "EVT",
    "retreat": "RET",
    "other": "OTH",
}


def upgrade() -> None:
    op.add_column(
        "services",
        sa.Column("catalog_code", sa.String(length=32), nullable=True),
    )

    connection = op.get_bind()

    services = connection.execute(
        sa.text(
            """
            SELECT id, type
            FROM services
            ORDER BY created_at ASC
            """
        )
    ).mappings().all()

    for index, service in enumerate(services, start=1):
        service_type = str(service["type"])
        prefix = SERVICE_TYPE_CODE_PREFIX.get(service_type, "OTH")
        catalog_code = f"PSI-{prefix}-{index:06d}"

        connection.execute(
            sa.text(
                """
                UPDATE services
                SET catalog_code = :catalog_code
                WHERE id = :service_id
                """
            ),
            {
                "catalog_code": catalog_code,
                "service_id": service["id"],
            },
        )

    op.alter_column(
        "services",
        "catalog_code",
        existing_type=sa.String(length=32),
        nullable=False,
    )

    op.create_index(
        op.f("ix_services_catalog_code"),
        "services",
        ["catalog_code"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_services_catalog_code"), table_name="services")
    op.drop_column("services", "catalog_code")