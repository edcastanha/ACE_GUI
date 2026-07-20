import json
import os
import signal
import socket
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import pytest

HERE = Path(__file__).parent
ROOT = HERE.parent
SRC = ROOT / "src"
VENV_PY = ROOT / ".venv" / "bin" / "python3"


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        return s.getsockname()[1]


def _wait_for_server(port: int, timeout: float = 15) -> bool:
    start = time.monotonic()
    while time.monotonic() - start < timeout:
        try:
            with socket.create_connection(("localhost", port), timeout=1):
                return True
        except (ConnectionRefusedError, OSError, TimeoutError):
            time.sleep(0.3)
    return False


def _render_app_script(config_dir: str, mock_ace_dir: str | None) -> str:
    """Python source that starts ACE_GUI as a Flet web server.

    When *mock_ace_dir* is provided, the config is pre-populated so the
    app boots into the main view.  Otherwise it stays in first-run/setup
    mode (no ace_path set).
    """
    parts = [
        "import sys",
        f"sys.path.insert(0, {str(SRC)!r})",
        "import flet as ft",
        "from ace_gui.app_state import AppState",
        "from ace_gui.config_manager import ConfigManager",
        "from ace_gui.storage_manager import StorageManager",
        "from ace_gui.views.setup_view import build_setup_view",
        "from ace_gui.views.main_view import build_main_view",
        "from pathlib import Path",
    ]

    if mock_ace_dir:
        ace_path = Path(mock_ace_dir).as_posix()
        parts += [
            "import json, os",
            f'cfg_dir = {config_dir!r}',
            "os.makedirs(cfg_dir, exist_ok=True)",
            f'json.dump({{"ace_path": {ace_path!r}, "first_run": False}}, '
            f'open(os.path.join(cfg_dir, "config.json"), "w"))',
        ]

    parts += [
        "async def main(page: ft.Page):",
        '    page.title = "ACE Mod Manager"',
        "    page.theme_mode = ft.ThemeMode.DARK",
        '    page.theme = ft.Theme(color_scheme_seed="blue")',
        "    page.padding = 0",
        "    page.spacing = 0",
        f'    cm = ConfigManager(config_dir=Path({config_dir!r}))',
        '    ace_path_str = cm.get("ace_path")',
        '    first_run = cm.get("first_run")',
        "    if ace_path_str and not first_run:",
        "        ace_path = Path(ace_path_str)",
        "        if ace_path.exists():",
        "            sm = StorageManager(ace_path)",
        "            state = AppState(page, cm, sm, ace_path)",
        "            await state.navigate_to('main')",
        "            return",
        "    state = AppState(page, cm, None, None)",
        "    await state.navigate_to('setup')",
        "ft.run(main)",
    ]
    return "\n".join(parts)


@pytest.fixture
def temp_config_dir() -> Path:
    with tempfile.TemporaryDirectory(prefix="ace_gui_test_") as d:
        yield Path(d)


@pytest.fixture
def mock_ace_dir(tmp_path) -> Path:
    ace = tmp_path / "ace_saves"
    (ace / "Mods").mkdir(parents=True)
    (ace / "External Liveries").mkdir(parents=True)
    pd = ace / "profile_data" / "default" / "saved_cars"
    pd.mkdir(parents=True)
    (pd / "ferrari_488.json").write_text(
        json.dumps({"carname": "Ferrari 488 GT3", "carguide": "abc123-def456"})
    )
    (pd / "porsche_911.json").write_text(
        json.dumps({"carname": "Porsche 911 GT3 R", "carguide": "xyz789-uvw101"})
    )
    return ace


@pytest.fixture
def gui_setup_server(temp_config_dir):
    """Flet web em modo first-run (tela Setup)."""
    port = _free_port()
    script = _render_app_script(str(temp_config_dir), mock_ace_dir=None)
    proc = subprocess.Popen(
        ["xvfb-run", "--auto-servernum", str(VENV_PY), "-c", script],
        env={
            **os.environ,
            "PYTHONPATH": str(SRC),
            "FLET_FORCE_WEB_SERVER": "true",
            "FLET_SERVER_PORT": str(port),
        },
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    assert _wait_for_server(port), f"Setup server did not start on port {port}"
    yield f"http://localhost:{port}"
    proc.terminate()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()


@pytest.fixture
def gui_main_server(temp_config_dir, mock_ace_dir):
    """Flet web em modo principal (tela Main, já configurada)."""
    port = _free_port()
    script = _render_app_script(str(temp_config_dir), str(mock_ace_dir))
    proc = subprocess.Popen(
        ["xvfb-run", "--auto-servernum", str(VENV_PY), "-c", script],
        env={
            **os.environ,
            "PYTHONPATH": str(SRC),
            "FLET_FORCE_WEB_SERVER": "true",
            "FLET_SERVER_PORT": str(port),
        },
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
    )
    ready = _wait_for_server(port)
    if not ready:
        _, err = proc.communicate(timeout=2)
        raise RuntimeError(
            f"Main server did not start on port {port}\n"
            f"stderr:\n{(err or b'').decode()[-2000:]}"
        )
    yield f"http://localhost:{port}", mock_ace_dir
    proc.terminate()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()


@pytest.fixture
def gui_setup_page(gui_setup_server, page):
    page.goto(gui_setup_server, wait_until="networkidle")
    page.wait_for_timeout(1000)
    return page


@pytest.fixture
def gui_main_page(gui_main_server, page):
    url, mock_ace_dir = gui_main_server
    page.goto(url, wait_until="networkidle")
    page.wait_for_timeout(1500)
    return page, mock_ace_dir
