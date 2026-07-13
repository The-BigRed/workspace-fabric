"""Workspace Fabric OREI UKM-404 Driver - USB matrix control."""

__version__ = "1.0.0"

from workspace_fabric_driver_orei_ukm404.driver import (
    USB_ROUTE_ACTION,
    USB_ROUTING_CAPABILITY,
    OreiUkm404UsbDriver,
    SocketCommandTransport,
)
from workspace_fabric_driver_orei_ukm404.plugin import get_plugin_descriptor

__all__ = [
    "OreiUkm404UsbDriver",
    "SocketCommandTransport",
    "USB_ROUTE_ACTION",
    "USB_ROUTING_CAPABILITY",
    "get_plugin_descriptor",
]
