from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from workspace_fabric_driver_api import Driver

try:
    from workspace_fabric.config.models import DriverConfig
except ImportError:
    from dataclasses import dataclass

    @dataclass
    class DriverConfig:
        id: str
        type: str
        fabric: str
        connection: dict[str, Any] | None = None
        capabilities: dict[str, Any] | None = None


from workspace_fabric_driver_mock.usb_matrix import MockUsbMatrixDriver
from workspace_fabric_driver_mock.video_matrix import MockVideoMatrixDriver

MOCK_DRIVER_TYPES = {
    MockVideoMatrixDriver.driver_type: MockVideoMatrixDriver,
    MockUsbMatrixDriver.driver_type: MockUsbMatrixDriver,
}


def create_mock_driver(config: DriverConfig) -> Driver:
    try:
        driver_class = MOCK_DRIVER_TYPES[config.type]
    except KeyError as exc:
        supported = ", ".join(sorted(MOCK_DRIVER_TYPES))
        raise ValueError(
            f"Unsupported mock driver type {config.type!r}; expected one of {supported}"
        ) from exc

    return driver_class.from_config(config)


def create_mock_drivers(configs: Iterable[DriverConfig]) -> dict[str, Driver]:
    return {config.id: create_mock_driver(config) for config in configs}
