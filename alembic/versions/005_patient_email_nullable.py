"""patient email nullable

Revision ID: 005
Revises: 004
Create Date: 2026-06-27

"""
from alembic import op
import sqlalchemy as sa

revision = '005'
down_revision = '004'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column('patients', 'email',
                    existing_type=sa.String(255),
                    nullable=True)


def downgrade() -> None:
    op.alter_column('patients', 'email',
                    existing_type=sa.String(255),
                    nullable=False)
