from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Callable, List, Optional

import flet as ft

from ace_gui.garage_reader import CarInfo, GarageReader
from ace_gui.livery_handler import LiveryHandler

if TYPE_CHECKING:
    from ace_gui.app_state import AppState


class LiveryCarModal:
    def __init__(
        self,
        page: ft.Page,
        state: AppState,
        zip_path: Path,
        livery_handler: LiveryHandler,
        garage_reader: GarageReader,
        on_installed: Optional[Callable] = None,
    ) -> None:
        self.page = page
        self.state = state
        self.zip_path = zip_path
        self.livery_handler = livery_handler
        self.garage_reader = garage_reader
        self.on_installed = on_installed
        self.cars: List[CarInfo] = []
        self.selected_car: Optional[CarInfo] = None
        self.dialog: Optional[ft.AlertDialog] = None

    async def show(self) -> None:
        try:
            self.cars = self.garage_reader.get_cars()
        except Exception:
            self.cars = []

        all_cars_list = ft.ListView(expand=True, spacing=2)
        search_field = ft.TextField(
            label="Search cars...",
            prefix_icon=ft.icons.Icons.SEARCH,
            on_change=lambda e: self._filter(e.control.value, all_cars_list),
        )

        install_btn = ft.Button("Install", disabled=True)

        all_cars_list.controls.clear()
        for car in self.cars:
            car_container = ft.Container(
                content=ft.Column(
                    [
                        ft.Text(car.name, size=16, weight=ft.FontWeight.BOLD),
                        ft.Text(
                            f"GUID: {car.guid} | Profile: {car.profile}",
                            size=11,
                            color=ft.Colors.GREY_400,
                        ),
                    ],
                    spacing=2,
                ),
                padding=12,
                border=ft.border.all(
                    1, ft.Colors.with_opacity(0.1, ft.Colors.WHITE)
                ),
                border_radius=6,
                margin=ft.margin.only(bottom=4),
                on_click=lambda _, c=car: self._select_car(
                    c, install_btn
                ),
            )
            all_cars_list.controls.append(car_container)

        if not self.cars:
            all_cars_list.controls.append(
                ft.Text(
                    "No cars found. Make sure ACE has been launched at least once.",
                    italic=True,
                    color=ft.Colors.GREY_400,
                )
            )

        install_btn.on_click = lambda e: self._install()

        self.dialog = ft.AlertDialog(
            title=ft.Text("Select Car for Livery"),
            content=ft.Container(
                content=ft.Column(
                    [
                        search_field,
                        ft.Container(
                            content=all_cars_list,
                            expand=True,
                            height=400,
                        ),
                    ],
                    spacing=10,
                ),
                width=500,
                height=500,
            ),
            actions=[
                ft.TextButton("Cancel", on_click=self._cancel),
                install_btn,
            ],
            on_dismiss=self._cancel,
        )

        self.page.dialog = self.dialog
        self.dialog.open = True
        self.page.update()

    def _filter(self, query: str, lst: ft.ListView) -> None:
        q = query.lower()
        for control in lst.controls:
            if isinstance(control, ft.Container) and control.content:
                name_text = control.content.controls[0].value.lower()
                control.visible = q in name_text
        lst.update()

    def _select_car(
        self,
        car: CarInfo,
        btn: ft.Button,
    ) -> None:
        self.selected_car = car
        btn.disabled = False
        btn.update()

    async def _install(self) -> None:
        if not self.selected_car or not self.dialog:
            return
        car = self.selected_car
        try:
            self.livery_handler.install(self.zip_path, car.guid)
            self.state.show_snackbar(
                f"Installed livery for {car.name}"
            )
        except Exception as ex:
            self.state.show_snackbar(f"Install failed: {ex}", "red")
        self.dialog.open = False
        self.page.update()
        if self.on_installed:
            await self.on_installed()

    async def _cancel(self, e=None) -> None:
        if self.dialog:
            self.dialog.open = False
            self.page.update()
