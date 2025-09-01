from __future__ import annotations

from dataclasses import asdict
from typing import Dict, Tuple

from scoring import OffenseStatline, offense_points


def project_offense(
    baselines: Dict[str, float], proe: float, waf: float
) -> Tuple[Dict[str, float], float]:
    """Simple offense projection using baseline rates, PROE, and weather."""
    pass_att = baselines.get("pass_attempts", 0) * (1 + proe) * waf
    comp_rate = baselines.get("comp_rate", 0.65)
    completions = pass_att * comp_rate
    pass_yds = pass_att * baselines.get("yards_per_attempt", 7) * waf
    pass_td = pass_att * baselines.get("td_rate", 0.05)
    interceptions = pass_att * baselines.get("int_rate", 0.02)

    rush_att = baselines.get("rush_attempts", 0) * waf
    rush_yds = rush_att * baselines.get("yards_per_rush", 4)
    rush_td = rush_att * baselines.get("rush_td_rate", 0.02)

    targets = baselines.get("targets", 0) * (1 + proe) * waf
    catch_rate = baselines.get("catch_rate", 0.6)
    receptions = targets * catch_rate
    rec_yds = receptions * baselines.get("yards_per_rec", 10) * waf
    rec_td = receptions * baselines.get("rec_td_rate", 0.05)

    stat = OffenseStatline(
        Comp=completions,
        Incomp=max(pass_att - completions, 0),
        PassYds=pass_yds,
        PassTD=pass_td,
        INT=interceptions,
        RushYds=rush_yds,
        RushTD=rush_td,
        Rec=receptions,
        RecYds=rec_yds,
        RecTD=rec_td,
    )
    points = offense_points(stat)
    return asdict(stat), points
