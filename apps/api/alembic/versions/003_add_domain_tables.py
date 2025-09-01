"""Add domain tables

Revision ID: 003
Revises: 002
Create Date: 2023-01-01 07:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'leagues',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('yahoo_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('yahoo_id'),
    )
    op.create_index(op.f('ix_leagues_id'), 'leagues', ['id'], unique=False)
    op.create_index(op.f('ix_leagues_yahoo_id'), 'leagues', ['yahoo_id'], unique=True)

    op.create_table(
        'teams',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('league_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('yahoo_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['league_id'], ['leagues.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_teams_id'), 'teams', ['id'], unique=False)

    op.create_table(
        'players',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('position', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_players_id'), 'players', ['id'], unique=False)

    op.create_table(
        'player_links',
        sa.Column('player_id', sa.Integer(), nullable=False),
        sa.Column('yahoo_key', sa.String(), nullable=True),
        sa.Column('gsis_id', sa.String(), nullable=True),
        sa.Column('pfr_id', sa.String(), nullable=True),
        sa.Column('last_manual_override', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.ForeignKeyConstraint(['player_id'], ['players.id']),
        sa.PrimaryKeyConstraint('player_id'),
        sa.UniqueConstraint('yahoo_key'),
        sa.UniqueConstraint('gsis_id'),
        sa.UniqueConstraint('pfr_id'),
    )
    op.create_index(op.f('ix_player_links_gsis_id'), 'player_links', ['gsis_id'], unique=True)
    op.create_index(op.f('ix_player_links_pfr_id'), 'player_links', ['pfr_id'], unique=True)
    op.create_index(op.f('ix_player_links_yahoo_key'), 'player_links', ['yahoo_key'], unique=True)

    op.create_table(
        'baselines',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('player_id', sa.Integer(), nullable=False),
        sa.Column('metric', sa.String(), nullable=False),
        sa.Column('value', sa.Float(), nullable=False),
        sa.ForeignKeyConstraint(['player_id'], ['players.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_baselines_id'), 'baselines', ['id'], unique=False)

    op.create_table(
        'injuries',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('player_id', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('report_time', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['player_id'], ['players.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_injuries_id'), 'injuries', ['id'], unique=False)

    op.create_table(
        'projections',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('player_id', sa.Integer(), nullable=False),
        sa.Column('week', sa.Integer(), nullable=False),
        sa.Column('projected_points', sa.Float(), nullable=False),
        sa.ForeignKeyConstraint(['player_id'], ['players.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_projections_id'), 'projections', ['id'], unique=False)

    op.create_table(
        'recommendations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('player_id', sa.Integer(), nullable=False),
        sa.Column('recommendation', sa.String(), nullable=False),
        sa.Column('reason', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['player_id'], ['players.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_recommendations_id'), 'recommendations', ['id'], unique=False)

    op.create_table(
        'roster_slots',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('team_id', sa.Integer(), nullable=False),
        sa.Column('player_id', sa.Integer(), nullable=False),
        sa.Column('week', sa.Integer(), nullable=False),
        sa.Column('position', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['player_id'], ['players.id']),
        sa.ForeignKeyConstraint(['team_id'], ['teams.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_roster_slots_id'), 'roster_slots', ['id'], unique=False)

    op.create_table(
        'weather',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('game_id', sa.String(), nullable=False),
        sa.Column('waf', sa.Float(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('game_id'),
    )
    op.create_index(op.f('ix_weather_game_id'), 'weather', ['game_id'], unique=True)
    op.create_index(op.f('ix_weather_id'), 'weather', ['id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_weather_id'), table_name='weather')
    op.drop_index(op.f('ix_weather_game_id'), table_name='weather')
    op.drop_table('weather')
    op.drop_index(op.f('ix_roster_slots_id'), table_name='roster_slots')
    op.drop_table('roster_slots')
    op.drop_index(op.f('ix_recommendations_id'), table_name='recommendations')
    op.drop_table('recommendations')
    op.drop_index(op.f('ix_projections_id'), table_name='projections')
    op.drop_table('projections')
    op.drop_index(op.f('ix_injuries_id'), table_name='injuries')
    op.drop_table('injuries')
    op.drop_index(op.f('ix_baselines_id'), table_name='baselines')
    op.drop_table('baselines')
    op.drop_index(op.f('ix_player_links_yahoo_key'), table_name='player_links')
    op.drop_index(op.f('ix_player_links_pfr_id'), table_name='player_links')
    op.drop_index(op.f('ix_player_links_gsis_id'), table_name='player_links')
    op.drop_table('player_links')
    op.drop_index(op.f('ix_players_id'), table_name='players')
    op.drop_table('players')
    op.drop_index(op.f('ix_teams_id'), table_name='teams')
    op.drop_table('teams')
    op.drop_index(op.f('ix_leagues_yahoo_id'), table_name='leagues')
    op.drop_index(op.f('ix_leagues_id'), table_name='leagues')
    op.drop_table('leagues')
