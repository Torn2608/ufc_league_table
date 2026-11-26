"""Saving and loading the league as JSON with pathlib."""

from __future__ import annotations

import json
import sys
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

from ufc_league.league import League
from ufc_league.models import Fight, Fighter, LeagueError

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DATA_FILE = DATA_DIR / "seed.json"


class StorageError(Exception):
    """Raised when a data file is missing, unreadable or broken."""


def league_to_dict(league: League) -> dict:
    """Turn a league into a JSON-friendly dictionary."""
    return {
        "title": league.title,
        "as_of": league.as_of,
        "fighters": [f.to_dict() for f in league.fighters],
        "fights": [f.to_dict() for f in league.fights],
    }


def league_from_dict(data: dict) -> League:
    """Build a league from a dictionary made by ``league_to_dict``."""
    return League(
        title=str(data["title"]),
        as_of=str(data["as_of"]),
        fighters=[Fighter.from_dict(item) for item in data["fighters"]],
        fights=[Fight.from_dict(item) for item in data["fights"]],
    )


def read_league(path: Path) -> League:
    """Read one JSON file; raise ``StorageError`` with a clear reason."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return league_from_dict(data)
    except FileNotFoundError as exc:
        raise StorageError(f"{path.name} was not found") from exc
    except json.JSONDecodeError as exc:
        raise StorageError(f"{path.name} is not valid JSON ({exc.msg})") from exc
    except (KeyError, TypeError, ValueError, AttributeError, LeagueError) as exc:
        raise StorageError(f"{path.name} has missing or wrong data") from exc
    except OSError as exc:
        raise StorageError(f"{path.name} could not be read ({exc.strerror})") from exc


def write_league(league: League, path: Path) -> None:
    """Write the league to ``path`` as JSON."""
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        text = json.dumps(league_to_dict(league), indent=2)
        path.write_text(text, encoding="utf-8")
    except OSError as exc:
        raise StorageError(f"could not save {path.name} ({exc.strerror})") from exc


def load_league(path: Path = DATA_FILE) -> League:
    """Load the league from ``path``.

    A missing or broken file never raises: the league is empty and the reason
    is added to ``league.notices``.
    """
    try:
        league = read_league(path)
    except StorageError as exc:
        league = League()
        league.notices.append(f"Could not load the rankings: {exc}.")
    return league


@contextmanager
def open_league(path: Path = DATA_FILE) -> Iterator[League]:
    """Load the league, hand it over, and save it when the block ends.

    If the file could not be loaded it is left alone, so a broken file is
    never overwritten by an empty league.
    """
    league = load_league(path)
    try:
        yield league
    finally:
        if not league.notices:
            try:
                write_league(league, path)
            except StorageError as exc:
                print(f"Warning: {exc}", file=sys.stderr)
