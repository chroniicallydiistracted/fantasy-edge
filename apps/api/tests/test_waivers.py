from app.models import League, Team, Player, RosterSlot, Projection, User
from app.settings import settings


def _auth_client(client, db_session):
    user = User(email=None)
    db_session.add(user)
    db_session.commit()
    original = settings.allow_debug_user
    settings.allow_debug_user = True
    client.get("/auth/session/debug", headers={"X-Debug-User": str(user.id)})
    settings.allow_debug_user = original
    return user


def test_team_waivers_sorted_and_tied(client, db_session):
    _auth_client(client, db_session)
    db_session.query(Projection).delete()
    db_session.query(RosterSlot).delete()
    db_session.query(Player).delete()
    db_session.query(Team).delete()
    db_session.query(League).delete()
    league = League(id=99, yahoo_id=99, name="L")
    team = Team(id=99, league=league, name="T")
    db_session.add_all([league, team])
    players = [
        Player(id=100, name="Starter"),
        Player(id=101, name="FA1"),
        Player(id=102, name="FA2"),
    ]
    db_session.add_all(players)
    db_session.add(RosterSlot(team_id=99, player_id=100, week=1))
    projections = [
        Projection(player_id=100, week=1, projected_points=5, data={}),
        Projection(player_id=101, week=1, projected_points=7, data={}),
        Projection(player_id=102, week=1, projected_points=7, data={}),
    ]
    db_session.add_all(projections)
    db_session.commit()

    resp = client.get("/team/99/waivers", params={"week": 1, "horizon": 2})
    assert resp.status_code == 200
    waivers = resp.json()["waivers"]
    assert [w["player_id"] for w in waivers] == [101, 102]
    assert waivers[0]["delta_xfp"] == waivers[1]["delta_xfp"] == 2
    assert [w["order"] for w in waivers] == [1, 2]


def test_streamers_endpoints(client, db_session):
    _auth_client(client, db_session)
    players = [
        Player(id=4, name="D1", position="DEF"),
        Player(id=5, name="D2", position="DEF"),
        Player(id=6, name="I1", position="IDP"),
        Player(id=7, name="I2", position="IDP"),
    ]
    projections = [
        Projection(player_id=4, week=1, projected_points=5, data={}),
        Projection(player_id=5, week=1, projected_points=8, data={}),
        Projection(player_id=6, week=1, projected_points=2, data={}),
        Projection(player_id=7, week=1, projected_points=3, data={}),
    ]
    db_session.add_all(players + projections)
    db_session.commit()

    resp = client.get("/streamers/def", params={"week": 1})
    assert resp.status_code == 200
    body = resp.json()
    assert [r["player_id"] for r in body] == [5, 4]

    resp = client.get("/streamers/idp", params={"week": 1})
    assert resp.status_code == 200
    body = resp.json()
    assert [r["player_id"] for r in body] == [7, 6]
