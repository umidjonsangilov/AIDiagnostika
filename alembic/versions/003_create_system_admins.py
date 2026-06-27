"""create system_admins table

Revision ID: 003
Revises: 002
Create Date: 2026-06-27

"""
from alembic import op
import sqlalchemy as sa

revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'system_admins',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('full_name', sa.String(150), nullable=False),
        sa.Column('email', sa.String(255), unique=True, nullable=False),
        sa.Column('phone', sa.String(20), nullable=True),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
    )


def downgrade() -> None:
    op.drop_table('system_admins')
