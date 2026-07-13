from __future__ import annotations

from workspace_fabric.drivers import (
    DriverAction,
    DriverActionType,
    DriverCapabilityStatus,
    DriverIssueCategory,
    UsbMatrixDriver,
    VideoMatrixDriver,
)
from workspace_fabric.drivers.mock import MockUsbMatrixDriver, MockVideoMatrixDriver


def test_phase_3_driver_contract_defines_capability_statuses() -> None:
    assert {status.value for status in DriverCapabilityStatus} == {
        "supported",
        "unsupported",
        "unknown",
    }


def test_phase_3_driver_contract_defines_shared_error_categories() -> None:
    assert {
        "connection_failed",
        "timeout",
        "unsupported_capability",
        "invalid_resource",
        "invalid_port",
        "invalid_route",
        "invalid_action",
        "hardware_rejected_command",
        "state_query_failed",
        "partial_apply",
        "authentication_failed",
        "authorization_failed",
        "missing_driver",
        "duplicate_driver_type",
        "incompatible_driver_api",
        "plugin_load_failed",
        "mock_failure",
        "unknown_error",
    } <= {category.value for category in DriverIssueCategory}


def test_video_and_usb_route_action_types_are_stable() -> None:
    assert DriverActionType.VIDEO_ROUTE.value == "video_route"
    assert DriverActionType.USB_ROUTE.value == "usb_route"


def test_driver_action_can_carry_optional_timeout() -> None:
    action = DriverAction(
        action_type=DriverActionType.VIDEO_ROUTE.value,
        timeout_seconds=2.5,
    )

    assert action.timeout_seconds == 2.5


def test_mock_video_driver_satisfies_stable_video_interface() -> None:
    driver = MockVideoMatrixDriver("mock_video")

    assert isinstance(driver, VideoMatrixDriver)
    action = driver.route_action(input_port=1, output_port=2)
    validation = driver.validate_action(action)

    assert action.action_type == DriverActionType.VIDEO_ROUTE.value
    assert action.payload == {
        "source": "input_1",
        "destination": "output_2",
        "input_port": 1,
        "output_port": 2,
    }
    assert validation.valid


def test_mock_usb_driver_satisfies_stable_usb_interface() -> None:
    driver = MockUsbMatrixDriver("mock_usb")

    assert isinstance(driver, UsbMatrixDriver)
    action = driver.route_action(device_port=1, host_port=2)
    validation = driver.validate_action(action)

    assert action.action_type == DriverActionType.USB_ROUTE.value
    assert action.payload == {
        "device": "device_1",
        "host": "host_2",
        "device_port": 1,
        "host_port": 2,
    }
    assert validation.valid


def test_mock_drivers_use_shared_error_categories() -> None:
    video_driver = MockVideoMatrixDriver(
        "mock_video",
        capabilities={"video_routing": DriverCapabilityStatus.UNSUPPORTED.value},
    )
    usb_driver = MockUsbMatrixDriver("mock_usb")

    video_validation = video_driver.validate_action(
        video_driver.route_action(source="desktop_dp1", destination="primary_4k")
    )
    usb_validation = usb_driver.validate_action(
        usb_driver.route_action(
            device="keyboard",
            host="desktop",
            device_port=0,
            host_port=1,
        )
    )

    assert video_validation.errors[0].category == DriverIssueCategory.UNSUPPORTED_CAPABILITY.value
    assert usb_validation.errors[0].category == DriverIssueCategory.INVALID_PORT.value
