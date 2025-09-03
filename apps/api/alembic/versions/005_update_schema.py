"""Update schema with proper constraints and indexes

Revision ID: 005
Revises: 004
Create Date: 2025-09-03 00:00:00.000000

"""

from alembic import op
import sqlalchemy as sa
from alembic import context

revision = "005"
down_revision = "004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add missing constraints and indexes
    # Use batch_alter_table for SQLite where ALTER constraint is not supported.
    ctx = context.get_context()
    is_sql_mode = getattr(ctx, "as_sql", False)
    dialect_name = ctx.dialect.name if ctx.dialect is not None else None
    # When running in offline SQL generation, ctx.dialect may be None. If so and
    # we're generating SQL, infer sqlite from the configured URL to ensure we
    # emit compatible SQL for tests that set sqlalchemy.url=sqlite://
    if dialect_name is None and is_sql_mode:
        dialect_name = "sqlite"

    # When generating SQL (--sql), batch mode cannot reflect live tables, so emit
    # direct operations. When running against a live SQLite DB, use batch_alter_table.
    if dialect_name == "sqlite":
        if is_sql_mode:
            # when generating SQL for sqlite, emit unique indexes instead of ALTERing
            op.create_index("ix_leagues_yahoo_id", "leagues", ["yahoo_id"], unique=True)
            op.create_index(
                "ix_roster_slots_team_week_slot",
                "roster_slots",
                ["team_id", "week", "slot"],
                unique=True,
            )
            op.create_index(
                "ix_proj_player_week", "projections", ["player_id", "week"], unique=True
            )
            op.create_index(
                "ix_proj_week_player",
                "projections",
                ["week", "player_id"],
                unique=False,
            )
        else:
            # live sqlite DB: use batch_alter_table which will recreate the table
            with op.batch_alter_table("leagues") as batch_op:
                batch_op.create_unique_constraint("uq_league_yahoo_id", ["yahoo_id"])
            with op.batch_alter_table("roster_slots") as batch_op:
                batch_op.create_unique_constraint(
                    "uq_team_week_slot", ["team_id", "week", "slot"]
                )
            with op.batch_alter_table("projections") as batch_op:
                batch_op.create_unique_constraint(
                    "uq_proj_player_week", ["player_id", "week"]
                )
                batch_op.create_index(
                    "ix_proj_week_player", ["week", "player_id"], unique=False
                )
    else:
        # non-sqlite dialects
        op.create_unique_constraint("uq_league_yahoo_id", "leagues", ["yahoo_id"])
        op.create_unique_constraint(
            "uq_team_week_slot", "roster_slots", ["team_id", "week", "slot"]
        )
        op.create_unique_constraint(
            "uq_proj_player_week", "projections", ["player_id", "week"]
        )
        op.create_index(
            "ix_proj_week_player", "projections", ["week", "player_id"], unique=False
        )

    # Add missing columns to leagues table
    op.add_column("leagues", sa.Column("season", sa.Integer(), nullable=True))
    op.add_column("leagues", sa.Column("scoring_json", sa.JSON(), nullable=True))
    op.add_column(
        "leagues",
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=True,
        ),
    )

    # Add missing columns to teams table
    op.add_column("teams", sa.Column("team_key", sa.String(), nullable=True))
    op.add_column("teams", sa.Column("manager_guid", sa.String(), nullable=True))
    op.add_column("teams", sa.Column("logo_url", sa.Text(), nullable=True))

    # Add missing columns to roster_slots table
    op.add_column(
        "roster_slots",
        sa.Column("is_starter", sa.Boolean(), default=True, nullable=False),
    )
    op.add_column("roster_slots", sa.Column("source", sa.String(), nullable=True))

    # Add missing columns to projections table
    op.add_column(
        "projections",
        sa.Column(
            "computed_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )


def downgrade() -> None:
    # Remove added columns
    op.drop_column("projections", "computed_at")
    op.drop_column("roster_slots", "source")
    op.drop_column("roster_slots", "is_starter")
    op.drop_column("teams", "logo_url")
    op.drop_column("teams", "manager_guid")
    op.drop_column("teams", "team_key")
    op.drop_column("leagues", "updated_at")
    op.drop_column("leagues", "scoring_json")
    op.drop_column("leagues", "season")

    # Remove constraints and indexes
    ctx = context.get_context()
    is_sql_mode = getattr(ctx, "as_sql", False)
    dialect_name = ctx.dialect.name if ctx.dialect is not None else None

    if dialect_name == "sqlite":
        if is_sql_mode:
            # drop indexes emitted in offline SQL mode
            op.drop_index("ix_proj_week_player")
            op.drop_index("ix_proj_player_week")
            op.drop_index("ix_roster_slots_team_week_slot")
            op.drop_index("ix_leagues_yahoo_id")
        else:
            with op.batch_alter_table("projections") as batch_op:
                batch_op.drop_index("ix_proj_week_player")
                batch_op.drop_constraint("uq_proj_player_week")
            with op.batch_alter_table("roster_slots") as batch_op:
                batch_op.drop_constraint("uq_team_week_slot")
            with op.batch_alter_table("leagues") as batch_op:
                batch_op.drop_constraint("uq_league_yahoo_id")
    else:
        op.drop_index("ix_proj_week_player")
        op.drop_constraint("uq_proj_player_week", "projections")
        op.drop_constraint("uq_team_week_slot", "roster_slots")
        op.drop_constraint("uq_league_yahoo_id", "leagues")
