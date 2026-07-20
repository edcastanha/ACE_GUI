import json
from pathlib import Path

from ace_gui.garage_reader import CarInfo, GarageReader
from ace_gui.storage_manager import StorageManager


def _make_car_json(profile_dir: Path, filename: str, data: dict) -> Path:
    saved_dir = profile_dir / "saved_cars"
    saved_dir.mkdir(parents=True, exist_ok=True)
    path = saved_dir / filename
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return path


def test_reads_car_info_from_saved_cars(tmp_path: Path) -> None:
    base = tmp_path / "ace"
    mgr = StorageManager(base)
    reader = GarageReader(mgr)

    profile = base / "profile_data" / "profile1"
    _make_car_json(profile, "car_1.json", {
        "carname": "Ferrari F2004",
        "carguide": "abc-123",
    })

    cars = reader.get_cars()

    assert len(cars) == 1
    assert cars[0] == CarInfo(name="Ferrari F2004", guid="abc-123", profile="profile1")


def test_deduplicates_by_guid(tmp_path: Path) -> None:
    base = tmp_path / "ace"
    mgr = StorageManager(base)
    reader = GarageReader(mgr)

    profile = base / "profile_data" / "profile1"
    _make_car_json(profile, "car_a.json", {
        "carname": "Car A",
        "carguide": "same-guid",
    })
    _make_car_json(profile, "car_b.json", {
        "carname": "Car B",
        "carguide": "same-guid",
    })

    cars = reader.get_cars()

    assert len(cars) == 1
    assert cars[0].name == "Car A"


def test_multiple_profiles(tmp_path: Path) -> None:
    base = tmp_path / "ace"
    mgr = StorageManager(base)
    reader = GarageReader(mgr)

    p1 = base / "profile_data" / "p1"
    _make_car_json(p1, "car.json", {"carname": "Car1", "carguide": "g1"})

    p2 = base / "profile_data" / "p2"
    _make_car_json(p2, "car.json", {"carname": "Car2", "carguide": "g2"})

    cars = reader.get_cars()

    assert len(cars) == 2
    guids = {c.guid for c in cars}
    assert guids == {"g1", "g2"}


def test_empty_profiles_dir(tmp_path: Path) -> None:
    base = tmp_path / "ace"
    mgr = StorageManager(base)
    reader = GarageReader(mgr)

    cars = reader.get_cars()

    assert cars == []
