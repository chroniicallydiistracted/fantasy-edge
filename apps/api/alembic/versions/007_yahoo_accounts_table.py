"""Add yahoo_accounts table and update oauth_tokens

Revision ID: 007
Revises: 006
Create Date: 2023-07-01 00:00:00.000000

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import func

# Check if column exists
bind = op.get_bind()
insp = None
cols = []
try:
    # In test contexts alembic may pass a MockConnection which SQLAlchemy
    # inspection cannot handle. Guard against that and assume no existing
    # columns when inspection isn't available.
    insp = sa.inspect(bind)
    cols = [c["name"] for c in insp.get_columns("oauth_tokens")]
except Exception:
    cols = []

revision = "007"
down_revision = "006"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add new columns to oauth_tokens if they don't exist
    if "access_token_enc" not in cols:
        op.add_column(
            "oauth_tokens", sa.Column("access_token_enc", sa.Text(), nullable=True)
        )

    if "refresh_token_enc" not in cols:
        op.add_column(
            "oauth_tokens", sa.Column("refresh_token_enc", sa.Text(), nullable=True)
        )

    if "access_expires_at" not in cols:
        op.add_column(
            "oauth_tokens",
            sa.Column("access_expires_at", sa.DateTime(timezone=True), nullable=True),
        )

    # Create yahoo_accounts table
    op.create_table(
        "yahoo_accounts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("yahoo_guid", sa.Text(), nullable=False),
        sa.Column("scope", sa.Text(), nullable=True),
        sa.Column("access_token_enc", sa.Text(), nullable=False),
        sa.Column("refresh_token_enc", sa.Text(), nullable=False),
        sa.Column("access_expires_at", sa.DateTime(timezone=True), nullable=False),
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
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", name="uq_yahoo_accounts_user_id"),
        sa.UniqueConstraint("yahoo_guid", name="uq_yahoo_accounts_yahoo_guid"),
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

    # Add trigger to yahoo_accounts
    op.execute("""
    DROP TRIGGER IF EXISTS update_yahoo_accounts_updated_at ON yahoo_accounts;
    CREATE TRIGGER update_yahoo_accounts_updated_at
    BEFORE UPDATE ON yahoo_accounts
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
    """)


def downgrade() -> None:
    # Remove trigger
    op.execute(
        "DROP TRIGGER IF EXISTS update_yahoo_accounts_updated_at ON yahoo_accounts;"
    )

    # Drop function
    op.execute("DROP FUNCTION IF EXISTS update_updated_at_column();")

    # Drop yahoo_accounts table
    op.drop_table("yahoo_accounts")

    # Remove new columns from oauth_tokens if they exist
    if "access_expires_at" in cols:
        op.drop_column("oauth_tokens", "access_expires_at")

    if "refresh_token_enc" in cols:
        op.drop_column("oauth_tokens", "refresh_token_enc")

    if "access_token_enc" in cols:
        op.drop_column("oauth_tokens", "access_token_enc")
