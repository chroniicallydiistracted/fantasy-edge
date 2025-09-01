"""Lineup optimization utilities."""

from __future__ import annotations

from typing import Any, Iterable, List, Mapping, Sequence, Tuple, Set, cast

Player = Mapping[str, object]


def optimize_lineup(
    players: Sequence[Player], roster_slots: Sequence[str]
) -> Tuple[List[str], float]:
    """Return the optimal lineup and total projected points.

    Parameters
    ----------
    players: Sequence[Player]
        Players with ``id``, ``positions`` (iterable of str), and ``points``.
    roster_slots: Sequence[str]
        Slots to fill, e.g., ["QB", "RB", "RB", "WR", "WR", "TE", "FLEX", "DST", "K"].

    Returns
    -------
    Tuple[List[str], float]
        A tuple of player ids in the same order as ``roster_slots`` and the
        total projected points.
    """

    best_lineup: List[str] = []
    best_score = float("-inf")

    eligibility = {"FLEX": {"RB", "WR", "TE"}}

    def backtrack(idx: int, used: Set[int], current: List[str], score: float) -> None:
        nonlocal best_lineup, best_score
        if idx == len(roster_slots):
            if score > best_score:
                best_score = score
                best_lineup = current.copy()
            return
        slot = roster_slots[idx]
        allowed = eligibility.get(slot, {slot})
        for i, p in enumerate(players):
            if i in used:
                continue
            positions = cast(Iterable[str], p.get("positions", []))
            p_positions = set(positions)
            if not allowed.intersection(p_positions):
                continue
            used.add(i)
            current.append(str(p.get("id")))
            points = cast(Any, p.get("points", 0))
            backtrack(idx + 1, used, current, score + float(points))
            current.pop()
            used.remove(i)

    backtrack(0, set(), [], 0.0)
    if best_score == float("-inf"):
        raise ValueError("no valid lineup")
    return best_lineup, best_score
