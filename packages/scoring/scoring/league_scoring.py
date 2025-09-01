from dataclasses import dataclass


def bonus_bins(val, bins):
    return sum(1 for b in bins if val >= b)


@dataclass
class OffenseStatline:
    Comp: float = 0
    Incomp: float = 0
    PassYds: float = 0
    PassTD: float = 0
    INT: float = 0
    PickSix: float = 0
    Pass1D: float = 0
    RushYds: float = 0
    RushTD: float = 0
    Rush1D: float = 0
    Rec: float = 0
    RecYds: float = 0
    RecTD: float = 0
    Rec1D: float = 0
    RetYds: float = 0
    RetTD: float = 0
    TwoPt: float = 0
    FumblesLost: float = 0
    OffFumRetTD: float = 0
    e40c: float = 0
    e40ptd: float = 0
    e40r: float = 0
    e40rtd: float = 0
    e40rec: float = 0
    e40rectd: float = 0


def offense_points(s: OffenseStatline) -> float:
    return (
        0.25 * s.Comp
        - 0.25 * s.Incomp
        + s.PassYds / 25
        + 2 * bonus_bins(s.PassYds, [300, 400, 500])
        + 6 * s.PassTD
        - 2 * s.INT
        + 2 * s.e40c
        + 2 * s.e40ptd
        + 0.5 * s.Pass1D
        - 2 * s.PickSix
        + s.RushYds / 10
        + 2 * bonus_bins(s.RushYds, [100, 150, 200])
        + 6 * s.RushTD
        + 2 * s.e40r
        + 2 * s.e40rtd
        + 0.5 * s.Rush1D
        + s.Rec
        + s.RecYds / 10
        + 2 * bonus_bins(s.RecYds, [100, 150, 200])
        + 6 * s.RecTD
        + 2 * s.e40rec
        + 2 * s.e40rectd
        + 0.5 * s.Rec1D
        + s.RetYds / 30
        + 6 * s.RetTD
        + 2 * s.TwoPt
        - 2 * s.FumblesLost
        + 6 * s.OffFumRetTD
    )


@dataclass
class KickerStatline:
    FG0_39: float = 0
    FG40_49: float = 0
    FG50_59: float = 0
    FG60: float = 0
    FGMiss0_39: float = 0
    FGMiss40_49: float = 0
    FGMiss50_59: float = 0
    FGMiss60: float = 0
    PAT: float = 0
    PATMiss: float = 0


def kicker_points(s: KickerStatline) -> float:
    return (
        3 * s.FG0_39
        + 4 * s.FG40_49
        + 5 * s.FG50_59
        + 6 * s.FG60
        + 1 * s.PAT
        - s.FGMiss0_39
        - s.FGMiss40_49
        - s.FGMiss50_59
        - s.FGMiss60
        - s.PATMiss
    )


@dataclass
class DefenseStatline:
    Sack: float = 0
    INT: float = 0
    FumRec: float = 0
    Safety: float = 0
    TD: float = 0
    BlkKick: float = 0
    PtsAllow: float = 0
    RetYds: float = 0
    RetTD: float = 0


def defense_points_allowed(pa: float) -> float:
    if pa == 0:
        return 10
    if 1 <= pa <= 6:
        return 7
    if 7 <= pa <= 13:
        return 4
    if 14 <= pa <= 20:
        return 1
    if 21 <= pa <= 27:
        return 0
    if 28 <= pa <= 34:
        return -1
    return -4


def defense_points(s: DefenseStatline) -> float:
    return (
        s.Sack
        + 2 * s.INT
        + 2 * s.FumRec
        + 2 * s.Safety
        + 6 * s.TD
        + 2 * s.BlkKick
        + s.RetYds / 30
        + 6 * s.RetTD
        + defense_points_allowed(s.PtsAllow)
    )


@dataclass
class IDPStatline:
    TackleSolo: float = 0
    TackleAst: float = 0
    Sack: float = 0
    INT: float = 0
    FumForce: float = 0
    FumRec: float = 0
    Safety: float = 0
    TD: float = 0
    PassDef: float = 0
    RetYds: float = 0
    RetTD: float = 0


def idp_points(s: IDPStatline) -> float:
    return (
        1.5 * s.TackleSolo
        + 0.75 * s.TackleAst
        + 4 * s.Sack
        + 3 * s.INT
        + 2 * s.FumForce
        + 2 * s.FumRec
        + 2 * s.Safety
        + 6 * s.TD
        + 1.5 * s.PassDef
        + s.RetYds / 30
        + 6 * s.RetTD
    )
