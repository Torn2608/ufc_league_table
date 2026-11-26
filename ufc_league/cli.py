"""Terminal interface: type a question or command, get an answer."""

from __future__ import annotations

from ufc_league.league import League
from ufc_league.models import Fighter, LeagueError
from ufc_league.storage import open_league
from ufc_league.utils import handle_errors

NUMBER_WORDS = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7,
    "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12,
    "thirteen": 13, "fourteen": 14, "fifteen": 15,
}  # fmt: skip

HELP_TEXT = """Ask or type any of these (capital letters do not matter):
  table                         show the whole league table
  who is number 1               the number 1 contender and their W-L-D
  rank 5   /   #5               same for any rank
  champion                      show the champion
  topuria   /   record topuria  record of one fighter
  result Topuria beat Gaethje   record a result (winner first)
  result Topuria draw Gaethje   record a draw
  help                          show this list
  quit                          save and leave"""

RANK_MARKERS = {"number", "no", "rank", "#"}
WIN_VERBS = {"beat", "beats", "defeated"}
DRAW_VERBS = {"draw", "draws"}


def split_words(text: str) -> list[str]:
    """Split a line into words and drop ``? ! . ,`` from their ends."""
    return [word.strip("?!.,") for word in text.split()]


def find_rank_word(words: list[str]) -> str | None:
    """Return the word after 'number', 'no', 'rank' or '#' (``#5`` also works)."""
    for index, word in enumerate(words):
        if word in RANK_MARKERS and index + 1 < len(words):
            return words[index + 1]
        if word.startswith("#") and len(word) > 1:
            return word[1:]
    return None


def split_result(words: list[str]) -> tuple[str, str, bool] | None:
    """Split ``['result', 'a', 'beat', 'b']`` into ``('a', 'b', is_draw)``."""
    for index, word in enumerate(words):
        if index > 0 and index < len(words) - 1 and (
            word in WIN_VERBS or word in DRAW_VERBS
        ):
            first = words[:index]
            if first[0] in {"result", "fight"}:
                first = first[1:]
            second = words[index + 1 :]
            return " ".join(first), " ".join(second), word in DRAW_VERBS
    return None


def format_line(label: str, fighter: Fighter) -> str:
    """Return one row of the table."""
    return f"{label:<6}{fighter.name:<26}{fighter.record}"


def format_table(league: League) -> str:
    """Return the whole table as text."""
    header = f"{league.title} - rankings as of {league.as_of or 'unknown'}"
    lines = [header, f"{'Rank':<6}{'Fighter':<26}W-L-D"]
    lines += [format_line(label, f) for label, f in league.iter_table()]
    return "\n".join(lines)


def describe_rank(league: League, rank: int) -> str:
    """Answer 'who is number N?'."""
    fighter = league.at_rank(rank)
    return f"#{rank} contender: {fighter.name}  |  Win-Loss-Draw: {fighter.record}"


def describe_fighter(league: League, text: str) -> str:
    """Answer a question about one fighter."""
    fighter = league.find(text)
    place = league.rank_of(fighter)
    label = "Champion" if place == "C" else f"Rank #{place}"
    return f"{fighter.name}  |  {label}  |  Win-Loss-Draw: {fighter.record}"


def parse_rank(word: str) -> int:
    """Turn ``"3"`` or ``"three"`` into 3; raise ``LeagueError`` otherwise."""
    if word.isdigit():
        return int(word)
    if word in NUMBER_WORDS:
        return NUMBER_WORDS[word]
    raise LeagueError(f"'{word}' is not a rank number.")


@handle_errors
def respond(league: League, text: str) -> str:
    """Turn one line typed by the user into the text to print."""
    line = text.strip().lower()
    if not line:
        return "Type 'help' to see what you can ask."
    if line in {"help", "?"}:
        return HELP_TEXT
    if line in {"table", "rankings", "ranking", "league", "top"}:
        return format_table(league)

    words = split_words(line)

    result = split_result(words)
    if result:
        first, second, is_draw = result
        fight = league.record_fight(first, second, draw=is_draw)
        return f"Recorded: {fight}\n\n{format_table(league)}"

    rank_word = find_rank_word(words)
    if rank_word is None and ("champion" in words or "champ" in words):
        champ = league.champion
        return f"Champion: {champ.name}  |  Win-Loss-Draw: {champ.record}"

    if rank_word is not None:
        return describe_rank(league, parse_rank(rank_word))

    for prefix in ("who is ", "who's ", "record ", "stats "):
        if line.startswith(prefix):
            line = line[len(prefix):]
            break
    try:
        return describe_fighter(league, line)
    except LeagueError:
        return f"I did not understand '{text.strip()}'. Type 'help' to see commands."


def main() -> None:
    """Run the interactive loop until the user quits."""
    with open_league() as league:
        for notice in league.notices:
            print(f"Note: {notice}")
        print(format_table(league))
        print("\nAsk me anything, e.g. 'who is number 1'. Type 'help' or 'quit'.")
        while True:
            try:
                text = input("\nufc> ")
            except (EOFError, KeyboardInterrupt):
                print()
                break
            if text.strip().lower() in {"quit", "exit", "q"}:
                break
            print(respond(league, text))
    print("Saved. Goodbye!")


if __name__ == "__main__":
    main()
