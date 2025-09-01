from optimizer import optimize_lineup


def test_optimize_lineup_basic():
    players = [
        {"id": "p1", "positions": ["QB"], "points": 20},
        {"id": "p2", "positions": ["RB"], "points": 12},
        {"id": "p3", "positions": ["RB"], "points": 10},
        {"id": "p4", "positions": ["WR"], "points": 18},
        {"id": "p5", "positions": ["WR"], "points": 15},
        {"id": "p6", "positions": ["TE"], "points": 8},
        {"id": "p7", "positions": ["RB", "WR"], "points": 14},
        {"id": "p8", "positions": ["WR"], "points": 13},
        {"id": "p9", "positions": ["RB"], "points": 9},
        {"id": "p10", "positions": ["DST"], "points": 5},
        {"id": "p11", "positions": ["K"], "points": 7},
    ]
    slots = ["QB", "RB", "RB", "WR", "WR", "TE", "FLEX", "DST", "K"]
    lineup, total = optimize_lineup(players, slots)
    assert lineup == ["p1", "p2", "p7", "p4", "p5", "p6", "p8", "p10", "p11"]
    assert total == 112

def test_optimize_lineup_invalid():
    players = [{"id": "p1", "positions": ["QB"], "points": 20}]
    slots = ["QB", "RB"]
    try:
        optimize_lineup(players, slots)
    except ValueError:
        assert True
    else:
        assert False, "expected ValueError"
