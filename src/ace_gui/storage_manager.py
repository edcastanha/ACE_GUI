import json
import os
import shutil
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Optional


class StorageManager:
    def __init__(self, base_path: Path) -> None:
        self._base_path = base_path

    @property
    def base_path(self) -> Path:
        return self._base_path

    @property
    def mods_dir(self) -> Path:
        return self._base_path / "Mods"

    @property
    def liveries_dir(self) -> Path:
        return self._base_path / "External Liveries"

    def ensure_dirs(self) -> None:
        self.mods_dir.mkdir(parents=True, exist_ok=True)
        self.liveries_dir.mkdir(parents=True, exist_ok=True)

    def copy_file(self, src: Path, dst: Path) -> None:
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src=src, dst=dst)

    def extract_zip(self, src: Path, dst: Path) -> None:
        dst.mkdir(parents=True, exist_ok=True)
        try:
            with zipfile.ZipFile(src, "r") as zf:
                zf.extractall(path=dst)
        except zipfile.BadZipFile:
            raise ValueError(f"File is not a valid zip archive: {src}")
        except Exception:
            raise

    def delete_path(self, path: Path) -> None:
        if not path.exists():
            return
        if path.is_dir():
            shutil.rmtree(path)
        else:
            path.unlink()

    def backup_path(self, path: Path, backup_dir: Path) -> Path:
        backup_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{path.name}_{timestamp}"
        backup_path = backup_dir / backup_name
        if path.is_dir():
            shutil.copytree(src=path, dst=backup_path)
        else:
            shutil.copy2(src=path, dst=backup_path)
        return backup_path

    def restore_backup(self, backup_path: Path, original_path: Path) -> None:
        if not backup_path.exists():
            raise FileNotFoundError(f"Backup does not exist: {backup_path}")
        self.delete_path(original_path)
        if backup_path.is_dir():
            shutil.copytree(src=backup_path, dst=original_path)
        else:
            shutil.copy2(src=backup_path, dst=original_path)

    def read_json(self, path: Path) -> dict:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)

    def write_json(self, path: Path, data: dict) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def validate_ace_path(self, path: Optional[Path] = None) -> bool:
        target = path if path is not None else self._base_path
        if not target or not target.exists():
            return False
        return (target / "Mods").is_dir() or (target / "External Liveries").is_dir()
