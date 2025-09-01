"""Make user email nullable

Revision ID: 002
Revises: 001
Create Date: 2023-01-01 06:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.alter_column('users', 'email', existing_type=sa.String(), nullable=True)

def downgrade() -> None:
    op.alter_column('users', 'email', existing_type=sa.String(), nullable=False)
