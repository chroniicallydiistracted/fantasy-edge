"""Add waiver_candidates and streamer_signals tables

Revision ID: 013
Revises: 012
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import func

revision = '013'
down_revision = '012'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create waiver_candidates table
    op.create_table('waiver_candidates',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('league_id', sa.Integer(), nullable=False),
        sa.Column('week', sa.SmallInteger(), nullable=False),
        sa.Column('player_id', sa.Integer(), nullable=False),
        sa.Column('delta_xfp', sa.Numeric(6, 2), nullable=True),
        sa.Column('fit_score', sa.Numeric(5, 2), nullable=True),
        sa.Column('faab_suggestion', sa.Integer(), nullable=True),
        sa.Column('acquisition_prob', sa.Numeric(5, 2), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=func.now(), nullable=False),
        sa.ForeignKeyConstraint(['league_id'], ['leagues.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['player_id'], ['players.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('league_id', 'week', 'player_id', name='uq_waiver_candidates_league_week_player')
    )

    # Create streamer_signals table
    op.create_table('streamer_signals',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('week', sa.SmallInteger(), nullable=False),
        sa.Column('kind', sa.Text(), nullable=False),
        sa.Column('subject_id', sa.Integer(), nullable=False),
        sa.Column('fit_score', sa.Numeric(5, 2), nullable=True),
        sa.Column('weather_bucket', sa.SmallInteger(), nullable=True),
        sa.Column('meta', sa.JSON(), nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('week', 'kind', 'subject_id', name='uq_streamer_signals_week_kind_subject_id')
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

    # Add triggers to waiver_candidates and streamer_signals
    op.execute("""
    DROP TRIGGER IF EXISTS update_waiver_candidates_updated_at ON waiver_candidates;
    CREATE TRIGGER update_waiver_candidates_updated_at
    BEFORE UPDATE ON waiver_candidates
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
    """)

    op.execute("""
    DROP TRIGGER IF EXISTS update_streamer_signals_updated_at ON streamer_signals;
    CREATE TRIGGER update_streamer_signals_updated_at
    BEFORE UPDATE ON streamer_signals
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
    """)


def downgrade() -> None:
    # Remove triggers
    op.execute("DROP TRIGGER IF EXISTS update_streamer_signals_updated_at ON streamer_signals;")
    op.execute("DROP TRIGGER IF EXISTS update_waiver_candidates_updated_at ON waiver_candidates;")

    # Drop function
    op.execute("DROP FUNCTION IF EXISTS update_updated_at_column();")

    # Drop constraints
    op.drop_constraint('uq_streamer_signals_week_kind_subject_id', 'streamer_signals', type_='unique')
    op.drop_constraint('uq_waiver_candidates_league_week_player', 'waiver_candidates', type_='unique')

    # Drop tables
    op.drop_table('streamer_signals')
    op.drop_table('waiver_candidates')
