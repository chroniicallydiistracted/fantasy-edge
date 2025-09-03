"""Add jobs and job_runs tables for background processing

Revision ID: 015
Revises: 014
Create Date: 2024-03-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import func
import uuid

revision = '015'
down_revision = '014'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create jobs table
    op.create_table('jobs',
        sa.Column('id', sa.UUID(), nullable=False, default=uuid.uuid4),
        sa.Column('kind', sa.Text(), nullable=False),
        sa.Column('payload', sa.JSON(), nullable=False),
        sa.Column('not_before', sa.DateTime(timezone=True), nullable=True),
        sa.Column('attempts', sa.SmallInteger(), nullable=False, server_default='0'),
        sa.Column('status', sa.Text(), nullable=False, server_default='queued'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # Create job_runs table
    op.create_table('job_runs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('job_id', sa.UUID(), nullable=False),
        sa.Column('started_at', sa.DateTime(timezone=True), server_default=func.now(), nullable=False),
        sa.Column('finished_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('ok', sa.Boolean(), nullable=True),
        sa.Column('message', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['job_id'], ['jobs.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
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

    # Add trigger to jobs
    op.execute("""
    DROP TRIGGER IF EXISTS update_jobs_updated_at ON jobs;
    CREATE TRIGGER update_jobs_updated_at
    BEFORE UPDATE ON jobs
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
    """)


def downgrade() -> None:
    # Remove triggers
    op.execute("DROP TRIGGER IF EXISTS update_jobs_updated_at ON jobs;")

    # Drop function
    op.execute("DROP FUNCTION IF EXISTS update_updated_at_column();")

    # Drop tables
    op.drop_table('job_runs')
    op.drop_table('jobs')
