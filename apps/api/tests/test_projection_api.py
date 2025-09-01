from app.models import User, Player, Projection
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


def test_get_projection(client, db_session):
    _auth_client(client, db_session)
    player = Player(id=1, name="Tester")
    proj = Projection(
        player_id=1,
        week=1,
        projected_points=12.3,
        variance=1.2,
        data={"PassYds": 100},
    )
    db_session.add_all([player, proj])
    db_session.commit()
    resp = client.get("/players/1/projection", params={"week": 1})
    assert resp.status_code == 200
    body = resp.json()
    assert body["projected_points"] == 12.3
    assert body["data"]["PassYds"] == 100


def test_projection_not_found(client, db_session):
    _auth_client(client, db_session)
    resp = client.get("/players/999/projection", params={"week": 1})
    assert resp.status_code == 404
