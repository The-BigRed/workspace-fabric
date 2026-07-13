from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from workspace_fabric_driver_api import Driver

from workspace_fabric_driver_mock.usb_matrix import MockUsbMatrixDriver
from workspace_fabric_driver_mock.video_matrix import MockVideoMatrixDriver

MOCK_DRIVER_TYPES = {
    MockVideoMatrixDriver.driver_type: MockVideoMatrixDriver,
    MockUsbMatrixDriver.driver_type: MockUsbMatrixDriver,
}


def create_mock_driver(config: Any) -> Driver:
    try:
        driver_class = MOCK_DRIVER_TYPES[config.type]
    except KeyError as exc:
        supported = ", ".join(sorted(MOCK_DRIVER_TYPES))
        raise ValueError(
            f"Unsupported mock driver type {config.type!r}; expected one of {supported}"
        ) from exc

    return driver_class.from_config(config)


def create_mock_drivers(configs: Iterable[Any]) -> dict[str, Driver]:
    return {config.id: create_mock_driver(config) for config in configs}
