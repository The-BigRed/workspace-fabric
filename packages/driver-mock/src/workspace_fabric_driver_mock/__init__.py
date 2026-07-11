"""Workspace Fabric Mock Drivers - In-memory test drivers."""

from workspace_fabric_driver_mock.factory import (
    MOCK_DRIVER_TYPES,
    create_mock_driver,
    create_mock_drivers,
)
from workspace_fabric_driver_mock.usb_matrix import (
    USB_ROUTE_ACTION,
    USB_ROUTING_CAPABILITY,
    MockUsbMatrixDriver,
)
from workspace_fabric_driver_mock.video_matrix import (
    VIDEO_ROUTE_ACTION,
    VIDEO_ROUTING_CAPABILITY,
    MockVideoMatrixDriver,
)

__version__ = "1.0.0"

__all__ = [
    "MOCK_DRIVER_TYPES",
    "MockUsbMatrixDriver",
    "MockVideoMatrixDriver",
    "USB_ROUTE_ACTION",
    "USB_ROUTING_CAPABILITY",
    "VIDEO_ROUTE_ACTION",
    "VIDEO_ROUTING_CAPABILITY",
    "create_mock_driver",
    "create_mock_drivers",
]
