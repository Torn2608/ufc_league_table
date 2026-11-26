import shutil

from ufc_league.storage import DATA_FILE, load_league, open_league


def test_shipped_data_loads_with_champion_and_fifteen_contenders():
    league = load_league(DATA_FILE)
    assert league.champion.name == "Justin Gaethje"
    assert league.max_rank == 15
    assert league.at_rank(1).record == "17-1-0"
    assert league.notices == []


def test_context_manager_saves_and_next_run_loads_it(tmp_path):
    copy = tmp_path / "seed.json"
    shutil.copy(DATA_FILE, copy)
    with open_league(copy) as league:
        league.record_fight("Topuria", "Gaethje")
    reloaded = load_league(copy)
    assert reloaded.champion.name == "Ilia Topuria"
    assert len(reloaded.fights) == 1


def test_corrupt_file_gives_notice_and_is_not_overwritten(tmp_path):
    bad = tmp_path / "seed.json"
    bad.write_text("{ this is not json", encoding="utf-8")
    with open_league(bad) as league:
        assert league.fighters == []
        assert "Could not load" in league.notices[0]
    assert bad.read_text(encoding="utf-8") == "{ this is not json"


def test_wrong_shape_file_gives_notice(tmp_path):
    bad = tmp_path / "seed.json"
    bad.write_text('{"title": "x"}', encoding="utf-8")
    assert load_league(bad).notices


def test_missing_file_gives_empty_league_not_crash(tmp_path):
    league = load_league(tmp_path / "missing.json")
    assert league.fighters == []
    assert league.notices


def test_unwritable_file_does_not_crash(tmp_path, capsys):
    copy = tmp_path / "seed.json"
    shutil.copy(DATA_FILE, copy)
    with open_league(copy):
        copy.unlink()
        copy.mkdir()  # saving onto a folder fails
    assert "Warning" in capsys.readouterr().err
