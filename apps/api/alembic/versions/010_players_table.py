"""Add players table with proper structure

Revision ID: 010
Revises: 009
Create Date: 2023-10-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import func

revision = '010'
down_revision = '009'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create players table
    op.create_table('players',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('yahoo_player_id', sa.Text(), nullable=True, unique=True),
        sa.Column('full_name', sa.Text(), nullable=False),
        sa.Column('position_primary', sa.Text(), nullable=True),
        sa.Column('nfl_team', sa.Text(), nullable=True),
        sa.Column('bye_week', sa.SmallInteger(), nullable=True),
        sa.Column('status', sa.Text(), nullable=True),
        sa.Column('meta', sa.JSON(), nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_players_pos', 'players', ['position_primary'], unique=False)

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

    # Add trigger to players
    op.execute("""
    DROP TRIGGER IF EXISTS update_players_updated_at ON players;
    CREATE TRIGGER update_players_updated_at
    BEFORE UPDATE ON players
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
    """)


def downgrade() -> None:
    # Remove trigger
    op.execute("DROP TRIGGER IF EXISTS update_players_updated_at ON players;")

    # Drop function
    op.execute("DROP FUNCTION IF EXISTS update_updated_at_column();")

    # Drop indexes
    op.drop_index('idx_players_pos', table_name='players')

    # Drop players table
    op.drop_table('players')
