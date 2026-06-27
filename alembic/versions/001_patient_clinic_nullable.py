"""patient clinic_id nullable

Revision ID: 001
Revises:
Create Date: 2026-06-27

"""
from alembic import op
import sqlalchemy as sa

revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column('patients', 'clinic_id',
                    existing_type=sa.Integer(),
                    nullable=True)


def downgrade() -> None:
    op.alter_column('patients', 'clinic_id',
                    existing_type=sa.Integer(),
                    nullable=False)
