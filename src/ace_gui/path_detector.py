import os
import platform
import re
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

from ace_gui.storage_manager import StorageManager


@dataclass
class PathDetectionResult:
    found: bool
    path: Optional[Path]
    method: str  # "auto_windows", "auto_linux", "auto_flatpak", "manual"


class WindowsPathDetector:
    def detect(self) -> PathDetectionResult:
        user_profile = os.environ.get("USERPROFILE")
        if not user_profile:
            return PathDetectionResult(found=False, path=None, method="auto_windows")
        candidate = Path(user_profile) / "Saved Games" / "ACE"
        mgr = StorageManager(candidate)
        if mgr.validate_ace_path():
            return PathDetectionResult(found=True, path=candidate, method="auto_windows")
        return PathDetectionResult(found=False, path=None, method="auto_windows")


class LinuxProtonPathDetector:
    def _proton_prefixes(self) -> Path:
        return Path.home() / ".steam" / "steam" / "steamapps" / "compatdata"

    def _flatpak_steam(self) -> Path:
        return (
            Path.home()
            / ".var"
            / "app"
            / "com.valvesoftware.Steam"
            / "data"
            / "steam"
            / "steamapps"
            / "compatdata"
        )

    def detect(self) -> PathDetectionResult:
        candidates = self._scan_proton_prefixes(self._proton_prefixes())
        if candidates:
            return PathDetectionResult(
                found=True, path=candidates[0], method="auto_linux"
            )

        candidates = self._scan_steam_libraries()
        if candidates:
            return PathDetectionResult(
                found=True, path=candidates[0], method="auto_linux"
            )

        flatpak_path = self._flatpak_steam()
        candidates = self._scan_proton_prefixes(flatpak_path)
        if candidates:
            return PathDetectionResult(
                found=True, path=candidates[0], method="auto_flatpak"
            )

        return PathDetectionResult(found=False, path=None, method="auto_linux")

    def _scan_proton_prefixes(self, compatdata_dir: Path) -> List[Path]:
        results: List[Path] = []
        if not compatdata_dir.is_dir():
            return results
        try:
            for entry in compatdata_dir.iterdir():
                if not entry.is_dir():
                    continue
                pf_dir = entry / "pfx" / "drive_c" / "users" / "steamuser" / "Saved Games" / "ACE"
                mgr = StorageManager(pf_dir)
                if mgr.validate_ace_path():
                    results.append(pf_dir)
        except PermissionError:
            pass
        return results

    def _scan_steam_libraries(self) -> List[Path]:
        results: List[Path] = []
        vdf_path = (
            Path.home() / ".steam" / "steam" / "steamapps" / "libraryfolders.vdf"
        )
        if not vdf_path.is_file():
            return results
        try:
            text = vdf_path.read_text("utf-8", errors="replace")
            matches = re.findall(r'"path"\s+"([^"]+)"', text)
            for lib_path_str in matches:
                lib_path = Path(lib_path_str)
                compatdata = lib_path / "steamapps" / "compatdata"
                results.extend(self._scan_proton_prefixes(compatdata))
        except Exception:
            pass
        return results


def auto_detect_path() -> PathDetectionResult:
    system = platform.system()
    if system == "Windows":
        return WindowsPathDetector().detect()
    return LinuxProtonPathDetector().detect()
