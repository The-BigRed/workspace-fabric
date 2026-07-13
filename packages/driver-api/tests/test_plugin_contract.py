from __future__ import annotations

import pytest

from workspace_fabric_driver_api import (
    DRIVER_API_COMPATIBILITY_VERSION,
    ApiCompatibilityVersion,
    DriverAction,
    DriverIssueCategory,
    PluginDescriptor,
    validate_driver_api_compatibility,
)


def _factory(config):
    raise AssertionError(f"Factory should not be called for {config!r}")


def test_api_compatibility_version_parses_semantic_version_strings() -> None:
    assert ApiCompatibilityVersion.parse("1.0") == DRIVER_API_COMPATIBILITY_VERSION
    assert str(ApiCompatibilityVersion.parse("1.2.3")) == "1.2.3"


def test_api_compatibility_rejects_invalid_version_strings() -> None:
    with pytest.raises(ValueError, match="major.minor"):
        ApiCompatibilityVersion.parse("1")

    with pytest.raises(ValueError, match="numeric"):
        ApiCompatibilityVersion.parse("1.x")


def test_plugin_descriptor_coerces_supported_api_version() -> None:
    descriptor = PluginDescriptor(
        driver_type="mock_video_matrix",
        display_name="Mock Video Matrix",
        driver_version="1.0.0",
        supported_driver_api="1.0",
        factory=_factory,
    )

    assert descriptor.supported_driver_api == DRIVER_API_COMPATIBILITY_VERSION


def test_driver_api_compatibility_accepts_same_major_prior_minor() -> None:
    descriptor = PluginDescriptor(
        driver_type="compatible",
        display_name="Compatible",
        driver_version="1.0.0",
        supported_driver_api="1.0",
        factory=_factory,
    )

    result = validate_driver_api_compatibility(descriptor, ApiCompatibilityVersion(1, 1))

    assert result.valid
    assert result.errors == ()


def test_driver_api_compatibility_rejects_future_minor_version() -> None:
    descriptor = PluginDescriptor(
        driver_type="future_minor",
        display_name="Future Minor",
        driver_version="1.0.0",
        supported_driver_api="1.1",
        factory=_factory,
    )

    result = validate_driver_api_compatibility(descriptor, ApiCompatibilityVersion(1, 0))

    assert not result.valid
    assert result.errors[0].category == DriverIssueCategory.INCOMPATIBLE_DRIVER_API.value
    assert "core accepts Driver API 1.0" in result.errors[0].message


def test_existing_route_action_payload_shape_remains_portable() -> None:
    action = DriverAction(
        action_type="video_route",
        payload={"input_port": 1, "output_port": 2},
    )

    assert action.payload == {"input_port": 1, "output_port": 2}
