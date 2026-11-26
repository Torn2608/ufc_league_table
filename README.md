# ufc_league_table

A terminal league table for the **UFC Lightweight (155 lb)** division.
Ask it questions like *"who is number 1"* and it answers with the fighter's
name and Win-Loss-Draw record.

Rankings and records: champion + top 15, as of **26 Nov 2026**
(source: ufcrankings.org, a fan site). Check them against ufc.com if exact
numbers matter.

## Requirements

Python 3.12 or newer. The program itself needs no extra packages.

## How to run

From the project folder (the one that contains `main.py`):

**macOS**

```bash
python3 main.py
# or
python3 -m ufc_league
```

**Windows** (Command Prompt or PowerShell)

```bat
python main.py
rem or
python -m ufc_league
```

## What you can type

| You type                        | What happens                                |
| ------------------------------- | ------------------------------------------- |
| `table`                         | whole league table                          |
| `who is number 1` / `rank 5` / `#5` | that contender's name and W-L-D         |
| `champion`                      | the champion and W-L-D                      |
| `topuria` / `record oliveira`   | one fighter's rank and W-L-D                |
| `result Topuria beat Gaethje`   | record a result (winner first)              |
| `result Topuria draw Gaethje`   | record a draw                               |
| `help` / `quit`                 | list commands / save and leave              |

Example:

```text
ufc> who is number 1
#1 contender: Ilia Topuria  |  Win-Loss-Draw: 17-1-0
```

### Ranking rule for new results

The table starts as the real ranking. When you record a result, a lower-ranked
fighter who beats a higher-ranked one swaps places with them (beating the
champion makes you champion). Draws and expected wins keep the order.
Records (W-L-D) always update.

## Saving

On quit the league is saved to `data/league.json` and loaded again next run.
If that file is missing or broken, the program tells you and starts from
`data/seed.json` (the shipped rankings). Delete `data/league.json` to reset.

## Project layout

```text
main.py              start the program
ufc_league/
  models.py          Fighter and Fight dataclasses
  league.py          League: the ranked ladder and result rules
  storage.py         JSON save/load (pathlib) + open_league context manager
  utils.py           handle_errors decorator
  cli.py             terminal questions and answers
data/seed.json       starting rankings
tests/               pytest tests
```

## Tests and code checks

```bash
python -m pip install pytest ruff
python -m pytest
python -m ruff check .
```
