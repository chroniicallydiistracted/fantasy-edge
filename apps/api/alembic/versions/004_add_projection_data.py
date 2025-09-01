"""Add projection data column

Revision ID: 004
Revises: 003
Create Date: 2023-01-01 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = '004'
down_revision = '003'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('projections', sa.Column('data', sa.JSON(), nullable=False, server_default='{}'))
    op.add_column('projections', sa.Column('variance', sa.Float(), nullable=True))
    op.alter_column('projections', 'data', server_default=None)


def downgrade() -> None:
    op.drop_column('projections', 'variance')
    op.drop_column('projections', 'data')
