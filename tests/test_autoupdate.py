"""Update checks remain bounded, cached and safe when background work fails."""

import json
import subprocess
import sys
from unittest.mock import Mock

import pytest

from nxdo import autoupdate


@pytest.fixture(autouse=True)
def isolate_updates(monkeypatch, tmp_path):
    for key in ("CI", "NO_AUTOUPDATE", "AUTO_UPGRADE", "NXDO_AUTO_UPGRADE"):
        monkeypatch.delenv(key, raising=False)
    monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path / "cache"))
    monkeypatch.setattr(autoupdate.subprocess, "Popen", Mock())
    monkeypatch.setattr(autoupdate.metadata, "version", lambda _: "1.0.0")
    monkeypatch.setattr(autoupdate.time, "time", lambda: 1000)


def test_first_check_starts_detached_worker_and_uses_package_cache(tmp_path):
    autoupdate.check_for_updates("nxdo", ttl_seconds=60)
    args, kwargs = autoupdate.subprocess.Popen.call_args
    assert args[0][:2] == [sys.executable, "-c"]
    worker = args[0][2]
    assert str(tmp_path / "cache" / "nxdo" / "update_check.json") in worker
    assert "current_version = '1.0.0'" in worker
    assert "timeout=3.0" in worker
    assert kwargs == {
        "stdout": subprocess.DEVNULL, "stderr": subprocess.DEVNULL,
        "stdin": subprocess.DEVNULL, "start_new_session": True,
    }


def test_default_cache_uses_home(monkeypatch, tmp_path):
    monkeypatch.delenv("XDG_CACHE_HOME")
    monkeypatch.setattr(autoupdate.Path, "home", lambda: tmp_path)
    cache = autoupdate._get_cache_dir("nxdo")
    assert cache == tmp_path / ".cache" / "nxdo"
    assert cache.is_dir()


@pytest.mark.parametrize("age,query", [(59, False), (60, True), (61, True)])
def test_cache_ttl_boundary(tmp_path, age, query):
    path = tmp_path / "result.json"
    path.write_text(json.dumps({"last_check": 1000 - age, "latest_version": "2.0.0"}))
    assert autoupdate._read_cached_check(path, 60) == ("2.0.0", query)


@pytest.mark.parametrize("contents", [None, "{broken", '{"last_check":"invalid"}'])
def test_absent_or_invalid_cache_requests_fresh_check(tmp_path, contents):
    path = tmp_path / "result.json"
    if contents is not None:
        path.write_text(contents)
    assert autoupdate._read_cached_check(path, 60) == (None, True)


@pytest.mark.parametrize("latest", ["1.0.0", "0.9.0", "2.0.0"])
def test_fresh_cache_never_queries_network(latest, capsys):
    path = autoupdate._get_cache_dir("nxdo") / "update_check.json"
    path.write_text(json.dumps({"last_check": 999, "latest_version": latest}))
    autoupdate.check_for_updates("nxdo", ttl_seconds=60)
    autoupdate.subprocess.Popen.assert_not_called()
    message = capsys.readouterr().err
    assert bool(message) == (latest == "2.0.0")
    if message:
        assert "1.0.0 → 2.0.0" in message
        assert "pip install --upgrade nxdo" in message


@pytest.mark.parametrize("key", ["CI", "NO_AUTOUPDATE"])
def test_disabled_check_does_not_inspect_installation(monkeypatch, key):
    monkeypatch.setenv(key, "1")
    lookup = Mock(side_effect=AssertionError("disabled check consulted metadata"))
    monkeypatch.setattr(autoupdate.metadata, "version", lookup)
    autoupdate.check_for_updates("nxdo")
    lookup.assert_not_called()
    autoupdate.subprocess.Popen.assert_not_called()


def test_missing_package_does_not_spawn_worker(monkeypatch):
    monkeypatch.setattr(autoupdate.metadata, "version", Mock(side_effect=LookupError("missing")))
    autoupdate.check_for_updates("nxdo")
    autoupdate.subprocess.Popen.assert_not_called()


@pytest.mark.parametrize("key", ["AUTO_UPGRADE", "NXDO_AUTO_UPGRADE"])
def test_opt_in_upgrade_is_detached(monkeypatch, capsys, key):
    monkeypatch.setenv(key, "1")
    autoupdate._handle_available_update("nxdo", "1.0.0", "2.0.0")
    args, kwargs = autoupdate.subprocess.Popen.call_args
    assert args[0] == [sys.executable, "-m", "pip", "install", "--upgrade", "--quiet",
                       "--disable-pip-version-check", "nxdo"]
    assert kwargs["start_new_session"] is True
    assert kwargs["stdin"] == kwargs["stdout"] == kwargs["stderr"] == subprocess.DEVNULL
    assert "1.0.0 → 2.0.0" in capsys.readouterr().err


@pytest.mark.parametrize("action", ["check", "upgrade"])
def test_spawn_failure_is_nonfatal(monkeypatch, tmp_path, action):
    monkeypatch.setattr(autoupdate.subprocess, "Popen", Mock(side_effect=OSError("denied")))
    if action == "check":
        autoupdate._spawn_detached_check("nxdo", "1.0.0", tmp_path / "cache.json")
    else:
        autoupdate._spawn_background_upgrade("nxdo")


def test_notification_failure_does_not_prevent_expired_cache_refresh(monkeypatch):
    monkeypatch.setattr(autoupdate, "_handle_available_update", Mock(side_effect=OSError("stderr closed")))
    path = autoupdate._get_cache_dir("nxdo") / "update_check.json"
    path.write_text(json.dumps({"last_check": 0, "latest_version": "2.0.0"}))
    autoupdate.check_for_updates("nxdo", ttl_seconds=60)
    autoupdate.subprocess.Popen.assert_called_once()


@pytest.mark.parametrize("latest,current,newer", [
    ("2.0", "1.9", True), ("1.0", "1.0", False), ("1.0rc1", "1.0", False),
])
def test_version_comparison(latest, current, newer):
    assert autoupdate._is_newer(latest, current) is newer


@pytest.mark.parametrize("latest,current,newer", [
    ("2.0beta", "1.9", True), ("1.0", "1.0", False), ("x.2", "0.1", True),
])
def test_version_comparison_without_packaging(monkeypatch, latest, current, newer):
    monkeypatch.setitem(sys.modules, "packaging", None)
    assert autoupdate._is_newer(latest, current) is newer


def test_cli_still_runs_when_optional_update_check_fails(monkeypatch, caplog):
    from nxdo import cli

    monkeypatch.setattr(autoupdate, "check_for_updates", Mock(side_effect=OSError("cache denied")))
    command = Mock()
    monkeypatch.setattr(cli, "app", command)
    cli.app_entry()
    command.assert_called_once_with()
    assert "Optional update check failed" in caplog.text
    assert "cache denied" in caplog.text
