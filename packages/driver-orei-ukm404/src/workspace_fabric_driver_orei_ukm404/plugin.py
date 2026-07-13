from __future__ import annotations

from workspace_fabric_driver_api import (
    DRIVER_API_COMPATIBILITY_VERSION,
    DriverCapabilityStatus,
    PluginDescriptor,
)

from workspace_fabric_driver_orei_ukm404.driver import (
    USB_ROUTING_CAPABILITY,
    OreiUkm404UsbDriver,
)

UKM404_DRIVER_VERSION = "1.0.0"


def get_plugin_descriptor() -> PluginDescriptor:
    return PluginDescriptor(
        driver_type=OreiUkm404UsbDriver.driver_type,
        display_name="OREI UKM-404 USB Matrix",
        driver_version=UKM404_DRIVER_VERSION,
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
            USB_ROUTING_CAPABILITY: DriverCapabilityStatus.SUPPORTED.value,
            "per_device_routing": DriverCapabilityStatus.SUPPORTED.value,
            "route_query": DriverCapabilityStatus.SUPPORTED.value,
            "usb3": DriverCapabilityStatus.SUPPORTED.value,
            "host_emulation": DriverCapabilityStatus.UNKNOWN.value,
            "device_emulation": DriverCapabilityStatus.UNKNOWN.value,
        },
        package_name="workspace-fabric-driver-orei-ukm404",
    )
