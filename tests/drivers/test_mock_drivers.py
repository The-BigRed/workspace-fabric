from __future__ import annotations

from pathlib import Path

from workspace_fabric.config import load_config
from workspace_fabric.core.graph import build_resource_graph
from workspace_fabric_driver_api import DriverAction, DriverActionStatus
from workspace_fabric_driver_mock import (
    MockUsbMatrixDriver,
    MockVideoMatrixDriver,
    create_mock_driver,
    create_mock_drivers,
)


def test_mock_driver_factory_loads_configured_mock_drivers() -> None:
    config = load_config(Path("examples/local-workspace.yaml"))

    drivers = create_mock_drivers(config.drivers.values())

    assert isinstance(drivers["mock_video"], MockVideoMatrixDriver)
    assert isinstance(drivers["mock_usb_a"], MockUsbMatrixDriver)
    assert isinstance(drivers["mock_usb_b"], MockUsbMatrixDriver)
    assert drivers["mock_video"].get_capabilities()["video_routing"] == "supported"


def test_mock_video_driver_plans_applies_and_reports_state() -> None:
    config = load_config(Path("examples/local-workspace.yaml"))
    graph = build_resource_graph(config)
    resolution = graph.resolve_video_route("primary_4k", "desktop_dp1")
    driver = create_mock_driver(resolution.driver)
    driver.connect()
    action = driver.route_action(
        source=resolution.source.id,
        destination=resolution.display.id,
    )

    plan = driver.plan_action(action)
    result = driver.apply_action(action)

    assert plan.status == DriverActionStatus.PLANNED
    assert plan.steps == ("route video source 'desktop_dp1' to 'primary_4k'",)
    assert result.status == DriverActionStatus.SUCCESS
    assert driver.get_state()["routes"] == {"primary_4k": "desktop_dp1"}
    assert result.observed_state["routes"] == {"primary_4k": "desktop_dp1"}


def test_mock_usb_driver_plans_applies_and_reports_state() -> None:
    config = load_config(Path("examples/local-workspace.yaml"))
    graph = build_resource_graph(config)
    resolution = graph.resolve_usb_route("speakers", "controller")
    driver = create_mock_driver(resolution.driver)
    driver.connect()
    action = driver.route_action(
        device=resolution.device.id,
        host=resolution.host.id,
        device_port=resolution.device_port,
        host_port=resolution.host_port,
    )

    plan = driver.plan_action(action)
    result = driver.apply_action(action)

    assert plan.status == DriverActionStatus.PLANNED
    assert plan.steps == ("route USB device 'speakers' to host 'controller'",)
    assert result.status == DriverActionStatus.SUCCESS
    assert driver.get_state()["routes"] == {"speakers": "controller"}


def test_mock_drivers_keep_instance_state_separate() -> None:
    usb_a = MockUsbMatrixDriver("mock_usb_a")
    usb_b = MockUsbMatrixDriver("mock_usb_b")

    usb_a.apply_action(
        usb_a.route_action(device="keyboard", host="desktop", device_port=1, host_port=1)
    )
    usb_b.apply_action(
        usb_b.route_action(device="speakers", host="controller", device_port=1, host_port=3)
    )

    assert usb_a.get_state()["routes"] == {"keyboard": "desktop"}
    assert usb_b.get_state()["routes"] == {"speakers": "controller"}


def test_mock_driver_can_simulate_unsupported_capability() -> None:
    driver = MockVideoMatrixDriver("mock_video", capabilities={"video_routing": "unsupported"})
    action = driver.route_action(source="desktop_dp1", destination="primary_4k")

    validation = driver.validate_action(action)
    plan = driver.plan_action(action)
    result = driver.apply_action(action)

    assert not validation.valid
    assert validation.errors[0].category == "unsupported_capability"
    assert plan.status == DriverActionStatus.FAILED_VALIDATION
    assert result.status == DriverActionStatus.FAILED_VALIDATION
    assert driver.get_state()["routes"] == {}


def test_mock_driver_can_simulate_apply_failure() -> None:
    driver = MockUsbMatrixDriver("mock_usb")
    action = driver.route_action(device="keyboard", host="desktop", device_port=1, host_port=1)
    driver.fail_next_action("usb_route", "Injected USB switch failure")

    first_result = driver.apply_action(action)
    second_result = driver.apply_action(action)

    assert first_result.status == DriverActionStatus.FAILED_APPLY
    assert first_result.errors[0].message == "Injected USB switch failure"
    assert first_result.observed_state["routes"] == {}
    assert second_result.status == DriverActionStatus.SUCCESS
    assert second_result.observed_state["routes"] == {"keyboard": "desktop"}


def test_mock_driver_rejects_unknown_action_type() -> None:
    driver = MockVideoMatrixDriver("mock_video")

    result = driver.apply_action(DriverAction(action_type="unknown"))

    assert result.status == DriverActionStatus.FAILED_VALIDATION
    assert result.errors[0].category == "invalid_action"
