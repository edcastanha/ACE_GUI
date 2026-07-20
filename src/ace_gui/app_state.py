from __future__ import annotations

from pathlib import Path
from typing import Optional

import flet as ft

from ace_gui.config_manager import ConfigManager
from ace_gui.storage_manager import StorageManager


class AppState:
    def __init__(
        self,
        page: ft.Page,
        config_manager: ConfigManager,
        storage_manager: Optional[StorageManager] = None,
        ace_path: Optional[Path] = None,
    ) -> None:
        self.page = page
        self.config_manager = config_manager
        self.storage_manager = storage_manager
        self.ace_path = ace_path

    async def navigate_to(self, view_name: str) -> None:
        self.page.clean()
        self.page.overlay.clear()
        if view_name == "setup":
            from ace_gui.views.setup_view import build_setup_view

            await build_main_view(self.page, self)
        elif view_name == "main":
            from ace_gui.views.main_view import build_main_view

            await build_main_view(self.page, self)

    def show_snackbar(self, message: str, color: str = "green") -> None:
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(message),
            bgcolor=color,
        )
        self.page.snack_bar.open = True
        self.page.update()
