from ufc_league.storage import SEED_FILE, load_league, open_league


def test_shipped_seed_loads_with_champion_and_fifteen_contenders(tmp_path):
    league = load_league(tmp_path / "missing.json", SEED_FILE)
    assert league.champion.name == "Justin Gaethje"
    assert league.max_rank == 15
    assert league.at_rank(1).record == "17-1-0"
    assert league.notices == []


def test_context_manager_saves_and_next_run_loads_it(tmp_path):
    save = tmp_path / "league.json"
    with open_league(save, SEED_FILE) as league:
        league.record_fight("Topuria", "Gaethje")
    assert save.exists()
    reloaded = load_league(save, SEED_FILE)
    assert reloaded.champion.name == "Ilia Topuria"
    assert len(reloaded.fights) == 1


def test_corrupt_save_falls_back_to_seed_with_notice(tmp_path):
    save = tmp_path / "league.json"
    save.write_text("{ this is not json", encoding="utf-8")
    league = load_league(save, SEED_FILE)
    assert league.champion.name == "Justin Gaethje"
    assert "ignored" in league.notices[0]


def test_wrong_shape_save_falls_back_to_seed(tmp_path):
    save = tmp_path / "league.json"
    save.write_text('{"title": "x"}', encoding="utf-8")
    league = load_league(save, SEED_FILE)
    assert league.max_rank == 15
    assert league.notices


def test_missing_seed_and_save_gives_empty_league_not_crash(tmp_path):
    league = load_league(tmp_path / "a.json", tmp_path / "b.json")
    assert league.fighters == []
    assert league.notices


def test_unwritable_save_does_not_crash(tmp_path, capsys):
    blocker = tmp_path / "file.txt"
    blocker.write_text("x", encoding="utf-8")
    with open_league(blocker / "league.json", SEED_FILE):
        pass
    assert "Warning" in capsys.readouterr().err
