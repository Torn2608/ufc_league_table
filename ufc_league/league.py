"""The League: an ordered ladder of fighters (champion first) and results."""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass, field

from ufc_league.models import Fight, Fighter, LeagueError


def normalise(text: str) -> str:
    """Lower-case text and squeeze spaces so names match in any case."""
    return " ".join(text.lower().split())


@dataclass
class League:
    """Fighters in ranking order: index 0 is the champion, 1 is rank #1, ...

    Rule for new results: if a lower-ranked fighter beats a higher-ranked one,
    the two swap places. Draws and expected results leave the order alone.
    """

    title: str = "UFC Lightweight (155 lb)"
    as_of: str = ""
    fighters: list[Fighter] = field(default_factory=list)
    fights: list[Fight] = field(default_factory=list)
    notices: list[str] = field(default_factory=list, repr=False)

    @property
    def champion(self) -> Fighter:
        """Return the champion (position 0)."""
        if not self.fighters:
            raise LeagueError("The league has no fighters yet.")
        return self.fighters[0]

    @property
    def max_rank(self) -> int:
        """Return the lowest contender number (the champion is not counted)."""
        return max(len(self.fighters) - 1, 0)

    def iter_table(self) -> Iterator[tuple[str, Fighter]]:
        """Yield ``("C", champion)`` then ``("1", ...)``, ``("2", ...)`` ..."""
        for position, fighter in enumerate(self.fighters):
            yield ("C" if position == 0 else str(position)), fighter

    def at_rank(self, rank: int) -> Fighter:
        """Return the contender at ``rank`` (1 = best contender)."""
        if not 1 <= rank <= self.max_rank:
            raise LeagueError(
                f"There is no contender at rank {rank}. "
                f"Ranks go from 1 to {self.max_rank}."
            )
        return self.fighters[rank]

    def rank_of(self, fighter: Fighter) -> str:
        """Return ``"C"`` or the contender number of ``fighter``."""
        position = self.fighters.index(fighter)
        return "C" if position == 0 else str(position)

    def find(self, text: str) -> Fighter:
        """Find a fighter by full name, or by a part of it if it is unique."""
        wanted = normalise(text)
        if not wanted:
            raise LeagueError("Please give a fighter name.")
        for fighter in self.fighters:
            if normalise(fighter.name) == wanted:
                return fighter
        matches = [f for f in self.fighters if wanted in normalise(f.name)]
        if len(matches) == 1:
            return matches[0]
        if len(matches) > 1:
            names = ", ".join(f.name for f in matches)
            raise LeagueError(f"'{text}' matches more than one fighter: {names}.")
        raise LeagueError(f"No fighter called '{text}' in this league.")

    def record_fight(self, name_a: str, name_b: str, draw: bool = False) -> Fight:
        """Record a result. The first name wins unless ``draw`` is true."""
        a = self.find(name_a)
        b = self.find(name_b)
        if a is b:
            raise LeagueError("A fighter cannot fight themselves.")
        if draw:
            a.draws += 1
            b.draws += 1
            fight = Fight(a.name, b.name, None)
        else:
            a.wins += 1
            b.losses += 1
            fight = Fight(a.name, b.name, a.name)
            pos_a = self.fighters.index(a)
            pos_b = self.fighters.index(b)
            if pos_a > pos_b:
                self.fighters[pos_a], self.fighters[pos_b] = b, a
        self.fights.append(fight)
        return fight
