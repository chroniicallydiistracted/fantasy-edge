from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from tasks import waiver_shortlist_sync
from app.models import Base, League, Team, Player, RosterSlot, Projection


def setup_db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)()


def test_waiver_shortlist_sync_orders_and_ties():
    session = setup_db()
    league = League(id=1, yahoo_id=1, name="L")
    team = Team(id=1, league=league, name="T")
    session.add_all([league, team])
    session.add_all(
        [Player(id=1, name="Starter"), Player(id=2, name="FA1"), Player(id=3, name="FA2")]
    )
    session.add(RosterSlot(team_id=1, player_id=1, week=1))
    session.add_all(
        [
            Projection(player_id=1, week=1, projected_points=5, data={}),
            Projection(player_id=2, week=1, projected_points=7, data={}),
            Projection(player_id=3, week=1, projected_points=7, data={}),
        ]
    )
    session.commit()

    result = waiver_shortlist_sync(session, league_id=1, week=1, horizon=1)
    waivers = result[1]
    assert [w["player_id"] for w in waivers] == [2, 3]
    assert waivers[0]["delta_xfp"] == waivers[1]["delta_xfp"] == 2
    assert [w["order"] for w in waivers] == [1, 2]

