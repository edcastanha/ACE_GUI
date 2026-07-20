from __future__ import annotations

import json
from pathlib import Path

import pytest

from ace_gui.config_manager import ConfigManager, DEFAULT_CONFIG


class TestConfigManager:
    def test_default_values_on_first_load(self, tmp_path: Path) -> None:
        cm = ConfigManager(config_dir=tmp_path)
        assert cm.get("ace_path") is None
        assert cm.get("first_run") is True
        assert cm.get("nonexistent") is None

    def test_set_get_roundtrip(self, tmp_path: Path) -> None:
        cm = ConfigManager(config_dir=tmp_path)
        cm.set("ace_path", "/usr/bin/ace")
        assert cm.get("ace_path") == "/usr/bin/ace"
        cm.set("first_run", False)
        assert cm.get("first_run") is False

    def test_save_load_persistence(self, tmp_path: Path) -> None:
        cm1 = ConfigManager(config_dir=tmp_path)
        cm1.set("ace_path", "/opt/ace/ace")
        cm1.set("first_run", False)

        cm2 = ConfigManager(config_dir=tmp_path)
        assert cm2.get("ace_path") == "/opt/ace/ace"
        assert cm2.get("first_run") is False

    def test_corruption_recovery(self, tmp_path: Path) -> None:
        config_dir = tmp_path / "ace_gui"
        config_dir.mkdir(parents=True)
        config_file = config_dir / "config.json"

        config_file.write_text("this is not valid json{")

        cm = ConfigManager(config_dir=config_dir)
        assert cm.get("ace_path") is None
        assert cm.get("first_run") is True

        backup = config_file.with_suffix(".json.bak")
        assert backup.exists()
        with backup.open("r") as f:
            assert f.read() == "this is not valid json{"

        with config_file.open("r") as f:
            recovered = json.load(f)
        assert recovered == DEFAULT_CONFIG
