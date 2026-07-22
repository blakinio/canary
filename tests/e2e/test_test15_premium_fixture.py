from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
ACCOUNT_FIXTURE = ROOT / "docker" / "data" / "01-test_account.sql"
LOGIN_SCRIPT = ROOT / "data" / "scripts" / "creaturescripts" / "player" / "login.lua"


def test_test15_fixture_seeds_bounded_premium_window() -> None:
    sql = ACCOUNT_FIXTURE.read_text(encoding="utf-8")

    assert "(115 , 'test15', '@test15'" in sql
    assert sql.count("UPDATE `accounts`") == 1
    assert "SET `premdays` = 30, `lastday` = UNIX_TIMESTAMP() + (30 * 24 * 60 * 60)" in sql
    assert "WHERE `id` = 115;" in sql


def test_fixture_matches_promotion_relog_policy() -> None:
    login = LOGIN_SCRIPT.read_text(encoding="utf-8")

    assert "if player:isPremium() then" in login
    assert "elseif player:isPromoted() then" in login
    assert "player:setVocation(vocation:getDemotion())" in login
