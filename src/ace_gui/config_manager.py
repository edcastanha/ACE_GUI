from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any, Optional


DEFAULT_CONFIG: dict[str, Any] = {
    "ace_path": None,
    "first_run": True,
}

_CONFIG_FILENAME = "config.json"
_BACKUP_SUFFIX = ".bak"


def _default_config_dir() -> Path:
    if sys.platform == "win32":
        base = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
    elif sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support"
    else:
        base = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
    return base / "ACE_GUI"


class ConfigManager:
    def __init__(self, config_dir: Optional[Path] = None) -> None:
        self._config_dir = config_dir if config_dir is not None else _default_config_dir()
        self._config_file = self._config_dir / _CONFIG_FILENAME
        self._config: dict[str, Any] = {}
        self.load()

    def get(self, key: str) -> Any:
        return self._config.get(key)

    def set(self, key: str, value: Any) -> None:
        self._config[key] = value
        self.save()

    def load(self) -> dict[str, Any]:
        self._config_dir.mkdir(parents=True, exist_ok=True)

        if not self._config_file.exists():
            self._config = dict(DEFAULT_CONFIG)
            self.save()
            return dict(self._config)

        try:
            with self._config_file.open("r", encoding="utf-8") as f:
                data = json.load(f)
            self._config = data
        except (json.JSONDecodeError, OSError):
            backup = self._config_file.with_suffix(
                self._config_file.suffix + _BACKUP_SUFFIX
            )
            try:
                self._config_file.rename(backup)
            except OSError:
                pass
            self._config = dict(DEFAULT_CONFIG)
            self.save()

        return dict(self._config)

    def save(self) -> None:
        self._config_dir.mkdir(parents=True, exist_ok=True)
        with self._config_file.open("w", encoding="utf-8") as f:
            json.dump(self._config, f, indent=2)
