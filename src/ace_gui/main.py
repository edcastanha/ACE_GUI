from __future__ import annotations

from pathlib import Path

import flet as ft

from ace_gui.app_state import AppState
from ace_gui.config_manager import ConfigManager
from ace_gui.storage_manager import StorageManager


async def main(page: ft.Page) -> None:
    page.title = "ACE Mod Manager"
    page.theme_mode = ft.ThemeMode.DARK
    page.theme = ft.Theme(color_scheme_seed="blue")
    page.padding = 0
    page.spacing = 0

    config_manager = ConfigManager()
    ace_path_str = config_manager.get("ace_path")
    first_run = config_manager.get("first_run")

    if ace_path_str and not first_run:
        ace_path = Path(ace_path_str)
        if ace_path.exists():
            storage_manager = StorageManager(ace_path)
            state = AppState(page, config_manager, storage_manager, ace_path)
            await state.navigate_to("main")
            return

    state = AppState(page, config_manager, None, None)
    await state.navigate_to("setup")


ft.run(main)
