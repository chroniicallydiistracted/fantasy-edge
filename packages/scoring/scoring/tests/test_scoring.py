from scoring import (
    OffenseStatline,
    KickerStatline,
    DefenseStatline,
    IDPStatline,
    offense_points,
    kicker_points,
    defense_points,
    idp_points,
)


def test_offense_qb_bonus_and_penalties():
    s = OffenseStatline(
        Comp=25,
        Incomp=15,
        PassYds=405,
        PassTD=3,
        INT=1,
        PickSix=1,
        Pass1D=12,
    )
    pts = offense_points(s)
    expected = 0.25 * 25 - 0.25 * 15 + 405 / 25 + 2 * 2 + 6 * 3 - 2 - 2 + 0.5 * 12
    assert round(pts, 2) == round(expected, 2)


def test_offense_rb_rush_and_rec_bonus():
    s = OffenseStatline(
        RushYds=150,
        RushTD=1,
        Rush1D=8,
        Rec=4,
        RecYds=50,
        Rec1D=3,
    )
    pts = offense_points(s)
    expected = (
        150 / 10
        + 2 * 2  # 100 and 150 yard bonuses
        + 6
        + 0.5 * 8
        + 4
        + 50 / 10
        + 0.5 * 3
    )
    assert round(pts, 2) == round(expected, 2)


def test_offense_wr_big_play_and_returns():
    s = OffenseStatline(
        Rec=7,
        RecYds=120,
        RecTD=1,
        Rec1D=5,
        e40rec=1,
        e40rectd=1,
        RetYds=90,
        RetTD=1,
    )
    pts = offense_points(s)
    expected = (
        7 + 120 / 10 + 2 + 6 + 2 * 1 + 2 * 1 + 0.5 * 5 + 90 / 30 + 6  # 100 yard bonus
    )
    assert round(pts, 2) == round(expected, 2)


def test_kicker_perfect_day():
    s = KickerStatline(FG0_39=2, FG40_49=1, FG50_59=1, PAT=3)
    pts = kicker_points(s)
    expected = 3 * 2 + 4 * 1 + 5 * 1 + 3 * 1
    assert pts == expected


def test_kicker_with_misses():
    s = KickerStatline(
        FG40_49=2,
        FG50_59=1,
        FGMiss40_49=1,
        FGMiss50_59=1,
        PAT=2,
        PATMiss=1,
    )
    pts = kicker_points(s)
    expected = 4 * 2 + 5 * 1 + 2 - 1 - 1 - 1
    assert pts == expected


def test_kicker_long_range():
    s = KickerStatline(FG60=1, FG50_59=1, FGMiss0_39=1)
    pts = kicker_points(s)
    expected = 6 * 1 + 5 * 1 - 1
    assert pts == expected


def test_defense_shutout():
    s = DefenseStatline(PtsAllow=0, Sack=3, INT=2, FumRec=1)
    pts = defense_points(s)
    expected = 3 + 2 * 2 + 2 * 1 + 10
    assert pts == expected


def test_defense_mid_points_allowed():
    s = DefenseStatline(PtsAllow=17, Sack=2, TD=1, RetYds=60)
    pts = defense_points(s)
    expected = 2 + 6 + 60 / 30 + 1
    assert pts == expected


def test_defense_high_points_allowed():
    s = DefenseStatline(
        PtsAllow=38,
        Sack=1,
        Safety=1,
        BlkKick=1,
        RetTD=1,
    )
    pts = defense_points(s)
    expected = 1 + 2 * 1 + 2 * 1 + 6 * 1 - 4
    assert pts == expected


def test_idp_linebacker():
    s = IDPStatline(
        TackleSolo=8,
        TackleAst=4,
        Sack=1,
        FumForce=1,
        FumRec=1,
    )
    pts = idp_points(s)
    expected = 1.5 * 8 + 0.75 * 4 + 4 * 1 + 2 * 1 + 2 * 1
    assert pts == expected


def test_idp_db_big_play():
    s = IDPStatline(
        TackleSolo=5,
        INT=1,
        TD=1,
        PassDef=2,
        RetYds=30,
    )
    pts = idp_points(s)
    expected = 1.5 * 5 + 3 * 1 + 6 * 1 + 1.5 * 2 + 30 / 30
    assert pts == expected


def test_idp_dl_safety():
    s = IDPStatline(TackleSolo=3, Sack=2, Safety=1)
    pts = idp_points(s)
    expected = 1.5 * 3 + 4 * 2 + 2 * 1
    assert pts == expected
