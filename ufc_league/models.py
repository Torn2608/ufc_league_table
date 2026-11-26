"""Data classes for fighters and fights."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date


class LeagueError(Exception):
    """Raised for any problem the user can fix (bad name, bad score, ...)."""


@dataclass
class Fighter:
    """A fighter and their professional win-loss-draw record."""

    name: str
    wins: int = 0
    losses: int = 0
    draws: int = 0

    def __post_init__(self) -> None:
        """Reject empty names and negative record numbers."""
        self.name = " ".join(self.name.split())
        if not self.name:
            raise LeagueError("A fighter needs a name.")
        if min(self.wins, self.losses, self.draws) < 0:
            raise LeagueError("Wins, losses and draws cannot be negative.")

    @property
    def record(self) -> str:
        """Return the record as ``wins-losses-draws``."""
        return f"{self.wins}-{self.losses}-{self.draws}"

    def to_dict(self) -> dict:
        """Return a JSON-friendly dictionary."""
        return {
            "name": self.name,
            "wins": self.wins,
            "losses": self.losses,
            "draws": self.draws,
        }

    @classmethod
    def from_dict(cls, data: dict) -> Fighter:
        """Build a fighter from a dictionary made by ``to_dict``."""
        return cls(
            name=str(data["name"]),
            wins=int(data["wins"]),
            losses=int(data["losses"]),
            draws=int(data["draws"]),
        )

    def __str__(self) -> str:
        """Return e.g. ``Ilia Topuria (17-1-0)``."""
        return f"{self.name} ({self.record})"


@dataclass
class Fight:
    """One result. ``winner`` is ``None`` for a draw."""

    fighter_a: str
    fighter_b: str
    winner: str | None = None
    day: str = field(default_factory=lambda: date.today().isoformat())

    def to_dict(self) -> dict:
        """Return a JSON-friendly dictionary."""
        return {
            "fighter_a": self.fighter_a,
            "fighter_b": self.fighter_b,
            "winner": self.winner,
            "day": self.day,
        }

    @classmethod
    def from_dict(cls, data: dict) -> Fight:
        """Build a fight from a dictionary made by ``to_dict``."""
        winner = data.get("winner")
        return cls(
            fighter_a=str(data["fighter_a"]),
            fighter_b=str(data["fighter_b"]),
            winner=None if winner is None else str(winner),
            day=str(data["day"]),
        )

    def __str__(self) -> str:
        """Return e.g. ``2026-11-26: Ilia Topuria beat Justin Gaethje``."""
        if self.winner is None:
            return f"{self.day}: {self.fighter_a} drew with {self.fighter_b}"
        loser = self.fighter_b if self.winner == self.fighter_a else self.fighter_a
        return f"{self.day}: {self.winner} beat {loser}"
