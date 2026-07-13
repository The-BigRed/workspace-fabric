from __future__ import annotations

import pytest

from workspace_fabric.config.models import DriverConfig
from workspace_fabric.drivers import (
    DRIVER_API_COMPATIBILITY_VERSION,
    ApiCompatibilityVersion,
    DriverIssueCategory,
    IncompatibleDriverApiError,
    PluginDescriptor,
    create_driver,
    ensure_driver_api_compatible,
    get_driver_descriptor,
    get_driver_descriptors,
    is_mock_driver_type,
)


def _factory(config):
    raise AssertionError(f"Factory should not be called for {config!r}")


def test_current_factory_descriptors_are_api_compatible() -> None:
    descriptors = get_driver_descriptors()

    assert descriptors["mock_video_matrix"].supported_driver_api == DRIVER_API_COMPATIBILITY_VERSION
    assert descriptors["orei_uhd808"].supported_driver_api == DRIVER_API_COMPATIBILITY_VERSION
    assert descriptors["orei_ukm404"].supported_driver_api == DRIVER_API_COMPATIBILITY_VERSION
    assert get_driver_descriptor("mock_usb_matrix").driver_type == "mock_usb_matrix"


def test_mock_detection_uses_descriptor_metadata() -> None:
    assert is_mock_driver_type("mock_video_matrix")
    assert is_mock_driver_type("mock_usb_matrix")
    assert not is_mock_driver_type("orei_uhd808")
    assert not is_mock_driver_type("not_installed")


def test_incompatible_driver_api_error_is_structured() -> None:
    descriptor = PluginDescriptor(
        driver_type="future_driver",
        display_name="Future Driver",
        driver_version="2.0.0",
        supported_driver_api=ApiCompatibilityVersion(2, 0),
        factory=_factory,
    )

    with pytest.raises(IncompatibleDriverApiError) as exc_info:
        ensure_driver_api_compatible(descriptor)

    error = exc_info.value
    assert error.descriptor is descriptor
    assert error.accepted_version == DRIVER_API_COMPATIBILITY_VERSION
    assert error.issue.category == DriverIssueCategory.INCOMPATIBLE_DRIVER_API.value


def test_create_driver_rejects_incompatible_descriptor_before_factory(monkeypatch) -> None:
    from workspace_fabric.drivers import factory

    descriptor = PluginDescriptor(
        driver_type="future_driver",
        display_name="Future Driver",
        driver_version="2.0.0",
        supported_driver_api=ApiCompatibilityVersion(2, 0),
        factory=_factory,
    )
    monkeypatch.setitem(factory.DRIVER_DESCRIPTORS, descriptor.driver_type, descriptor)

    with pytest.raises(IncompatibleDriverApiError):
        create_driver(
            DriverConfig(
                id="future",
                type="future_driver",
                fabric="physical_lab",
            )
        )
