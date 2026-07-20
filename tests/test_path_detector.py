import os
from pathlib import Path

from ace_gui.path_detector import (
    LinuxProtonPathDetector,
    PathDetectionResult,
    WindowsPathDetector,
    auto_detect_path,
)
from ace_gui.storage_manager import StorageManager


def test_validate_ace_path_with_mock_dirs(tmp_path: Path) -> None:
    base = tmp_path / "ace_game"
    (base / "Mods").mkdir(parents=True)
    (base / "External Liveries").mkdir(parents=True)

    mgr = StorageManager(base)
    assert mgr.validate_ace_path() is True

    empty_dir = tmp_path / "empty"
    empty_dir.mkdir()
    mgr2 = StorageManager(empty_dir)
    assert mgr2.validate_ace_path() is False


def test_validate_ace_path_mods_only(tmp_path: Path) -> None:
    base = tmp_path / "ace_game"
    (base / "Mods").mkdir(parents=True)

    mgr = StorageManager(base)
    assert mgr.validate_ace_path() is True


def test_validate_ace_path_liveries_only(tmp_path: Path) -> None:
    base = tmp_path / "ace_game"
    (base / "External Liveries").mkdir(parents=True)

    mgr = StorageManager(base)
    assert mgr.validate_ace_path() is True


def test_windows_detector_with_mocked_env(monkeypatch, tmp_path: Path) -> None:
    ace_dir = tmp_path / "Saved Games" / "ACE"
    (ace_dir / "Mods").mkdir(parents=True)

    monkeypatch.setenv("USERPROFILE", str(tmp_path))
    monkeypatch.setattr("platform.system", lambda: "Windows")

    result = WindowsPathDetector().detect()

    assert isinstance(result, PathDetectionResult)
    assert result.found is True
    assert result.path == ace_dir
    assert result.method == "auto_windows"


def test_windows_detector_not_found(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("USERPROFILE", str(tmp_path))
    monkeypatch.setattr("platform.system", lambda: "Windows")

    result = WindowsPathDetector().detect()

    assert isinstance(result, PathDetectionResult)
    assert result.found is False
    assert result.path is None
    assert result.method == "auto_windows"


def test_windows_detector_no_env_var(monkeypatch) -> None:
    monkeypatch.delenv("USERPROFILE", raising=False)
    result = WindowsPathDetector().detect()

    assert result.found is False
    assert result.path is None


def test_linux_detector_no_steam(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr("platform.system", lambda: "Linux")

    home = tmp_path / "home"
    monkeypatch.setattr(Path, "home", lambda: home)

    result = LinuxProtonPathDetector().detect()

    assert isinstance(result, PathDetectionResult)
    assert result.found is False
    assert result.path is None
    assert result.method == "auto_linux"


def test_linux_detector_with_valid_prefix(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr("platform.system", lambda: "Linux")

    home = tmp_path / "home"
    monkeypatch.setattr(Path, "home", lambda: home)

    ace_dir = (
        home
        / ".steam"
        / "steam"
        / "steamapps"
        / "compatdata"
        / "123456"
        / "pfx"
        / "drive_c"
        / "users"
        / "steamuser"
        / "Saved Games"
        / "ACE"
    )
    (ace_dir / "Mods").mkdir(parents=True)

    result = LinuxProtonPathDetector().detect()

    assert result.found is True
    assert result.path == ace_dir
    assert result.method == "auto_linux"


def test_linux_detector_with_flatpak(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr("platform.system", lambda: "Linux")

    home = tmp_path / "home"
    monkeypatch.setattr(Path, "home", lambda: home)

    ace_dir = (
        home
        / ".var"
        / "app"
        / "com.valvesoftware.Steam"
        / "data"
        / "steam"
        / "steamapps"
        / "compatdata"
        / "654321"
        / "pfx"
        / "drive_c"
        / "users"
        / "steamuser"
        / "Saved Games"
        / "ACE"
    )
    (ace_dir / "External Liveries").mkdir(parents=True)

    result = LinuxProtonPathDetector().detect()

    assert result.found is True
    assert result.path == ace_dir
    assert result.method == "auto_flatpak"


def test_auto_detect_linux(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr("platform.system", lambda: "Linux")

    home = tmp_path / "home"
    monkeypatch.setattr(Path, "home", lambda: home)

    ace_dir = (
        home
        / ".steam"
        / "steam"
        / "steamapps"
        / "compatdata"
        / "99999"
        / "pfx"
        / "drive_c"
        / "users"
        / "steamuser"
        / "Saved Games"
        / "ACE"
    )
    (ace_dir / "Mods").mkdir(parents=True)

    result = auto_detect_path()

    assert result.found is True
    assert result.path == ace_dir


def test_auto_detect_windows(monkeypatch, tmp_path: Path) -> None:
    ace_dir = tmp_path / "Saved Games" / "ACE"
    (ace_dir / "Mods").mkdir(parents=True)

    monkeypatch.setenv("USERPROFILE", str(tmp_path))
    monkeypatch.setattr("platform.system", lambda: "Windows")

    result = auto_detect_path()
    assert result.found is True
    assert result.path == ace_dir
