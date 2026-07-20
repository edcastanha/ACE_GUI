from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import flet as ft

from ace_gui.path_detector import auto_detect_path
from ace_gui.storage_manager import StorageManager

if TYPE_CHECKING:
    from ace_gui.app_state import AppState


async def build_setup_view(page: ft.Page, state: AppState) -> None:
    page.title = "ACE Mod Manager - Setup"
    page.padding = 40

    detected = auto_detect_path()

    path_field = ft.TextField(
        label="ACE Saved Games Path",
        value=str(detected.path) if detected.found else "",
        hint_text="Select or type the path to your ACE Saved Games folder",
        expand=True,
    )

    status_text = ft.Text(
        f"Auto-detected: {detected.path}"
        if detected.found
        else "Could not auto-detect path",
        size=12,
        italic=True,
    )

    file_picker = ft.FilePicker()

    def on_pick_directory(e: ft.FilePickerResultEvent) -> None:
        if e.path:
            path_field.value = e.path
            page.update()

    file_picker.on_result = on_pick_directory
    page.overlay.append(file_picker)
    page.update()

    async def browse_click(e) -> None:
        await file_picker.get_directory_path()

    async def confirm_click(e) -> None:
        path_str = path_field.value.strip()
        if not path_str:
            state.show_snackbar("Please select a path", "red")
            return
        path = Path(path_str)
        if not path.exists():
            state.show_snackbar("Selected path does not exist", "red")
            return
        mgr = StorageManager(path)
        if not mgr.validate_ace_path():
            state.show_snackbar(
                "Invalid ACE path — missing Mods/ or External Liveries/ directory",
                "red",
            )
            return
        state.config_manager.set("ace_path", str(path))
        state.config_manager.set("first_run", False)
        state.ace_path = path
        state.storage_manager = StorageManager(path)
        state.storage_manager.ensure_dirs()
        await state.navigate_to("main")

    page.add(
        ft.Container(
            content=ft.Column(
                [
                    ft.Text(
                        "ACE Mod Manager - Setup",
                        size=28,
                        weight=ft.FontWeight.BOLD,
                    ),
                    ft.Container(height=20),
                    ft.Text(
                        "Configure your ACE Saved Games path:",
                        size=16,
                    ),
                    ft.Container(height=10),
                    ft.Row(
                        [
                            path_field,
                            ft.ElevatedButton(
                                "Browse",
                                icon=ft.icons.Icons.FOLDER_OPEN,
                                on_click=browse_click,
                            ),
                        ],
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    status_text,
                    ft.Container(height=20),
                    ft.ElevatedButton(
                        "Confirm",
                        icon=ft.icons.Icons.CHECK,
                        on_click=confirm_click,
                    ),
                ],
                width=600,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            alignment=ft.alignment.Alignment.CENTER,
            expand=True,
        )
    )
    page.update()
