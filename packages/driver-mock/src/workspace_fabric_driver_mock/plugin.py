from __future__ import annotations

from workspace_fabric_driver_api import (
    DRIVER_API_COMPATIBILITY_VERSION,
    DriverCapabilityStatus,
    PluginDescriptor,
)

from workspace_fabric_driver_mock.usb_matrix import (
    USB_ROUTING_CAPABILITY,
    MockUsbMatrixDriver,
)
from workspace_fabric_driver_mock.video_matrix import (
    VIDEO_ROUTING_CAPABILITY,
    MockVideoMatrixDriver,
)

MOCK_DRIVER_VERSION = "1.0.0"


def get_mock_video_plugin_descriptor() -> PluginDescriptor:
    return PluginDescriptor(
        driver_type=MockVideoMatrixDriver.driver_type,
        display_name="Mock Video Matrix",
        driver_version=MOCK_DRIVER_VERSION,
        supported_driver_api=DRIVER_API_COMPATIBILITY_VERSION,
        factory=MockVideoMatrixDriver.from_config,
        configuration_schema={"connection": {"required": ()}},
        port_metadata={
            "inputs": {
                "dynamic": True,
                "kind": "virtual_video",
                "accepts": ("video_source",),
            },
            "outputs": {
                "dynamic": True,
                "kind": "virtual_video",
                "accepts": ("display", "video_output"),
            },
        },
        capability_metadata={
            VIDEO_ROUTING_CAPABILITY: DriverCapabilityStatus.SUPPORTED.value,
            "route_query": DriverCapabilityStatus.SUPPORTED.value,
        },
        is_mock=True,
        package_name="workspace-fabric-driver-mock",
    )


def get_mock_usb_plugin_descriptor() -> PluginDescriptor:
    return PluginDescriptor(
        driver_type=MockUsbMatrixDriver.driver_type,
        display_name="Mock USB Matrix",
        driver_version=MOCK_DRIVER_VERSION,
        supported_driver_api=DRIVER_API_COMPATIBILITY_VERSION,
        factory=MockUsbMatrixDriver.from_config,
        configuration_schema={"connection": {"required": ()}},
        port_metadata={
            "device_ports": {
                "dynamic": True,
                "kind": "virtual_usb",
                "accepts": ("usb_device",),
            },
            "host_ports": {
                "dynamic": True,
                "kind": "virtual_usb",
                "accepts": ("host",),
            },
        },
        capability_metadata={
            USB_ROUTING_CAPABILITY: DriverCapabilityStatus.SUPPORTED.value,
            "route_query": DriverCapabilityStatus.SUPPORTED.value,
        },
        is_mock=True,
        package_name="workspace-fabric-driver-mock",
    )


def get_plugin_descriptors() -> tuple[PluginDescriptor, ...]:
    return (
        get_mock_video_plugin_descriptor(),
        get_mock_usb_plugin_descriptor(),
    )
