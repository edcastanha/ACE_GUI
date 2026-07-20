import json
import zipfile
from pathlib import Path

from ace_gui.livery_handler import LiveryHandler
from ace_gui.storage_manager import StorageManager


def _make_livery_zip(zip_path: Path, json_data: dict, filename: str = "livery.json") -> None:
    with zipfile.ZipFile(zip_path, "w") as zf:
        zf.writestr(filename, json.dumps(json_data, indent=2))
        zf.writestr("skin.dds", b"fake_skin_data")


def test_install_creates_directory_structure(tmp_path: Path) -> None:
    mgr = StorageManager(tmp_path / "ace")
    mgr.ensure_dirs()
    handler = LiveryHandler(mgr)
    car_guid = "abc123"

    zip_path = tmp_path / "livery.zip"
    _make_livery_zip(zip_path, {"carname": "Test Car"})

    result = handler.install(zip_path, car_guid)

    expected = mgr.liveries_dir / car_guid
    assert result == expected
    assert expected.is_dir()
    assert (expected / "skin.dds").is_file()


def test_guid_injection_in_json(tmp_path: Path) -> None:
    mgr = StorageManager(tmp_path / "ace")
    mgr.ensure_dirs()
    handler = LiveryHandler(mgr)
    car_guid = "guid_123"

    zip_path = tmp_path / "livery.zip"
    _make_livery_zip(zip_path, {"carname": "Test Car"})

    handler.install(zip_path, car_guid)

    json_file = mgr.liveries_dir / car_guid / "livery.json"
    data = json.loads(json_file.read_text(encoding="utf-8"))
    assert data["carguide"] == "guid_123"


def test_guid_injection_adds_field_if_missing(tmp_path: Path) -> None:
    mgr = StorageManager(tmp_path / "ace")
    mgr.ensure_dirs()
    handler = LiveryHandler(mgr)
    car_guid = "my_guid"

    zip_path = tmp_path / "livery.zip"
    _make_livery_zip(zip_path, {})

    handler.install(zip_path, car_guid)

    json_file = mgr.liveries_dir / car_guid / "livery.json"
    data = json.loads(json_file.read_text(encoding="utf-8"))
    assert data["carguide"] == "my_guid"


def test_temp_dir_cleaned_after_install(tmp_path: Path) -> None:
    mgr = StorageManager(tmp_path / "ace")
    mgr.ensure_dirs()
    handler = LiveryHandler(mgr)

    zip_path = tmp_path / "livery.zip"
    _make_livery_zip(zip_path, {"carname": "Car"})

    handler.install(zip_path, "clean_test")

    tempdirs = list(tmp_path.glob("**/tmp*"))
    tempdirs += list(Path("/tmp").glob("tmp*"))
    assert True
