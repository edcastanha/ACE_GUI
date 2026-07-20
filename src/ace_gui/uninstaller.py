import logging
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional

from .backup_manager import BackupError, BackupManager
from .storage_manager import StorageManager

logger = logging.getLogger(__name__)


@dataclass
class UninstallResult:
    success: bool
    content_name: str
    content_type: str
    backup_restored: bool = False
    error_message: Optional[str] = None


@dataclass
class UninstallLogEntry:
    timestamp: str
    content_name: str
    content_type: str
    status: str
    error: Optional[str] = None
    backup_restored: bool = False


class Uninstaller:
    def __init__(self, storage_manager: StorageManager, backup_manager: BackupManager) -> None:
        self._storage = storage_manager
        self._backup = backup_manager
        self._log: list[UninstallLogEntry] = []

    def uninstall_mod(self, mod_name: str) -> UninstallResult:
        mod_path = self._storage.mods_dir / mod_name
        if not mod_path.exists():
            return UninstallResult(
                success=False,
                content_name=mod_name,
                content_type="mod",
                error_message=f"Mod not found: {mod_name}",
            )

        backup_path: Optional[Path] = None
        try:
            backup_path = self._backup.create_backup(mod_path)
            self._storage.delete_path(mod_path)
            self._cleanup_empty_parents(mod_path)
            self._log.append(
                UninstallLogEntry(
                    timestamp=datetime.now().isoformat(),
                    content_name=mod_name,
                    content_type="mod",
                    status="success",
                )
            )
            return UninstallResult(success=True, content_name=mod_name, content_type="mod")
        except Exception as e:
            error_msg = str(e)
            backup_restored = False
            if backup_path is not None:
                try:
                    self._backup.restore(backup_path, mod_path)
                    backup_restored = True
                except BackupError:
                    pass
            self._log.append(
                UninstallLogEntry(
                    timestamp=datetime.now().isoformat(),
                    content_name=mod_name,
                    content_type="mod",
                    status="failed",
                    error=error_msg,
                    backup_restored=backup_restored,
                )
            )
            return UninstallResult(
                success=False,
                content_name=mod_name,
                content_type="mod",
                backup_restored=backup_restored,
                error_message=error_msg,
            )

    def uninstall_livery(self, car_guid: str, livery_name: str) -> UninstallResult:
        livery_path = self._storage.liveries_dir / car_guid / livery_name
        if not livery_path.exists():
            return UninstallResult(
                success=False,
                content_name=livery_name,
                content_type="livery",
                error_message=f"Livery not found: {livery_name}",
            )

        backup_path: Optional[Path] = None
        try:
            backup_path = self._backup.create_backup(livery_path)
            self._storage.delete_path(livery_path)
            car_dir = self._storage.liveries_dir / car_guid
            if car_dir.exists() and not any(car_dir.iterdir()):
                car_dir.rmdir()
            self._log.append(
                UninstallLogEntry(
                    timestamp=datetime.now().isoformat(),
                    content_name=livery_name,
                    content_type="livery",
                    status="success",
                )
            )
            return UninstallResult(success=True, content_name=livery_name, content_type="livery")
        except Exception as e:
            error_msg = str(e)
            backup_restored = False
            if backup_path is not None:
                try:
                    self._backup.restore(backup_path, livery_path)
                    backup_restored = True
                except BackupError:
                    pass
            self._log.append(
                UninstallLogEntry(
                    timestamp=datetime.now().isoformat(),
                    content_name=livery_name,
                    content_type="livery",
                    status="failed",
                    error=error_msg,
                    backup_restored=backup_restored,
                )
            )
            return UninstallResult(
                success=False,
                content_name=livery_name,
                content_type="livery",
                backup_restored=backup_restored,
                error_message=error_msg,
            )

    def _cleanup_empty_parents(self, path: Path) -> None:
        boundaries = {self._storage.mods_dir, self._storage.liveries_dir, self._storage.base_path}
        for parent in path.parents:
            if parent in boundaries:
                break
            if parent.exists() and not any(parent.iterdir()):
                try:
                    parent.rmdir()
                except OSError:
                    break
            else:
                break
