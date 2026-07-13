from __future__ import annotations

from workspace_fabric_driver_api import DRIVER_API_COMPATIBILITY_VERSION

from workspace_fabric_driver_mock.plugin import get_plugin_descriptors


def test_mock_package_declares_both_driver_descriptors() -> None:
    descriptors = get_plugin_descriptors()

    assert {descriptor.driver_type for descriptor in descriptors} == {
        "mock_video_matrix",
        "mock_usb_matrix",
    }
    assert all(descriptor.is_mock for descriptor in descriptors)
    assert all(
        descriptor.supported_driver_api == DRIVER_API_COMPATIBILITY_VERSION
        for descriptor in descriptors
    )
    assert all(callable(descriptor.factory) for descriptor in descriptors)
