"""Add leagues table with proper structure

Revision ID: 008
Revises: 007
Create Date: 2023-08-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import func

revision = '008'
down_revision = '007'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create leagues table
    op.create_table('leagues',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('yahoo_league_id', sa.Text(), nullable=False),
        sa.Column('season', sa.SmallInteger(), nullable=False),
        sa.Column('name', sa.Text(), nullable=False),
        sa.Column('scoring_type', sa.Text(), nullable=False),
        sa.Column('roster_positions', sa.JSON(), nullable=False, server_default='[]'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('yahoo_league_id', name='uq_leagues_yahoo_league_id')
    )

    # Add updated_at trigger if not exists
    op.execute("""
    CREATE OR REPLACE FUNCTION update_updated_at_column()
    RETURNS TRIGGER AS $$
    BEGIN
        NEW.updated_at = now();
        RETURN NEW;
    END;
    $$ language 'plpgsql';
    """)

    # Add trigger to leagues
    op.execute("""
    DROP TRIGGER IF EXISTS update_leagues_updated_at ON leagues;
    CREATE TRIGGER update_leagues_updated_at
    BEFORE UPDATE ON leagues
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
    """)


def downgrade() -> None:
    # Remove trigger
    op.execute("DROP TRIGGER IF EXISTS update_leagues_updated_at ON leagues;")

    # Drop function
    op.execute("DROP FUNCTION IF EXISTS update_updated_at_column();")

    # Drop leagues table
    op.drop_table('leagues')
