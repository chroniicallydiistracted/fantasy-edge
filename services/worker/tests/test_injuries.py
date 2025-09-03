from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
import pytest

from tasks import ingest_injuries_from_csv

try:
    from app.models import Base, Injury, Player, PlayerLink  # type: ignore[import-not-found]
except Exception:

    pytest.skip("injury models not available", allow_module_level=True)


def setup_db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)()


def test_ingest_injuries(tmp_path):
    session: Session = setup_db()

    player = Player(id=1, name="Test", position="QB")
    link = PlayerLink(player_id=1, gsis_id="00-000001")
    session.add_all([player, link])
    session.commit()

    csv_path = tmp_path / "injuries.csv"
    csv_path.write_text(
        "gsis_id,status,report_date\n00-000001,Questionable,2023-01-01T00:00:00Z\n"
    )

    count = ingest_injuries_from_csv(csv_path, session)
    assert count == 1
    injury = session.query(Injury).one()
    assert injury.status == "Questionable"
    assert injury.report_time.isoformat().startswith("2023-01-01")
