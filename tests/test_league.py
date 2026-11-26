import pytest

from ufc_league.league import League
from ufc_league.models import Fight, Fighter, LeagueError


@pytest.fixture
def league() -> League:
    return League(
        as_of="2026-11-26",
        fighters=[
            Fighter("Champ One", 10, 1, 0),
            Fighter("Second Place", 8, 2, 0),
            Fighter("Third Place", 7, 3, 1),
        ],
    )


def test_record_property_and_str():
    fighter = Fighter("Ilia Topuria", 17, 1, 0)
    assert fighter.record == "17-1-0"
    assert str(fighter) == "Ilia Topuria (17-1-0)"


def test_negative_record_is_rejected():
    with pytest.raises(LeagueError):
        Fighter("Bad Data", wins=-1)


def test_blank_name_is_rejected():
    with pytest.raises(LeagueError):
        Fighter("   ")


def test_table_order_is_champion_then_ranks(league):
    rows = list(league.iter_table())
    assert [label for label, _ in rows] == ["C", "1", "2"]
    assert rows[1][1].name == "Second Place"


def test_at_rank_limits(league):
    assert league.at_rank(1).name == "Second Place"
    with pytest.raises(LeagueError):
        league.at_rank(0)
    with pytest.raises(LeagueError):
        league.at_rank(3)


def test_find_ignores_case_and_accepts_part_of_a_name():
    league = League(fighters=[Fighter("Champ"), Fighter("Benoit Saint Denis")])
    assert league.find("BENOIT  saint denis").name == "Benoit Saint Denis"
    assert league.find("denis").name == "Benoit Saint Denis"


def test_find_unknown_and_ambiguous(league):
    with pytest.raises(LeagueError):
        league.find("nobody")
    with pytest.raises(LeagueError):
        league.find("place")  # matches two fighters


def test_upset_swaps_places_and_updates_records(league):
    fight = league.record_fight("Third Place", "Champ One")
    assert league.champion.name == "Third Place"
    assert league.fighters[2].name == "Champ One"
    assert league.champion.record == "8-3-1"
    assert str(fight).endswith("Third Place beat Champ One")


def test_expected_result_keeps_order(league):
    league.record_fight("Champ One", "Third Place")
    assert [f.name for f in league.fighters][0] == "Champ One"
    assert league.fighters[0].wins == 11


def test_draw_updates_both_records_and_keeps_order(league):
    league.record_fight("Second Place", "Champ One", draw=True)
    assert league.champion.name == "Champ One"
    assert league.champion.record == "10-1-1"
    assert league.fights[0].winner is None


def test_fighter_cannot_fight_themselves(league):
    with pytest.raises(LeagueError):
        league.record_fight("Champ One", "champ one")


def test_empty_league_has_no_champion():
    with pytest.raises(LeagueError):
        League().champion


def test_fight_dict_round_trip():
    fight = Fight("A", "B", "A", "2026-01-01")
    assert Fight.from_dict(fight.to_dict()) == fight
