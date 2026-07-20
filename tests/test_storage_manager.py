import json
import os
import zipfile

from pathlib import Path

import pytest

from ace_gui.storage_manager import StorageManager


def test_ensure_dirs_creates_mods_and_liveries(tmp_path: Path) -> None:
    base = tmp_path / "ace"
    mgr = StorageManager(base)
    mgr.ensure_dirs()
    assert mgr.mods_dir.is_dir()
    assert mgr.liveries_dir.is_dir()


def test_ensure_dirs_is_idempotent(tmp_path: Path) -> None:
    base = tmp_path / "ace"
    mgr = StorageManager(base)
    mgr.ensure_dirs()
    mgr.ensure_dirs()
    assert mgr.mods_dir.is_dir()
    assert mgr.liveries_dir.is_dir()


def test_copy_file_roundtrip(tmp_path: Path) -> None:
    base = tmp_path / "ace"
    src = tmp_path / "source.txt"
    src.write_text("hello")
    dst = base / "sub" / "dest.txt"

    mgr = StorageManager(base)
    mgr.copy_file(src, dst)

    assert dst.is_file()
    assert dst.read_text() == "hello"


def test_extract_zip(tmp_path: Path) -> None:
    base = tmp_path / "ace"
    zip_src = tmp_path / "archive.zip"
    extract_dst = tmp_path / "extracted"

    inner = tmp_path / "inner.txt"
    inner.write_text("zipped content")

    with zipfile.ZipFile(zip_src, "w") as zf:
        zf.write(inner, arcname="inner.txt")

    mgr = StorageManager(base)
    mgr.extract_zip(zip_src, extract_dst)

    assert (extract_dst / "inner.txt").is_file()
    assert (extract_dst / "inner.txt").read_text() == "zipped content"


def test_extract_zip_bad_zip(tmp_path: Path) -> None:
    base = tmp_path / "ace"
    bad_zip = tmp_path / "not_a_zip.bin"
    bad_zip.write_text("not a zip file")
    mgr = StorageManager(base)
    with pytest.raises(ValueError, match="not a valid zip"):
        mgr.extract_zip(bad_zip, tmp_path / "out")


def test_delete_path_removes_file(tmp_path: Path) -> None:
    base = tmp_path / "ace"
    file_path = tmp_path / "todelete.txt"
    file_path.write_text("bye")

    mgr = StorageManager(base)
    mgr.delete_path(file_path)

    assert not file_path.exists()


def test_delete_path_removes_directory(tmp_path: Path) -> None:
    base = tmp_path / "ace"
    dir_path = tmp_path / "todelete"
    dir_path.mkdir()
    (dir_path / "child.txt").write_text("child")

    mgr = StorageManager(base)
    mgr.delete_path(dir_path)

    assert not dir_path.exists()


def test_delete_path_nonexistent_does_nothing(tmp_path: Path) -> None:
    base = tmp_path / "ace"
    missing = tmp_path / "does_not_exist"
    mgr = StorageManager(base)
    mgr.delete_path(missing)
    assert not missing.exists()


def test_backup_and_restore_file(tmp_path: Path) -> None:
    base = tmp_path / "ace"
    backup_dir = tmp_path / "backups"
    original = tmp_path / "important.txt"
    original.write_text("data")

    mgr = StorageManager(base)
    bp = mgr.backup_path(original, backup_dir)

    assert bp.exists()
    assert bp.read_text() == "data"
    assert backup_dir.is_dir()

    original.write_text("modified")
    mgr.restore_backup(bp, original)

    assert original.read_text() == "data"


def test_backup_and_restore_directory(tmp_path: Path) -> None:
    base = tmp_path / "ace"
    backup_dir = tmp_path / "backups"
    original_dir = tmp_path / "mydir"
    original_dir.mkdir()
    (original_dir / "file.txt").write_text("content")

    mgr = StorageManager(base)
    bp = mgr.backup_path(original_dir, backup_dir)

    assert bp.is_dir()
    assert (bp / "file.txt").read_text() == "content"

    (original_dir / "file.txt").write_text("changed")
    mgr.restore_backup(bp, original_dir)

    assert (original_dir / "file.txt").read_text() == "content"


def test_restore_backup_missing_raises(tmp_path: Path) -> None:
    base = tmp_path / "ace"
    mgr = StorageManager(base)
    with pytest.raises(FileNotFoundError, match="does not exist"):
        mgr.restore_backup(tmp_path / "nonexistent_backup", tmp_path / "original")


def test_read_write_json(tmp_path: Path) -> None:
    base = tmp_path / "ace"
    json_path = tmp_path / "data.json"

    mgr = StorageManager(base)
    data = {"key": "value", "num": 42}

    mgr.write_json(json_path, data)

    assert json_path.is_file()
    parsed = json.loads(json_path.read_text("utf-8"))
    assert parsed == data

    loaded = mgr.read_json(json_path)
    assert loaded == data


def test_validate_ace_path_valid(tmp_path: Path) -> None:
    base = tmp_path / "ace"
    (base / "Mods").mkdir(parents=True)
    mgr = StorageManager(base)
    assert mgr.validate_ace_path() is True


def test_validate_ace_path_invalid(tmp_path: Path) -> None:
    base = tmp_path / "ace"
    mgr = StorageManager(base)
    assert mgr.validate_ace_path() is False


def test_validate_ace_path_nonexistent(tmp_path: Path) -> None:
    base = tmp_path / "does_not_exist"
    mgr = StorageManager(base)
    assert mgr.validate_ace_path() is False
