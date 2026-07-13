from __future__ import annotations

from workspace_fabric_driver_api import DRIVER_API_COMPATIBILITY_VERSION

from workspace_fabric_driver_orei_ukm404.plugin import get_plugin_descriptor


def test_ukm404_plugin_descriptor_declares_stable_type_and_api_version() -> None:
    descriptor = get_plugin_descriptor()

    assert descriptor.driver_type == "orei_ukm404"
    assert descriptor.display_name == "OREI UKM-404 USB Matrix"
    assert descriptor.driver_version == "1.0.0"
    assert descriptor.supported_driver_api == DRIVER_API_COMPATIBILITY_VERSION
    assert descriptor.port_metadata["device_ports"]["count"] == 4
    assert descriptor.capability_metadata["usb_routing"] == "supported"
    assert callable(descriptor.factory)
