from sqlalchemy import text
from app.deps import SessionLocal


def test_db_connects():
    with SessionLocal() as s:
        assert s.execute(text("SELECT 1")).scalar() == 1
