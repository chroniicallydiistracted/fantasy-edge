"""Add sessions table and update users table

Revision ID: 006
Revises: 005
Create Date: 2023-06-01 00:00:00.000000

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import func

revision = "006"
down_revision = "005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create sessions table
    op.create_table(
        "sessions",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=func.now(),
            nullable=False,
        ),
        sa.Column(
            "last_seen_at",
            sa.DateTime(timezone=True),
            server_default=func.now(),
            nullable=False,
        ),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("user_agent", sa.Text(), nullable=True),
        # Use a portable string column for IP addresses to support SQLite/offline SQL
        sa.Column("ip_addr", sa.String(length=45), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "idx_sessions_user_expires", "sessions", ["user_id", "expires_at"], unique=False
    )

    # Add columns to users table
    op.add_column("users", sa.Column("yahoo_guid", sa.Text(), nullable=True))
    op.add_column("users", sa.Column("display_name", sa.Text(), nullable=True))
    op.add_column("users", sa.Column("avatar_url", sa.Text(), nullable=True))

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

    # Add trigger to all tables with updated_at column
    tables_with_updated_at = [
        "users",
        "oauth_tokens",
        "leagues",
        "teams",
        "players",
        "roster_slots",
        "projections",
    ]

    for table in tables_with_updated_at:
        op.execute(f"""
        DROP TRIGGER IF EXISTS update_{table}_updated_at ON {table};
        CREATE TRIGGER update_{table}_updated_at
        BEFORE UPDATE ON {table}
        FOR EACH ROW
        EXECUTE FUNCTION update_updated_at_column();
        """)


def downgrade() -> None:
    # Remove triggers
    tables_with_updated_at = [
        "users",
        "oauth_tokens",
        "leagues",
        "teams",
        "players",
        "roster_slots",
        "projections",
    ]

    for table in tables_with_updated_at:
        op.execute(f"DROP TRIGGER IF EXISTS update_{table}_updated_at ON {table};")

    # Drop function
    op.execute("DROP FUNCTION IF EXISTS update_updated_at_column();")

    # Drop sessions table
    op.drop_index("idx_sessions_user_expires", table_name="sessions")
    op.drop_table("sessions")

    # Remove columns from users table
    op.drop_column("users", "avatar_url")
    op.drop_column("users", "display_name")
    op.drop_column("users", "yahoo_guid")
