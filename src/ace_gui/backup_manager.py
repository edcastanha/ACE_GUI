import shutil
from pathlib import Path
from datetime import datetime
from typing import Optional


class BackupError(Exception):
    ...


class BackupManager:
    def __init__(self, backup_root: Path) -> None:
        self._backup_root = backup_root

    def create_backup(self, source_path: Path) -> Path:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = self._backup_root / timestamp
        backup_dir.mkdir(parents=True, exist_ok=True)
        backup_path = backup_dir / source_path.name
        try:
            if source_path.is_dir():
                shutil.copytree(src=source_path, dst=backup_path)
            else:
                shutil.copy2(src=source_path, dst=backup_path)
        except (OSError, shutil.Error) as e:
            raise BackupError(f"Failed to create backup of {source_path}: {e}") from e
        return backup_path

    def restore(self, backup_path: Path, target_path: Path) -> None:
        if not backup_path.exists():
            raise BackupError(f"Backup does not exist: {backup_path}")
        try:
            if target_path.exists():
                if target_path.is_dir():
                    shutil.rmtree(target_path)
                else:
                    target_path.unlink()
            if backup_path.is_dir():
                shutil.copytree(src=backup_path, dst=target_path)
            else:
                shutil.copy2(src=backup_path, dst=target_path)
        except (OSError, shutil.Error) as e:
            raise BackupError(f"Failed to restore {backup_path} to {target_path}: {e}") from e

    def cleanup(self, backup_path: Path) -> None:
        try:
            if backup_path.is_dir():
                shutil.rmtree(backup_path)
            else:
                backup_path.unlink()
            parent = backup_path.parent
            if parent != self._backup_root and parent.exists() and not any(parent.iterdir()):
                parent.rmdir()
        except (OSError, shutil.Error) as e:
            raise BackupError(f"Failed to cleanup {backup_path}: {e}") from e

    def cleanup_all(self) -> None:
        try:
            if self._backup_root.exists():
                shutil.rmtree(self._backup_root)
        except (OSError, shutil.Error) as e:
            raise BackupError(f"Failed to cleanup all backups: {e}") from e

    def list_backups(self) -> list[Path]:
        if not self._backup_root.exists():
            return []
        backups: list[Path] = []
        for entry in sorted(self._backup_root.iterdir()):
            if entry.is_dir():
                for item in sorted(entry.iterdir()):
                    backups.append(item)
        return backups
