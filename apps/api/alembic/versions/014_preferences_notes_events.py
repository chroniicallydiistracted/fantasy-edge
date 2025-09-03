"""Add user_preferences, notes, and event_log tables

Revision ID: 014
Revises: 013
Create Date: 2024-02-01 00:00:00.000000

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import func

revision = "014"
down_revision = "013"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create user_preferences table
    op.create_table(
        "user_preferences",
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("theme", sa.Text(), nullable=False, server_default="system"),
        sa.Column("saved_views", sa.JSON(), nullable=False, server_default="{}"),
        # Use JSON for pinned_players to be portable across dialects (SQLite offline SQL)
        sa.Column("pinned_players", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("user_id"),
    )

    # Create notes table
    op.create_table(
        "notes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("player_id", sa.Integer(), nullable=False),
        sa.Column("note", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["player_id"], ["players.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "idx_notes_user_player", "notes", ["user_id", "player_id"], unique=False
    )

    # Create event_log table
    op.create_table(
        "event_log",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "ts", sa.DateTime(timezone=True), server_default=func.now(), nullable=False
        ),
        sa.Column("type", sa.Text(), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_event_log_ts", "event_log", ["ts"], unique=False)

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

    # Add triggers to user_preferences
    op.execute("""
    DROP TRIGGER IF EXISTS update_user_preferences_updated_at ON user_preferences;
    CREATE TRIGGER update_user_preferences_updated_at
    BEFORE UPDATE ON user_preferences
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
    """)


def downgrade() -> None:
    # Remove triggers
    op.execute(
        "DROP TRIGGER IF EXISTS update_user_preferences_updated_at ON user_preferences;"
    )

    # Drop function
    op.execute("DROP FUNCTION IF EXISTS update_updated_at_column();")

    # Drop indexes
    op.drop_index("idx_event_log_ts", table_name="event_log")
    op.drop_index("idx_notes_user_player", table_name="notes")

    # Drop tables
    op.drop_table("event_log")
    op.drop_table("notes")
    op.drop_table("user_preferences")
