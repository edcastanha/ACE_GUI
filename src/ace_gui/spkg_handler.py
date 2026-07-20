from __future__ import annotations

import shutil
import tempfile
import zipfile
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ace_gui.storage_manager import StorageManager


_PKG_MAGIC = b"PK\x03\x04"


class SpkgHandler:
    def __init__(self, storage_manager: StorageManager) -> None:
        self._storage = storage_manager

    def probe_format(self, spkg_path: Path) -> str:
        with spkg_path.open("rb") as f:
            header = f.read(4)
        return "zip" if header[:4] == _PKG_MAGIC else "binary"

    def validate_zip(self, spkg_path: Path) -> bool:
        try:
            with zipfile.ZipFile(spkg_path, "r") as zf:
                bad = zf.testzip()
            return bad is None
        except (zipfile.BadZipFile, zipfile.LargeZipFile):
            return False

    def install(self, spkg_path: Path, overwrite: bool = False) -> Path:
        fmt = self.probe_format(spkg_path)
        if fmt == "zip":
            dest = self._storage.mods_dir / spkg_path.stem
        else:
            dest = self._storage.mods_dir / spkg_path.name

        if dest.exists() and not overwrite:
            raise FileExistsError(
                f"Mod already exists at {dest}. Use overwrite=True to replace."
            )

        if dest.exists() and overwrite:
            backup_dir = self._storage.base_path / ".backups"
            self._storage.backup_path(dest, backup_dir)
            self._storage.delete_path(dest)

        if fmt == "zip":
            self._storage.extract_zip(spkg_path, dest)
        else:
            self._storage.copy_file(spkg_path, dest)

        return dest
