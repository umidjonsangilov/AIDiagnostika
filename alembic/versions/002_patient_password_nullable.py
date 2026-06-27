"""patient hashed_password nullable

Revision ID: 002
Revises: 001
Create Date: 2026-06-27

"""
from alembic import op
import sqlalchemy as sa

revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column('patients', 'hashed_password',
                    existing_type=sa.String(255),
                    nullable=True)


def downgrade() -> None:
    op.alter_column('patients', 'hashed_password',
                    existing_type=sa.String(255),
                    nullable=False)
