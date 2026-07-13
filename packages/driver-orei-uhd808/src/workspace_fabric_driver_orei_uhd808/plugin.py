from __future__ import annotations

from workspace_fabric_driver_api import (
    DRIVER_API_COMPATIBILITY_VERSION,
    DriverCapabilityStatus,
    PluginDescriptor,
)

from workspace_fabric_driver_orei_uhd808.driver import (
    VIDEO_ROUTING_CAPABILITY,
    OreiUhd808VideoDriver,
)

UHD808_DRIVER_VERSION = "1.0.0"


def get_plugin_descriptor() -> PluginDescriptor:
    return PluginDescriptor(
        driver_type=OreiUhd808VideoDriver.driver_type,
        display_name="OREI UHD-808 HDMI Matrix",
        driver_version=UHD808_DRIVER_VERSION,
        supported_driver_api=DRIVER_API_COMPATIBILITY_VERSION,
        factory=OreiUhd808VideoDriver.from_config,
        configuration_schema={
            "connection": {
                "required": ("host",),
                "transports": ("tcp", "telnet"),
            }
        },
        port_metadata={
            "inputs": {
                "count": 8,
                "kind": "hdmi",
                "direction": "sink",
                "accepts": ("video_source",),
            },
            "outputs": {
                "count": 8,
                "kind": "hdmi",
                "direction": "source",
                "accepts": ("display", "video_output"),
            },
        },
        capability_metadata={
            VIDEO_ROUTING_CAPABILITY: DriverCapabilityStatus.SUPPORTED.value,
            "route_query": DriverCapabilityStatus.SUPPORTED.value,
            "edid_clone": DriverCapabilityStatus.UNKNOWN.value,
            "edid_profile_apply": DriverCapabilityStatus.UNKNOWN.value,
            "scaler": DriverCapabilityStatus.UNKNOWN.value,
            "upscale": DriverCapabilityStatus.UNKNOWN.value,
            "fast_switching": DriverCapabilityStatus.UNSUPPORTED.value,
            "hpd_control": DriverCapabilityStatus.UNSUPPORTED.value,
            "cec": DriverCapabilityStatus.UNKNOWN.value,
            "audio_routing": DriverCapabilityStatus.UNKNOWN.value,
        },
        package_name="workspace-fabric-driver-orei-uhd808",
    )
