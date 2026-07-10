from __future__ import annotations

from collections.abc import Callable, Iterable

from workspace_fabric.config.models import DriverConfig
from workspace_fabric.drivers.base import Driver
from workspace_fabric.drivers.mock import MOCK_DRIVER_TYPES
from workspace_fabric.drivers.usb import OreiUkm404UsbDriver
from workspace_fabric.drivers.video import OreiUhd808VideoDriver

DriverFactory = Callable[[DriverConfig], Driver]

DRIVER_TYPES: dict[str, DriverFactory] = {
    driver_type: driver_class.from_config for driver_type, driver_class in MOCK_DRIVER_TYPES.items()
} | {
    OreiUhd808VideoDriver.driver_type: OreiUhd808VideoDriver.from_config,
    OreiUkm404UsbDriver.driver_type: OreiUkm404UsbDriver.from_config,
}


def create_driver(config: DriverConfig) -> Driver:
    try:
        factory = DRIVER_TYPES[config.type]
    except KeyError as exc:
        supported = ", ".join(sorted(DRIVER_TYPES))
        raise ValueError(
            f"Unsupported driver type {config.type!r}; expected one of {supported}"
        ) from exc

    return factory(config)


def create_drivers(configs: Iterable[DriverConfig]) -> dict[str, Driver]:
    return {config.id: create_driver(config) for config in configs}


def is_mock_driver_type(driver_type: str) -> bool:
    return driver_type in MOCK_DRIVER_TYPES
