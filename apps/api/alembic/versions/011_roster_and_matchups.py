"""Add roster_slots and matchups tables

Revision ID: 011
Revises: 010
Create Date: 2023-11-01 00:00:00.000000

"""

from alembic import op
import sqlalchemy as sa
from alembic import context
from sqlalchemy.sql import func

# Check if column exists
bind = op.get_bind()
insp = None
cols = []
try:
    insp = sa.inspect(bind)
    cols = [c["name"] for c in insp.get_columns("roster_slots")]
except Exception:
    cols = []

revision = "011"
down_revision = "010"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create roster_slots table
    op.create_table(
        "roster_slots",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("team_id", sa.Integer(), nullable=False),
        sa.Column("week", sa.SmallInteger(), nullable=False),
        sa.Column("slot", sa.Text(), nullable=False),  # Using 'slot' as per SPEC3
        sa.Column("player_id", sa.Integer(), nullable=True),
        sa.Column("projected_pts", sa.Numeric(6, 2), nullable=True),
        sa.Column("actual_pts", sa.Numeric(6, 2), nullable=True),
        sa.Column("is_starter", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["team_id"], ["teams.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["player_id"], ["players.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )

    # Add unique constraint if not exists
    exists = False
    try:
        # PostgreSQL-specific metadata check; in offline/sql generation bind may be a MockConnection
        exists = bool(
            bind.exec_driver_sql(
                "select 1 from pg_constraint where conname = 'uq_team_week_slot'"
            ).scalar()
        )
    except Exception:
        exists = False

    # If generating offline SQL for sqlite, emit a unique index instead of creating
    # an ALTER unique constraint which sqlite does not support in SQL generation.
    ctx = context.get_context()
    is_sql_mode = getattr(ctx, "as_sql", False)
    dialect_name = ctx.dialect.name if ctx.dialect is not None else None

    if not exists:
        if dialect_name == "sqlite" and is_sql_mode:
            op.create_index(
                "ix_roster_slots_team_week_slot",
                "roster_slots",
                ["team_id", "week", "slot"],
                unique=True,
            )
        else:
            op.create_unique_constraint(
                "uq_team_week_slot", "roster_slots", ["team_id", "week", "slot"]
            )

    op.create_index(
        "idx_roster_slots_team_week", "roster_slots", ["team_id", "week"], unique=False
    )

    # Create matchups table
    op.create_table(
        "matchups",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("league_id", sa.Integer(), nullable=False),
        sa.Column("week", sa.SmallInteger(), nullable=False),
        sa.Column("team_id", sa.Integer(), nullable=False),
        sa.Column("opponent_team_id", sa.Integer(), nullable=True),
        sa.Column("projected_pts", sa.Numeric(7, 2), nullable=True),
        sa.Column("actual_pts", sa.Numeric(7, 2), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["league_id"], ["leagues.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["team_id"], ["teams.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["opponent_team_id"], ["teams.id"], ondelete="SET NULL"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "league_id", "week", "team_id", name="uq_matchups_league_week_team"
        ),
    )
    op.create_index(
        "idx_matchups_league_week", "matchups", ["league_id", "week"], unique=False
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

    # Add triggers to roster_slots and matchups
    op.execute("""
    DROP TRIGGER IF EXISTS update_roster_slots_updated_at ON roster_slots;
    CREATE TRIGGER update_roster_slots_updated_at
    BEFORE UPDATE ON roster_slots
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
    """)

    op.execute("""
    DROP TRIGGER IF EXISTS update_matchups_updated_at ON matchups;
    CREATE TRIGGER update_matchups_updated_at
    BEFORE UPDATE ON matchups
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
    """)


def downgrade() -> None:
    # Remove triggers
    op.execute("DROP TRIGGER IF EXISTS update_matchups_updated_at ON matchups;")
    op.execute("DROP TRIGGER IF EXISTS update_roster_slots_updated_at ON roster_slots;")

    # Drop function
    op.execute("DROP FUNCTION IF EXISTS update_updated_at_column();")

    # Drop indexes
    op.drop_index("idx_matchups_league_week", table_name="matchups")
    op.drop_index("idx_roster_slots_team_week", table_name="roster_slots")

    # Drop constraints
    op.drop_constraint("uq_matchups_league_week_team", "matchups", type_="unique")
    op.drop_constraint("uq_team_week_slot", "roster_slots", type_="unique")

    # Drop tables
    op.drop_table("matchups")
    op.drop_table("roster_slots")
