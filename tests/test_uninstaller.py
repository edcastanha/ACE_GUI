from pathlib import Path
from unittest.mock import patch

import pytest

from ace_gui.backup_manager import BackupManager
from ace_gui.storage_manager import StorageManager
from ace_gui.uninstaller import UninstallResult, Uninstaller


def make_uninstaller(tmp_path: Path) -> tuple[Uninstaller, StorageManager, BackupManager]:
    ace_path = tmp_path / "ace"
    storage = StorageManager(ace_path)
    storage.ensure_dirs()
    backup_mgr = BackupManager(ace_path / ".ace_gui_backups")
    uninstaller = Uninstaller(storage, backup_mgr)
    return uninstaller, storage, backup_mgr


def test_uninstall_mod_removes_file(tmp_path: Path) -> None:
    uninstaller, storage, _ = make_uninstaller(tmp_path)
    mod_file = storage.mods_dir / "my_mod.7z"
    mod_file.write_text("mod content")

    result = uninstaller.uninstall_mod("my_mod.7z")

    assert result.success is True
    assert result.content_name == "my_mod.7z"
    assert result.content_type == "mod"
    assert not mod_file.exists()


def test_uninstall_mod_removes_directory(tmp_path: Path) -> None:
    uninstaller, storage, _ = make_uninstaller(tmp_path)
    mod_dir = storage.mods_dir / "my_mod"
    mod_dir.mkdir()
    (mod_dir / "contents.txt").write_text("mod content")

    result = uninstaller.uninstall_mod("my_mod")

    assert result.success is True
    assert not mod_dir.exists()


def test_uninstall_mod_restores_from_backup_on_failure(tmp_path: Path) -> None:
    uninstaller, storage, _ = make_uninstaller(tmp_path)
    mod_file = storage.mods_dir / "my_mod.7z"
    mod_file.write_text("original content")

    with patch.object(storage, "delete_path", side_effect=OSError("delete failed")):
        result = uninstaller.uninstall_mod("my_mod.7z")

    assert result.success is False
    assert result.backup_restored is True
    assert mod_file.exists()
    assert mod_file.read_text() == "original content"


def test_uninstall_mod_not_found(tmp_path: Path) -> None:
    uninstaller, _, _ = make_uninstaller(tmp_path)

    result = uninstaller.uninstall_mod("nonexistent.7z")

    assert result.success is False
    assert "not found" in (result.error_message or "").lower()


def test_uninstall_livery_removes_directory(tmp_path: Path) -> None:
    uninstaller, storage, _ = make_uninstaller(tmp_path)
    livery_dir = storage.liveries_dir / "CAR123" / "my_livery"
    livery_dir.mkdir(parents=True)
    (livery_dir / "skin.dds").write_text("skin data")

    result = uninstaller.uninstall_livery("CAR123", "my_livery")

    assert result.success is True
    assert result.content_name == "my_livery"
    assert result.content_type == "livery"
    assert not livery_dir.exists()


def test_uninstall_livery_removes_empty_car_guid_parent(tmp_path: Path) -> None:
    uninstaller, storage, _ = make_uninstaller(tmp_path)
    livery_dir = storage.liveries_dir / "CAR123" / "only_livery"
    livery_dir.mkdir(parents=True)
    (livery_dir / "skin.dds").write_text("skin data")

    result = uninstaller.uninstall_livery("CAR123", "only_livery")

    assert result.success is True
    assert not livery_dir.exists()
    assert not (storage.liveries_dir / "CAR123").exists()


def test_uninstall_livery_keeps_car_guid_when_not_empty(tmp_path: Path) -> None:
    uninstaller, storage, _ = make_uninstaller(tmp_path)
    car_dir = storage.liveries_dir / "CAR123"
    (car_dir / "livery_a").mkdir(parents=True)
    (car_dir / "livery_a" / "skin.dds").write_text("data")
    (car_dir / "livery_b").mkdir(parents=True)
    (car_dir / "livery_b" / "skin.dds").write_text("data")

    result = uninstaller.uninstall_livery("CAR123", "livery_a")

    assert result.success is True
    assert car_dir.exists()


def test_uninstall_livery_restores_from_backup_on_failure(tmp_path: Path) -> None:
    uninstaller, storage, _ = make_uninstaller(tmp_path)
    livery_dir = storage.liveries_dir / "CAR123" / "my_livery"
    livery_dir.mkdir(parents=True)
    (livery_dir / "skin.dds").write_text("skin data")

    with patch.object(storage, "delete_path", side_effect=OSError("delete failed")):
        result = uninstaller.uninstall_livery("CAR123", "my_livery")

    assert result.success is False
    assert result.backup_restored is True
    assert livery_dir.exists()
    assert (livery_dir / "skin.dds").read_text() == "skin data"


def test_uninstall_livery_not_found(tmp_path: Path) -> None:
    uninstaller, _, _ = make_uninstaller(tmp_path)

    result = uninstaller.uninstall_livery("CAR999", "ghost_livery")

    assert result.success is False
    assert "not found" in (result.error_message or "").lower()


def test_uninstall_result_has_correct_fields(tmp_path: Path) -> None:
    uninstaller, storage, _ = make_uninstaller(tmp_path)
    mod_file = storage.mods_dir / "some_mod.7z"
    mod_file.write_text("data")

    result = uninstaller.uninstall_mod("some_mod.7z")

    assert isinstance(result, UninstallResult)
    assert isinstance(result.success, bool)
    assert isinstance(result.content_name, str)
    assert isinstance(result.content_type, str)
    assert isinstance(result.backup_restored, bool)
    assert result.error_message is None


def test_cleanup_empty_parents_removes_only_empty_dirs(tmp_path: Path) -> None:
    uninstaller, storage, _ = make_uninstaller(tmp_path)
    mod_dir = storage.mods_dir / "category" / "submod"
    mod_dir.mkdir(parents=True)
    file_path = mod_dir / "file.txt"
    file_path.write_text("content")

    file_path.unlink()

    uninstaller._cleanup_empty_parents(file_path)

    assert not mod_dir.exists()
    assert not (storage.mods_dir / "category").exists()
    assert storage.mods_dir.exists()


def test_cleanup_empty_parents_stops_at_non_empty_dir(tmp_path: Path) -> None:
    uninstaller, storage, _ = make_uninstaller(tmp_path)
    category = storage.mods_dir / "category"
    sub_a = category / "sub_a"
    sub_a.mkdir(parents=True)
    (sub_a / "file.txt").write_text("a")
    sub_b = category / "sub_b"
    sub_b.mkdir(parents=True)
    (sub_b / "file.txt").write_text("b")

    sub_a_file = sub_a / "file.txt"
    sub_a_file.unlink()

    uninstaller._cleanup_empty_parents(sub_a_file)

    assert not sub_a.exists()
    assert category.exists()
    assert sub_b.exists()


def test_cleanup_empty_parents_stops_at_boundary(tmp_path: Path) -> None:
    uninstaller, storage, _ = make_uninstaller(tmp_path)

    boundary = storage.mods_dir
    child = boundary / "empty_dir"
    child.mkdir()
    file_path = child / "file.txt"
    file_path.write_text("data")
    file_path.unlink()

    uninstaller._cleanup_empty_parents(file_path)

    assert not child.exists()
    assert boundary.exists()
