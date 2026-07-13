"""Workspace Fabric OREI UHD-808 Driver - HDMI matrix control."""

__version__ = "1.0.0"

from workspace_fabric_driver_orei_uhd808.driver import (
    VIDEO_ROUTE_ACTION,
    VIDEO_ROUTING_CAPABILITY,
    OreiUhd808VideoDriver,
    SocketCommandTransport,
)
from workspace_fabric_driver_orei_uhd808.plugin import get_plugin_descriptor

__all__ = [
    "OreiUhd808VideoDriver",
    "SocketCommandTransport",
    "VIDEO_ROUTE_ACTION",
    "VIDEO_ROUTING_CAPABILITY",
    "get_plugin_descriptor",
]
