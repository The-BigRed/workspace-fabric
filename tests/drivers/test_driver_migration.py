from __future__ import annotations

from pathlib import Path


def test_core_source_contains_no_legacy_driver_implementation_modules() -> None:
    drivers_dir = Path("packages/core/src/workspace_fabric/drivers")

    assert not any((drivers_dir / "mock").glob("*.py"))
    assert not any((drivers_dir / "video").glob("*.py"))
    assert not any((drivers_dir / "usb").glob("*.py"))


def test_core_source_does_not_import_driver_implementation_packages() -> None:
    core_source = Path("packages/core/src/workspace_fabric")
    implementation_imports = (
        "workspace_fabric_driver_mock",
        "workspace_fabric_driver_orei_uhd808",
        "workspace_fabric_driver_orei_ukm404",
    )

    for source_file in core_source.rglob("*.py"):
        text = source_file.read_text(encoding="utf-8")
        for implementation_import in implementation_imports:
            assert implementation_import not in text, source_file


def test_driver_packages_do_not_import_core_modules() -> None:
    driver_package_dirs = (
        Path("packages/driver-mock/src"),
        Path("packages/driver-orei-uhd808/src"),
        Path("packages/driver-orei-ukm404/src"),
    )

    for package_dir in driver_package_dirs:
        for source_file in package_dir.rglob("*.py"):
            text = source_file.read_text(encoding="utf-8")
            assert "workspace_fabric.config" not in text, source_file
            assert "workspace_fabric.core" not in text, source_file
            assert "workspace_fabric.drivers" not in text, source_file
