"""Launch ACE_GUI in web mode and take a screenshot with Playwright."""
import asyncio
import os
import signal
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SRC = os.path.join(ROOT, "src")
PORT = 9098


async def main():
    screenshot_path = os.path.join(ROOT, "screenshot.png")

    env = os.environ.copy()
    env["PYTHONPATH"] = SRC
    env["FLET_FORCE_WEB_SERVER"] = "true"
    env["FLET_SERVER_PORT"] = str(PORT)

    proc = await asyncio.create_subprocess_exec(
        "xvfb-run", sys.executable, "-c", f"""
import sys
sys.path.insert(0, '{SRC}')
import flet as ft

# Replicate the real app setup
from ace_gui.config_manager import ConfigManager
from ace_gui.storage_manager import StorageManager
from ace_gui.app_state import AppState
from ace_gui.views.setup_view import build_setup_view
from ace_gui.views.main_view import build_main_view
from pathlib import Path

async def main(page: ft.Page):
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
""",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        env=env,
    )

    await asyncio.sleep(8)

    from playwright.async_api import async_playwright

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1280, "height": 800})
        url = f"http://localhost:{PORT}"

        try:
            resp = await page.goto(url, timeout=15000, wait_until="networkidle")
            print(f"HTTP {resp.status if resp else 'none'}")
            await asyncio.sleep(2)
            await page.screenshot(path=screenshot_path, full_page=True)
            print(f"SCREENSHOT OK: {screenshot_path}")
        except Exception as e:
            print(f"SCREENSHOT FAILED: {e}")
        finally:
            await browser.close()

    proc.send_signal(signal.SIGTERM)
    await asyncio.sleep(1)
    if proc.returncode is None:
        proc.kill()
    await proc.wait()

    _, stderr = await proc.communicate()
    if stderr:
        for line in stderr.decode().splitlines()[-5:]:
            if "error" in line.lower() or "traceback" in line.lower():
                print(f"[STDERR] {line}")


if __name__ == "__main__":
    asyncio.run(main())
