import pytest
from alembic import command
import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.models import League, Team
from app.seed import seed_league


def test_migrations_upgrade(tmp_path):
    cfg = Config("alembic.ini")
    cfg.set_main_option("sqlalchemy.url", "sqlite://")
    cfg.attributes["configure_args"] = {"render_as_batch": True}
    command.upgrade(cfg, "head", sql=True)


def test_foreign_key_integrity(db_session):
    league = League(yahoo_id=1, name="Test")
    db_session.add(league)
    db_session.commit()
    with pytest.raises(IntegrityError):
        db_session.add(Team(league_id=999, name="Bad"))
        db_session.commit()
    db_session.rollback()


def test_unique_constraint(db_session):
    db_session.add(League(yahoo_id=2, name="A"))
    db_session.commit()
    db_session.add(League(yahoo_id=2, name="B"))
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_seed_idempotent(db_session):
    seed_league(db_session)
    seed_league(db_session)
    rows = db_session.execute(select(League).where(League.yahoo_id == 528886)).scalars().all()
    assert len(rows) == 1
