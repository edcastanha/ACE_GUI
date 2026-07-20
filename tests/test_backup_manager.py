from pathlib import Path

import pytest

from ace_gui.backup_manager import BackupError, BackupManager


def test_create_backup_stores_file_at_correct_path(tmp_path: Path) -> None:
    backup_root = tmp_path / "backups"
    source = tmp_path / "test.txt"
    source.write_text("hello")

    mgr = BackupManager(backup_root)
    bp = mgr.create_backup(source)

    assert bp.exists()
    assert bp.read_text() == "hello"
    assert bp.parent.parent == backup_root
    assert bp.parent.is_dir()


def test_create_backup_with_timestamp(tmp_path: Path) -> None:
    backup_root = tmp_path / "backups"
    source = tmp_path / "test.txt"
    source.write_text("data")

    mgr = BackupManager(backup_root)
    bp = mgr.create_backup(source)

    timestamp_dir = bp.parent.name
    assert len(timestamp_dir) == 15
    assert "_" in timestamp_dir


def test_restore_replaces_target(tmp_path: Path) -> None:
    backup_root = tmp_path / "backups"
    source = tmp_path / "original.txt"
    source.write_text("original content")

    mgr = BackupManager(backup_root)
    bp = mgr.create_backup(source)

    source.write_text("modified content")
    mgr.restore(bp, source)

    assert source.read_text() == "original content"


def test_cleanup_removes_backup(tmp_path: Path) -> None:
    backup_root = tmp_path / "backups"
    source = tmp_path / "test.txt"
    source.write_text("hello")

    mgr = BackupManager(backup_root)
    bp = mgr.create_backup(source)

    assert bp.exists()
    mgr.cleanup(bp)
    assert not bp.exists()


def test_cleanup_all_removes_all_backups(tmp_path: Path) -> None:
    backup_root = tmp_path / "backups"
    mgr = BackupManager(backup_root)

    f1 = tmp_path / "f1.txt"
    f1.write_text("1")
    f2 = tmp_path / "f2.txt"
    f2.write_text("2")

    mgr.create_backup(f1)
    mgr.create_backup(f2)

    mgr.cleanup_all()
    assert not backup_root.exists()


def test_create_backup_with_directory(tmp_path: Path) -> None:
    backup_root = tmp_path / "backups"
    source_dir = tmp_path / "mydir"
    source_dir.mkdir()
    (source_dir / "nested.txt").write_text("nested")

    mgr = BackupManager(backup_root)
    bp = mgr.create_backup(source_dir)

    assert bp.is_dir()
    assert (bp / "nested.txt").read_text() == "nested"


def test_backup_error_on_invalid_source(tmp_path: Path) -> None:
    backup_root = tmp_path / "backups"
    invalid = tmp_path / "nonexistent"

    mgr = BackupManager(backup_root)
    with pytest.raises(BackupError):
        mgr.create_backup(invalid)


def test_restore_error_on_missing_backup(tmp_path: Path) -> None:
    backup_root = tmp_path / "backups"
    mgr = BackupManager(backup_root)
    with pytest.raises(BackupError, match="does not exist"):
        mgr.restore(tmp_path / "nonexistent", tmp_path / "target")


def test_list_backups_returns_sorted(tmp_path: Path) -> None:
    backup_root = tmp_path / "backups"
    mgr = BackupManager(backup_root)

    f1 = tmp_path / "a.txt"
    f1.write_text("a")
    f2 = tmp_path / "b.txt"
    f2.write_text("b")

    mgr.create_backup(f1)
    mgr.create_backup(f2)

    backups = mgr.list_backups()
    assert len(backups) == 2
    assert all(b.exists() for b in backups)


def test_list_backups_empty(tmp_path: Path) -> None:
    mgr = BackupManager(tmp_path / "backups")
    assert mgr.list_backups() == []


def test_cleanup_removes_timestamp_dir_when_empty(tmp_path: Path) -> None:
    backup_root = tmp_path / "backups"
    source = tmp_path / "test.txt"
    source.write_text("hello")

    mgr = BackupManager(backup_root)
    bp = mgr.create_backup(source)
    timestamp_dir = bp.parent

    mgr.cleanup(bp)

    assert not bp.exists()
    assert not timestamp_dir.exists()
