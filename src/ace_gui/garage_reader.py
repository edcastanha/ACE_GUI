from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from ace_gui.storage_manager import StorageManager


@dataclass
class CarInfo:
    name: str
    guid: str
    profile: str


class GarageReader:
    def __init__(self, storage_manager: StorageManager) -> None:
        self._storage = storage_manager

    def get_cars(self) -> List[CarInfo]:
        seen: set[str] = set()
        cars: list[CarInfo] = []

        for profile_dir in self._scan_profiles():
            saved_dir = profile_dir / "saved_cars"
            if not saved_dir.is_dir():
                continue
            for car_file in sorted(saved_dir.glob("*.json")):
                try:
                    data = json.loads(car_file.read_text(encoding="utf-8"))
                except (json.JSONDecodeError, OSError):
                    continue
                if not isinstance(data, dict):
                    continue
                guid = data.get("carguide") or data.get("guid") or ""
                name = data.get("carname") or data.get("name") or car_file.stem
                if guid and guid not in seen:
                    seen.add(guid)
                    cars.append(
                        CarInfo(
                            name=str(name),
                            guid=str(guid),
                            profile=profile_dir.name,
                        )
                    )

        return cars

    def _scan_profiles(self) -> List[Path]:
        profiles_dir = self._storage.base_path / "profile_data"
        if not profiles_dir.is_dir():
            return []
        return sorted(
            p for p in profiles_dir.iterdir() if p.is_dir()
        )
