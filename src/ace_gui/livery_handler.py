from __future__ import annotations

import json
import shutil
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from ace_gui.storage_manager import StorageManager


class LiveryHandler:
    def __init__(self, storage_manager: StorageManager) -> None:
        self._storage = storage_manager

    def install(self, zip_path: Path, car_guid: str) -> Path:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_dir = Path(tmp)
            self._storage.extract_zip(zip_path, tmp_dir)

            json_path = self._find_livery_json(tmp_dir)
            if json_path is None:
                raise FileNotFoundError(
                    f"No JSON config found in livery zip: {zip_path}"
                )

            self._inject_guid(json_path, car_guid)

            final_dir = self._storage.liveries_dir / car_guid
            if final_dir.exists():
                shutil.rmtree(final_dir)
            final_dir.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(src=tmp_dir, dst=final_dir)

        return final_dir

    def _find_livery_json(self, directory: Path) -> Optional[Path]:
        for child in sorted(directory.iterdir()):
            if child.suffix == ".json" and child.is_file():
                return child
        return None

    def _inject_guid(self, json_path: Path, car_guid: str) -> None:
        data = json.loads(json_path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            data = {}
        data["carguide"] = car_guid
        json_path.write_text(
            json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8"
        )
