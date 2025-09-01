from dataclasses import dataclass

def bonus_bins(val, bins):
    return sum(1 for b in bins if val >= b)

@dataclass
class Statline:
    Comp: float = 0; Incomp: float = 0; PassYds: float = 0; PassTD: float = 0; INT: float = 0
    PickSix: float = 0; Pass1D: float = 0; RushYds: float = 0; RushTD: float = 0; Rush1D: float = 0
    Rec: float = 0; RecYds: float = 0; RecTD: float = 0; Rec1D: float = 0
    RetYds: float = 0; RetTD: float = 0; TwoPt: float = 0; FumblesLost: float = 0; OffFumRetTD: float = 0
    e40c: float = 0; e40ptd: float = 0; e40r: float = 0; e40rtd: float = 0; e40rec: float = 0; e40rectd: float = 0

def offense_points(s: Statline) -> float:
    return (
        0.25*s.Comp - 0.25*s.Incomp + s.PassYds/25 + 2*bonus_bins(s.PassYds,[300,400,500])
        + 6*s.PassTD - 2*s.INT + 2*s.e40c + 2*s.e40ptd + 0.5*s.Pass1D - 2*s.PickSix
        + s.RushYds/10 + 2*bonus_bins(s.RushYds,[100,150,200]) + 6*s.RushTD + 2*s.e40r + 2*s.e40rtd + 0.5*s.Rush1D
        + s.Rec + s.RecYds/10 + 2*bonus_bins(s.RecYds,[100,150,200]) + 6*s.RecTD + 2*s.e40rec + 2*s.e40rectd + 0.5*s.Rec1D
        + s.RetYds/30 + 6*s.RetTD + 2*s.TwoPt - 2*s.FumblesLost + 6*s.OffFumRetTD
    )
