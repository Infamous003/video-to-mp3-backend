"""create conversion jobs table

Revision ID: 56ff1762b9ce
Revises: 45aa68ebc65c
Create Date: 2025-12-31 16:32:12.633599

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '56ff1762b9ce'
down_revision: Union[str, Sequence[str], None] = '45aa68ebc65c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    jobstatus_enum = sa.Enum(
        "PENDING",
        "PROCESSING",
        "DONE",
        "FAILED",
        name="jobstatus",
    )
    op.create_table(
        "conversion_jobs",
        sa.Column("id", sa.Uuid(), primary_key=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("input_key", sa.String(), nullable=False),
        sa.Column("output_key", sa.String(), nullable=True),
        sa.Column("status", jobstatus_enum, nullable=False),
        sa.Column("error", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )

    op.create_index(
        "ix_conversion_jobs_user_id",
        "conversion_jobs",
        ["user_id"],
        unique=False,
    )

def downgrade() -> None:
    op.drop_index(
        "ix_conversion_jobs_user_id",
        table_name="conversion_jobs",
    )
    op.drop_table("conversion_jobs")
    sa.Enum(name="jobstatus").drop(op.get_bind(), checkfirst=True)