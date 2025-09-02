"""Update schema with proper constraints and indexes

Revision ID: 005
Revises: 004
Create Date: 2025-09-03 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = '005'
down_revision = '004'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add missing constraints and indexes
    op.create_unique_constraint("uq_league_yahoo_id", "leagues", ["yahoo_id"])
    op.create_unique_constraint("uq_team_week_slot", "roster_slots", ["team_id", "week", "slot"])
    op.create_unique_constraint("uq_proj_player_week", "projections", ["player_id", "week"])
    op.create_index("ix_proj_week_player", "projections", ["week", "player_id"], unique=False)

    # Add missing columns to leagues table
    op.add_column('leagues', sa.Column('season', sa.Integer(), nullable=True))
    op.add_column('leagues', sa.Column('scoring_json', sa.JSON(), nullable=True))
    op.add_column('leagues', sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True))

    # Add missing columns to teams table
    op.add_column('teams', sa.Column('team_key', sa.String(), nullable=True))
    op.add_column('teams', sa.Column('manager_guid', sa.String(), nullable=True))
    op.add_column('teams', sa.Column('logo_url', sa.Text(), nullable=True))

    # Add missing columns to roster_slots table
    op.add_column('roster_slots', sa.Column('is_starter', sa.Boolean(), default=True, nullable=False))
    op.add_column('roster_slots', sa.Column('source', sa.String(), nullable=True))

    # Add missing columns to projections table
    op.add_column('projections', sa.Column('computed_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False))


def downgrade() -> None:
    # Remove added columns
    op.drop_column('projections', 'computed_at')
    op.drop_column('roster_slots', 'source')
    op.drop_column('roster_slots', 'is_starter')
    op.drop_column('teams', 'logo_url')
    op.drop_column('teams', 'manager_guid')
    op.drop_column('teams', 'team_key')
    op.drop_column('leagues', 'updated_at')
    op.drop_column('leagues', 'scoring_json')
    op.drop_column('leagues', 'season')

    # Remove constraints and indexes
    op.drop_index("ix_proj_week_player")
    op.drop_constraint("uq_proj_player_week", "projections")
    op.drop_constraint("uq_team_week_slot", "roster_slots")
    op.drop_constraint("uq_league_yahoo_id", "leagues")
