import zipfile
from pathlib import Path

import pytest

from ace_gui.spkg_handler import SpkgHandler
from ace_gui.storage_manager import StorageManager


def test_probe_format_zip(tmp_path: Path) -> None:
    mgr = StorageManager(tmp_path)
    handler = SpkgHandler(mgr)
    spkg = tmp_path / "mod.spkg"
    with zipfile.ZipFile(spkg, "w") as zf:
        zf.writestr("dummy.txt", "hello")
    assert handler.probe_format(spkg) == "zip"


def test_probe_format_binary(tmp_path: Path) -> None:
    mgr = StorageManager(tmp_path)
    handler = SpkgHandler(mgr)
    spkg = tmp_path / "mod.spkg"
    spkg.write_bytes(b"\x00\x01\x02\x03some random data")
    assert handler.probe_format(spkg) == "binary"


def test_validate_zip_valid(tmp_path: Path) -> None:
    mgr = StorageManager(tmp_path)
    handler = SpkgHandler(mgr)
    spkg = tmp_path / "valid.zip"
    with zipfile.ZipFile(spkg, "w") as zf:
        zf.writestr("file.txt", "content")
    assert handler.validate_zip(spkg) is True


def test_validate_zip_corrupted(tmp_path: Path) -> None:
    mgr = StorageManager(tmp_path)
    handler = SpkgHandler(mgr)
    spkg = tmp_path / "corrupt.zip"
    spkg.write_bytes(b"not a zip at all")
    assert handler.validate_zip(spkg) is False


def test_install_binary_mode(tmp_path: Path) -> None:
    mgr = StorageManager(tmp_path / "ace")
    mgr.ensure_dirs()
    handler = SpkgHandler(mgr)
    spkg = tmp_path / "mod.spkg"
    spkg.write_bytes(b"\x00\x01\x02\x03binary_mod_data")

    dest = handler.install(spkg)

    assert dest == mgr.mods_dir / "mod.spkg"
    assert dest.is_file()
    assert dest.read_bytes() == b"\x00\x01\x02\x03binary_mod_data"


def test_install_zip_mode(tmp_path: Path) -> None:
    mgr = StorageManager(tmp_path / "ace")
    mgr.ensure_dirs()
    handler = SpkgHandler(mgr)
    spkg = tmp_path / "mod.spkg"
    with zipfile.ZipFile(spkg, "w") as zf:
        zf.writestr("data.txt", "zip content")

    dest = handler.install(spkg)

    assert dest == mgr.mods_dir / "mod"
    assert dest.is_dir()
    assert (dest / "data.txt").is_file()
    assert (dest / "data.txt").read_text() == "zip content"


def test_install_overwrite_replace(tmp_path: Path) -> None:
    mgr = StorageManager(tmp_path / "ace")
    mgr.ensure_dirs()
    handler = SpkgHandler(mgr)

    existing = mgr.mods_dir / "mod.spkg"
    existing.write_text("old_data")

    spkg = tmp_path / "mod.spkg"
    spkg.write_bytes(b"\x00\x01\x02\x03new_data")

    dest = handler.install(spkg, overwrite=True)

    assert dest == existing
    assert dest.read_bytes() == b"\x00\x01\x02\x03new_data"


def test_install_raises_file_exists(tmp_path: Path) -> None:
    mgr = StorageManager(tmp_path / "ace")
    mgr.ensure_dirs()
    handler = SpkgHandler(mgr)

    existing = mgr.mods_dir / "mod.spkg"
    existing.write_text("old_data")

    spkg = tmp_path / "mod.spkg"
    spkg.write_bytes(b"\x00\x01\x02\x03new_data")

    with pytest.raises(FileExistsError, match="already exists"):
        handler.install(spkg, overwrite=False)
