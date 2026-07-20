from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, List

import flet as ft

from ace_gui.backup_manager import BackupManager
from ace_gui.garage_reader import GarageReader
from ace_gui.livery_handler import LiveryHandler
from ace_gui.spkg_handler import SpkgHandler
from ace_gui.uninstaller import Uninstaller

if TYPE_CHECKING:
    from ace_gui.app_state import AppState


async def build_main_view(page: ft.Page, state: AppState) -> None:
    page.title = "ACE Mod Manager"
    page.padding = 0

    center_content = ft.Column(expand=True, spacing=10)
    status_text = ft.Text(f"ACE Path: {state.ace_path}", size=12)

    spkg_handler = SpkgHandler(state.storage_manager)
    livery_handler = LiveryHandler(state.storage_manager)
    garage_reader = GarageReader(state.storage_manager)
    backup_manager = BackupManager(state.storage_manager.base_path / ".backups")
    uninstaller = Uninstaller(state.storage_manager, backup_manager)

    # ----- Mods -----

    def build_mod_item(name: str, mod_path: Path) -> ft.Container:
        return ft.Container(
            content=ft.Row(
                [
                    ft.Column(
                        [
                            ft.Text(name, size=16, weight=ft.FontWeight.BOLD),
                        ],
                        expand=True,
                    ),
                    ft.IconButton(
                        icon=ft.icons.Icons.DELETE_OUTLINE,
                        icon_color=ft.Colors.RED_400,
                        tooltip="Delete mod",
                        on_click=lambda _, p=mod_path, n=name: delete_mod(p, n),
                    ),
                ],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=15,
            border=ft.border.all(1, ft.Colors.with_opacity(0.15, ft.Colors.WHITE)),
            border_radius=8,
            margin=ft.margin.only(bottom=5),
        )

    async def load_mods() -> None:
        center_content.controls.clear()
        center_content.controls.append(
            ft.Row(
                [
                    ft.Text("Mods", size=22, weight=ft.FontWeight.BOLD),
                    ft.Button(
                        "Install Mod",
                        icon=ft.icons.Icons.UPLOAD_FILE,
                        on_click=install_mod_click,
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            )
        )

        mods_dir = state.storage_manager.mods_dir
        if not mods_dir.exists():
            center_content.controls.append(
                ft.Text("No mods directory found.", italic=True)
            )
            page.update()
            return

        mods_list = ft.ListView(expand=True, spacing=5)
        entries: List[Path] = sorted(
            mods_dir.iterdir(), key=lambda p: p.name.lower()
        )
        for entry in entries:
            if entry.is_dir():
                mods_list.controls.append(build_mod_item(entry.name, entry))

        if not mods_list.controls:
            mods_list.controls.append(
                ft.Text("No mods installed.", italic=True)
            )

        center_content.controls.append(mods_list)
        page.update()

    mod_file_picker = ft.FilePicker()
    livery_file_picker = ft.FilePicker()

    async def install_mod_click(e) -> None:
        await mod_file_picker.pick_files(allowed_extensions=["spkg"])

    async def on_mod_picked(e: ft.FilePickerResultEvent) -> None:
        if not e.files or not e.files[0].path:
            return
        src = Path(e.files[0].path)
        progress = ft.ProgressRing(width=20, height=20)
        center_content.controls.append(progress)
        page.update()
        try:
            spkg_handler.install(src)
            state.show_snackbar(f"Installed mod: {src.name}")
        except FileExistsError:
            state.show_snackbar(f"Mod already installed: {src.name}", "orange")
        except Exception as ex:
            state.show_snackbar(f"Install failed: {ex}", "red")
        finally:
            if progress in center_content.controls:
                center_content.controls.remove(progress)
        await load_mods()

    async def delete_mod(path: Path, name: str) -> None:
        try:
            uninstaller.uninstall_mod(name)
            state.show_snackbar(f"Deleted: {name}")
        except Exception as ex:
            state.show_snackbar(f"Delete failed: {ex}", "red")
        await load_mods()

    # ----- Liveries -----

    def build_livery_item(
        livery_path: Path, car_guid: str
    ) -> ft.Container:
        return ft.Container(
            content=ft.Row(
                [
                    ft.Text(f"  {livery_path.name}", expand=True),
                    ft.IconButton(
                        icon=ft.icons.Icons.DELETE_OUTLINE,
                        icon_color=ft.Colors.RED_400,
                        tooltip="Delete livery",
                        on_click=lambda _, p=livery_path: delete_livery(p),
                    ),
                ],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.padding.only(left=20, right=10, top=5, bottom=5),
        )

    async def load_liveries() -> None:
        center_content.controls.clear()
        center_content.controls.append(
            ft.Row(
                [
                    ft.Text("Liveries", size=22, weight=ft.FontWeight.BOLD),
                    ft.Button(
                        "Install Livery",
                        icon=ft.icons.Icons.UPLOAD_FILE,
                        on_click=install_livery_click,
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            )
        )

        liveries_dir = state.storage_manager.liveries_dir
        if not liveries_dir.exists():
            center_content.controls.append(
                ft.Text("No liveries directory found.", italic=True)
            )
            page.update()
            return

        car_names = {}
        try:
            for car in garage_reader.get_cars():
                car_names[car.guid] = car.name
        except Exception:
            pass

        livery_groups: dict[str, list[Path]] = {}
        for entry in sorted(liveries_dir.iterdir(), key=lambda p: p.name.lower()):
            if entry.is_dir():
                guid = entry.name
                label = car_names.get(guid, f"Car ({guid[:8]}...)")
                livery_groups.setdefault(label, []).append(entry)

        liveries_list = ft.ListView(expand=True, spacing=5)

        if not livery_groups:
            liveries_list.controls.append(
                ft.Text("No liveries installed.", italic=True)
            )
        else:
            for car_label in sorted(livery_groups.keys()):
                liveries_list.controls.append(
                    ft.Container(
                        content=ft.Text(
                            car_label,
                            size=16,
                            weight=ft.FontWeight.BOLD,
                        ),
                        padding=ft.padding.only(top=10, bottom=5),
                    )
                )
                for lp in livery_groups[car_label]:
                    liveries_list.controls.append(
                        build_livery_item(lp, lp.name)
                    )

        center_content.controls.append(liveries_list)
        page.update()

    async def install_livery_click(e) -> None:
        await livery_file_picker.pick_files(allowed_extensions=["zip"])

    async def on_livery_picked(e: ft.FilePickerResultEvent) -> None:
        if not e.files or not e.files[0].path:
            return
        src = Path(e.files[0].path)
        from ace_gui.views.livery_modal import LiveryCarModal

        modal = LiveryCarModal(
            page=page,
            state=state,
            zip_path=src,
            livery_handler=livery_handler,
            garage_reader=garage_reader,
            on_installed=load_liveries,
        )
        await modal.show()

    async def delete_livery(livery_path: Path) -> None:
        try:
            state.storage_manager.delete_path(livery_path)
            car_dir = livery_path.parent
            if car_dir.exists() and not any(car_dir.iterdir()):
                car_dir.rmdir()
            state.show_snackbar(f"Deleted: {livery_path.name}")
        except Exception as ex:
            state.show_snackbar(f"Delete failed: {ex}", "red")
        await load_liveries()

    mod_file_picker.on_result = on_mod_picked
    livery_file_picker.on_result = on_livery_picked
    page.overlay.extend([mod_file_picker, livery_file_picker])

    # ----- Tab switching -----

    async def switch_tab(index: int) -> None:
        if index == 0:
            await load_mods()
        else:
            await load_liveries()

    # ----- Layout -----

    tabs = ft.Tabs(
        selected_index=0,
        on_change=lambda e: switch_tab(e.control.selected_index),
        tabs=[
            ft.Tab(text="Mods"),
            ft.Tab(text="Liveries"),
        ],
    )

    sidebar = ft.Container(
        content=ft.Column(
            [
                ft.Text(
                    "Navigation",
                    size=14,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.GREY_400,
                ),
                tabs,
            ],
            spacing=10,
        ),
        width=300,
        bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.WHITE),
        padding=ft.padding.all(15),
    )

    central_panel = ft.Container(
        content=center_content,
        expand=True,
        padding=ft.padding.all(20),
    )

    status_bar = ft.Container(
        content=status_text,
        padding=ft.padding.symmetric(horizontal=15, vertical=5),
        bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.WHITE),
    )

    page.add(
        ft.Column(
            [
                ft.Row([sidebar, central_panel], expand=True, spacing=0),
                status_bar,
            ],
            expand=True,
            spacing=0,
        )
    )

    await load_mods()
