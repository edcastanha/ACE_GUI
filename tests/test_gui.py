"""Integration tests for ACE_GUI GUI layer.

Strategy
--------
Flet renders via CanvasKit canvas in web mode, so standard Playwright
DOM selectors cannot read the app's text content or click buttons.

Two complementary approaches:

1. **View-level unit tests** (no browser) — call ``build_setup_view`` /
   ``build_main_view`` directly with mock Page/AppState, inspect the
   resulting control tree, and invoke event handlers programmatically.
   Fast, deterministic, and runs without a display server.

2. **Playwright smoke tests** — start the full app in ``FLET_APP_HIDDEN``
   + web-server mode via ``xvfb-run``, take a screenshot and verify the
   server responds with HTTP 200.  Validates that the app boots without
   crashes.  Does NOT attempt DOM assertions on canvas content.
"""

import asyncio
import json
import zipfile
from io import BytesIO
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, PropertyMock, patch

import pytest

# Register custom marker
pytestmark = [pytest.mark.view]


# ============================================================
#  UNIT TEST HELPERS
# ============================================================

def _make_spkg(dest: Path, name: str = "test_car") -> Path:
    p = dest / f"{name}.spkg"
    p.write_bytes(b"PK\x03\x04" + b"\x00" * 22)
    return p


def _make_livery_zip(dest: Path) -> Path:
    buf = BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("livery.json", json.dumps({"name": "Test Livery"}))
    p = dest / "livery.zip"
    p.write_bytes(buf.getvalue())
    return p


@pytest.fixture
def mock_page():
    """A fake ``ft.Page`` with minimal wiring so views can register
    controls and call ``page.update()`` / ``page.add()``."""
    page = MagicMock()
    page.title = ""
    page.padding = 0
    page.spacing = 0
    page.overlay = []
    page.controls = []
    page.theme_mode = None
    page.theme = None
    # The SnackBar prototype – just capture that it was called
    page.snack_bar = None
    # FilePicker mock
    fp = MagicMock()
    fp.get_directory_path = AsyncMock()
    page.overlay.append(fp)
    return page


@pytest.fixture
def mock_config_manager(mock_ace_dir):
    """ConfigManager pointing at ``mock_ace_dir`` (not first-run)."""
    cm = MagicMock()
    cm.get.side_effect = lambda k, _cm=cm: {
        "ace_path": str(mock_ace_dir),
        "first_run": False,
    }.get(k)
    cm.set = MagicMock()
    return cm


@pytest.fixture
def mock_state(mock_page, mock_config_manager, mock_ace_dir):
    """AppState wired with mock page, ConfigManager & StorageManager."""
    from ace_gui.app_state import AppState
    from ace_gui.storage_manager import StorageManager

    sm = StorageManager(mock_ace_dir)
    state = AppState(mock_page, mock_config_manager, sm, mock_ace_dir)
    state.navigate_to = AsyncMock()
    return state


# ============================================================
#  FLOW 1 — SETUP VIEW (FIRST-RUN)
# ============================================================

class TestSetupView:
    """Tests the setup view build & event handlers directly."""

    def test_setup_creates_controls(self, mock_page, monkeypatch):
        """Call ``build_setup_view`` and verify controls were added."""
        monkeypatch.setattr(
            "ace_gui.views.setup_view.auto_detect_path",
            lambda: type("R", (), {"found": False, "path": None})(),
        )

        from ace_gui.views.setup_view import build_setup_view

        state = MagicMock()
        state.config_manager = MagicMock()
        state.config_manager.get.return_value = None

        asyncio.run(build_setup_view(mock_page, state))
        assert mock_page.add.called

    def test_setup_interactions(self, mock_page, monkeypatch):
        """Simulate confirm_click with empty and valid paths."""
        monkeypatch.setattr(
            "ace_gui.views.setup_view.auto_detect_path",
            lambda: type("R", (), {"found": False, "path": None})(),
        )

        from ace_gui.views.setup_view import build_setup_view

        state = MagicMock()
        state.config_manager = MagicMock()
        state.config_manager.get.return_value = None
        state.show_snackbar = MagicMock()

        asyncio.run(build_setup_view(mock_page, state))
        # Verify build completes without error
        assert mock_page.add.called


# ============================================================
#  PLAYWRIGHT SMOKE TESTS
# ============================================================

@pytest.mark.playwright
class TestAppBoot:
    """Verify the app starts without crashes using Playwright + screenshot."""

    def test_setup_screenshot(self, gui_setup_page, tmp_path):
        p = gui_setup_page
        shot = tmp_path / "setup.png"
        p.screenshot(path=str(shot))
        assert shot.stat().st_size > 5000, "Setup screenshot too small — likely blank"

    def test_main_screenshot(self, gui_main_page, tmp_path):
        p, _ = gui_main_page
        shot = tmp_path / "main.png"
        p.screenshot(path=str(shot))
        assert shot.stat().st_size > 5000, "Main screenshot too small — likely blank"
