from __future__ import annotations

from collections.abc import Callable, Iterable

from workspace_fabric.config.models import DriverConfig
from workspace_fabric.drivers.base import (
    DRIVER_API_COMPATIBILITY_VERSION,
    ApiCompatibilityVersion,
    Driver,
    DriverIssue,
    PluginDescriptor,
    validate_driver_api_compatibility,
)
from workspace_fabric.drivers.mock import MOCK_DRIVER_TYPES
from workspace_fabric.drivers.usb import OreiUkm404UsbDriver
from workspace_fabric.drivers.video import OreiUhd808VideoDriver

DriverFactory = Callable[[DriverConfig], Driver]
CORE_DRIVER_API_VERSION = DRIVER_API_COMPATIBILITY_VERSION


class IncompatibleDriverApiError(ValueError):
    def __init__(
        self,
        descriptor: PluginDescriptor,
        accepted_version: ApiCompatibilityVersion = CORE_DRIVER_API_VERSION,
        issue: DriverIssue | None = None,
    ) -> None:
        if issue is None:
            validation = validate_driver_api_compatibility(descriptor, accepted_version)
            if validation.valid:
                raise ValueError(
                    f"Driver {descriptor.driver_type!r} is compatible with "
                    f"Driver API {accepted_version}"
                )
            issue = validation.errors[0]
        self.descriptor = descriptor
        self.accepted_version = accepted_version
        self.issue = issue
        super().__init__(issue.message)


DRIVER_DESCRIPTORS: dict[str, PluginDescriptor] = {
    driver_type: PluginDescriptor(
        driver_type=driver_type,
        display_name=driver_type.replace("_", " ").title(),
        driver_version="1.0.0",
        supported_driver_api=DRIVER_API_COMPATIBILITY_VERSION,
        factory=driver_class.from_config,
        is_mock=True,
        package_name="workspace-fabric-driver-mock",
    )
    for driver_type, driver_class in MOCK_DRIVER_TYPES.items()
} | {
    OreiUhd808VideoDriver.driver_type: PluginDescriptor(
        driver_type=OreiUhd808VideoDriver.driver_type,
        display_name="OREI UHD-808 HDMI Matrix",
        driver_version="1.0.0",
        supported_driver_api=DRIVER_API_COMPATIBILITY_VERSION,
        factory=OreiUhd808VideoDriver.from_config,
        configuration_schema={
            "connection": {
                "required": ("host",),
                "transports": ("tcp", "telnet"),
            }
        },
        port_metadata={
            "inputs": {"count": 8, "kind": "hdmi"},
            "outputs": {"count": 8, "kind": "hdmi"},
        },
        capability_metadata={
            "video_routing": "supported",
            "route_query": "supported",
        },
        package_name="workspace-fabric-driver-orei-uhd808",
    ),
    OreiUkm404UsbDriver.driver_type: PluginDescriptor(
        driver_type=OreiUkm404UsbDriver.driver_type,
        display_name="OREI UKM-404 USB Matrix",
        driver_version="1.0.0",
        supported_driver_api=DRIVER_API_COMPATIBILITY_VERSION,
        factory=OreiUkm404UsbDriver.from_config,
        configuration_schema={
            "connection": {
                "required": ("host",),
                "transports": ("tcp", "telnet", "serial"),
            }
        },
        port_metadata={
            "device_ports": {"count": 4, "kind": "usb"},
            "host_ports": {"count": 4, "kind": "usb"},
        },
        capability_metadata={
            "usb_routing": "supported",
            "per_device_routing": "supported",
            "route_query": "supported",
        },
        package_name="workspace-fabric-driver-orei-ukm404",
    ),
}

DRIVER_TYPES: dict[str, DriverFactory] = {
    driver_type: descriptor.factory for driver_type, descriptor in DRIVER_DESCRIPTORS.items()
}


def get_driver_descriptors() -> dict[str, PluginDescriptor]:
    return dict(DRIVER_DESCRIPTORS)


def get_driver_descriptor(driver_type: str) -> PluginDescriptor:
    try:
        return DRIVER_DESCRIPTORS[driver_type]
    except KeyError as exc:
        supported = ", ".join(sorted(DRIVER_DESCRIPTORS))
        raise ValueError(
            f"Unsupported driver type {driver_type!r}; expected one of {supported}"
        ) from exc


def ensure_driver_api_compatible(
    descriptor: PluginDescriptor,
    accepted_version: ApiCompatibilityVersion = CORE_DRIVER_API_VERSION,
) -> None:
    validation = validate_driver_api_compatibility(descriptor, accepted_version)
    if not validation.valid:
        raise IncompatibleDriverApiError(
            descriptor,
            accepted_version,
            validation.errors[0],
        )


def create_driver(config: DriverConfig) -> Driver:
    try:
        descriptor = DRIVER_DESCRIPTORS[config.type]
    except KeyError as exc:
        supported = ", ".join(sorted(DRIVER_DESCRIPTORS))
        raise ValueError(
            f"Unsupported driver type {config.type!r}; expected one of {supported}"
        ) from exc

    ensure_driver_api_compatible(descriptor)
    return descriptor.factory(config)


def create_drivers(configs: Iterable[DriverConfig]) -> dict[str, Driver]:
    return {config.id: create_driver(config) for config in configs}


def is_mock_driver_type(driver_type: str) -> bool:
    descriptor = DRIVER_DESCRIPTORS.get(driver_type)
    return descriptor.is_mock if descriptor is not None else False
