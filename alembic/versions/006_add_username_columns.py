"""add username to all user tables

Revision ID: 006
Revises: 005
Create Date: 2026-06-27

"""
from alembic import op
import sqlalchemy as sa

revision = '006'
down_revision = '005'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('patients',     sa.Column('username', sa.String(100), nullable=True))
    op.add_column('doctors',      sa.Column('username', sa.String(100), nullable=True))
    op.add_column('nurses',       sa.Column('username', sa.String(100), nullable=True))
    op.add_column('clinic_admins', sa.Column('username', sa.String(100), nullable=True))
    op.add_column('system_admins', sa.Column('username', sa.String(100), nullable=True))

    op.create_unique_constraint('uq_patients_username',     'patients',     ['username'])
    op.create_unique_constraint('uq_doctors_username',      'doctors',      ['username'])
    op.create_unique_constraint('uq_nurses_username',       'nurses',       ['username'])
    op.create_unique_constraint('uq_clinic_admins_username','clinic_admins',['username'])
    op.create_unique_constraint('uq_system_admins_username','system_admins',['username'])

    # email larni nullable qilish
    op.alter_column('doctors', 'email', existing_type=sa.String(255), nullable=True)
    op.alter_column('nurses',  'email', existing_type=sa.String(255), nullable=True)
    op.alter_column('clinic_admins', 'email', existing_type=sa.String(255), nullable=True)
    op.alter_column('system_admins', 'email', existing_type=sa.String(255), nullable=True)


def downgrade() -> None:
    op.drop_constraint('uq_patients_username',     'patients',     type_='unique')
    op.drop_constraint('uq_doctors_username',      'doctors',      type_='unique')
    op.drop_constraint('uq_nurses_username',       'nurses',       type_='unique')
    op.drop_constraint('uq_clinic_admins_username','clinic_admins',type_='unique')
    op.drop_constraint('uq_system_admins_username','system_admins',type_='unique')

    op.drop_column('patients',     'username')
    op.drop_column('doctors',      'username')
    op.drop_column('nurses',       'username')
    op.drop_column('clinic_admins','username')
    op.drop_column('system_admins','username')
