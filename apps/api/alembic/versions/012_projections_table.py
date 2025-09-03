"""Add projections table

Revision ID: 012
Revises: 011
Create Date: 2023-12-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import func

revision = '012'
down_revision = '011'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create projections table
    op.create_table('projections',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('player_id', sa.Integer(), nullable=False),
        sa.Column('week', sa.SmallInteger(), nullable=False),
        sa.Column('source', sa.Text(), nullable=False),
        sa.Column('points', sa.Numeric(6, 2), nullable=False),
        sa.Column('breakdown', sa.JSON(), nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=func.now(), nullable=False),
        sa.ForeignKeyConstraint(['player_id'], ['players.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('player_id', 'week', 'source', name='uq_projections_player_week_source')
    )
    op.create_index('idx_projections_week', 'projections', ['week'], unique=False)

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

    # Add trigger to projections
    op.execute("""
    DROP TRIGGER IF EXISTS update_projections_updated_at ON projections;
    CREATE TRIGGER update_projections_updated_at
    BEFORE UPDATE ON projections
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
    """)


def downgrade() -> None:
    # Remove trigger
    op.execute("DROP TRIGGER IF EXISTS update_projections_updated_at ON projections;")

    # Drop function
    op.execute("DROP FUNCTION IF EXISTS update_updated_at_column();")

    # Drop indexes
    op.drop_index('idx_projections_week', table_name='projections')

    # Drop constraints
    op.drop_constraint('uq_projections_player_week_source', 'projections', type_='unique')

    # Drop projections table
    op.drop_table('projections')
