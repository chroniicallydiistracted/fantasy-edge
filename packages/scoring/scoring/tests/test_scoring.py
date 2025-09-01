from scoring.league_scoring import Statline, offense_points

def test_qb_bonus_and_penalties():
    s = Statline(Comp=25, Incomp=15, PassYds=405, PassTD=3, INT=1, PickSix=1, Pass1D=12)
    pts = offense_points(s)
    expected = 0.25*25 - 0.25*15 + 405/25 + 2*2 + 6*3 - 2 - 2 + 0.5*12
    assert round(pts, 2) == round(expected, 2)
