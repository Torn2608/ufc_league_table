import pytest

from ufc_league.cli import respond
from ufc_league.storage import SEED_FILE, load_league


@pytest.fixture
def league(tmp_path):
    return load_league(tmp_path / "none.json", SEED_FILE)


def test_who_is_number_one(league):
    answer = respond(league, "who is number 1")
    assert "Ilia Topuria" in answer
    assert "17-1-0" in answer


@pytest.mark.parametrize("question", ["rank 1", "#1", "Who is number one contender?"])
def test_rank_one_phrasings(league, question):
    assert "Ilia Topuria" in respond(league, question)


def test_champion_question(league):
    assert "Justin Gaethje" in respond(league, "who is the champion")


def test_rank_out_of_range_gives_message_not_traceback(league):
    assert respond(league, "number 99").startswith("Error:")
    assert respond(league, "number banana").startswith("Error:")


def test_fighter_lookup_by_surname(league):
    answer = respond(league, "record oliveira")
    assert "37-11-0" in answer and "Rank #3" in answer


def test_name_containing_no_is_not_a_rank(league):
    assert "Tom Nolan" in respond(league, "nolan")


def test_unknown_input_and_empty_input(league):
    assert "did not understand" in respond(league, "blah blah")
    assert "help" in respond(league, "   ")


def test_result_command_changes_table(league):
    answer = respond(league, "result Pimblett beat Holloway")
    assert "Recorded" in answer
    assert league.at_rank(4).name == "Paddy Pimblett"


def test_bad_result_input(league):
    assert respond(league, "result Nobody beat Topuria").startswith("Error:")
    assert respond(league, "result Topuria beat Topuria").startswith("Error:")
