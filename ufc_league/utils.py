"""Small helpers: a decorator that turns league errors into friendly text."""

from __future__ import annotations

import functools
from collections.abc import Callable

from ufc_league.models import LeagueError


def handle_errors(func: Callable[..., str]) -> Callable[..., str]:
    """Return an error message instead of letting a ``LeagueError`` escape."""

    @functools.wraps(func)
    def wrapper(*args: object, **kwargs: object) -> str:
        try:
            return func(*args, **kwargs)
        except LeagueError as exc:
            return f"Error: {exc}"
        except ValueError:
            return "Error: that input could not be understood. Type 'help'."

    return wrapper
