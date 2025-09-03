from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pytest

from tasks import generate_projections

try:
    from app.models import Base, Baseline, Player, Projection, Weather  # type: ignore[import-not-found]
except Exception:
    pytest.skip("app models not available", allow_module_level=True)


def setup_db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)()


def test_generate_projections_inserts_rows():
    session = setup_db()
    player = Player(id=1, name="Tester", position="QB")
    session.add(player)
    session.commit()
    baselines = [
        Baseline(player_id=1, metric="pass_attempts", value=30),
        Baseline(player_id=1, metric="yards_per_attempt", value=7),
        Baseline(player_id=1, metric="td_rate", value=0.05),
        Baseline(player_id=1, metric="int_rate", value=0.02),
        Baseline(player_id=1, metric="rush_attempts", value=5),
        Baseline(player_id=1, metric="yards_per_rush", value=4),
        Baseline(player_id=1, metric="rush_td_rate", value=0.02),
        Baseline(player_id=1, metric="proe", value=0.1),
    ]
    session.add_all(baselines)
    session.add(Weather(game_id="1-1", waf=0.8))
    session.commit()

    count = generate_projections(session, week=1)
    assert count == 1
    proj = session.query(Projection).filter_by(player_id=1, week=1).one()
    assert proj.projected_points > 0
    assert proj.variance and proj.variance > 0
    assert proj.data["PassYds"] > 0
