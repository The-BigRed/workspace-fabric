from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

import pytest

from workspace_fabric.drivers import (
    DriverAction,
    DriverActionStatus,
    DriverIssueCategory,
    UsbMatrixDriver,
)
from workspace_fabric_driver_orei_ukm404.driver import (
    OreiUkm404ConnectionError,
    OreiUkm404TimeoutError,
    OreiUkm404UsbDriver,
    SerialCommandTransport,
    SocketCommandTransport,
    parse_route_response,
    query_route_command,
    response_confirms_route,
    route_command,
)


@dataclass(frozen=True, slots=True)
class DriverConfig:
    id: str
    type: str
    fabric: str
    connection: dict[str, Any]
    capabilities: dict[str, str] | None = None


class ScriptedTransport:
    def __init__(
        self,
        responses: Mapping[str, list[str | Exception]] | None = None,
        *,
        connect_error: Exception | None = None,
    ) -> None:
        self.connected = False
        self.commands: list[str] = []
        self.timeouts: list[float | None] = []
        self._responses = {command: list(values) for command, values in (responses or {}).items()}
        self._connect_error = connect_error

    def connect(self) -> None:
        if self._connect_error is not None:
            raise self._connect_error
        self.connected = True

    def disconnect(self) -> None:
        self.connected = False

    def send_command(self, command: str, *, timeout_seconds: float | None = None) -> str:
        self.commands.append(command)
        self.timeouts.append(timeout_seconds)
        responses = self._responses.get(command)
        if not responses:
            raise AssertionError(f"No scripted response for {command!r}")

        response = responses.pop(0)
        if isinstance(response, Exception):
            raise response
        return response


def make_driver(transport: ScriptedTransport) -> OreiUkm404UsbDriver:
    return OreiUkm404UsbDriver("ukm404", transport=transport)


def test_ukm404_route_command_matches_vendor_syntax() -> None:
    assert route_command(1, 2) == "set device 1 in host 2"
    assert query_route_command(1) == "get device 1 in host"


def test_ukm404_route_response_parser_reads_documented_formats() -> None:
    response = """
    device 1->host 2
    device 2 in host 3
    device3 connect to host4
    """

    assert parse_route_response(response) == {1: 2, 2: 3, 3: 4}
    assert response_confirms_route(response, device_port=2, host_port=3)
    assert not response_confirms_route(response, device_port=1, host_port=3)


def test_ukm404_driver_satisfies_usb_matrix_contract() -> None:
    driver = make_driver(ScriptedTransport())

    assert isinstance(driver, UsbMatrixDriver)
    assert driver.route_action(device_port=1, host_port=2).payload == {
        "device_port": 1,
        "host_port": 2,
    }


def test_ukm404_driver_accepts_logical_context_without_depending_on_it() -> None:
    driver = make_driver(ScriptedTransport())
    action = driver.route_action(
        device="keyboard",
        host="desktop",
        device_port=1,
        host_port=2,
    )

    validation = driver.validate_action(action)

    assert validation.valid
    assert action.payload == {
        "device": "keyboard",
        "host": "desktop",
        "device_port": 1,
        "host_port": 2,
    }


def test_ukm404_driver_plans_documented_route_and_query_commands() -> None:
    driver = make_driver(ScriptedTransport())
    action = driver.route_action(device_port=1, host_port=2)

    plan = driver.plan_action(action)

    assert plan.status == DriverActionStatus.PLANNED
    assert plan.steps == (
        "send UKM-404 USB route command 'set device 1 in host 2'",
        "query UKM-404 route state with 'get device 1 in host'",
    )


def test_ukm404_driver_applies_route_and_reports_observed_state() -> None:
    transport = ScriptedTransport(
        {
            "set device 1 in host 2": ["set device 1 in host 2"],
            "get device 1 in host": ["device 1 in host 2"],
        }
    )
    driver = make_driver(transport)
    action = driver.route_action(device_port=1, host_port=2)

    result = driver.apply_action(action)

    assert result.status == DriverActionStatus.SUCCESS
    assert transport.connected
    assert transport.commands == ["set device 1 in host 2", "get device 1 in host"]
    assert result.observed_state["state_status"] == "observed"
    assert result.observed_state["routes"] == {"1": "2"}


def test_ukm404_driver_query_state_uses_documented_per_device_query_commands() -> None:
    transport = ScriptedTransport(
        {
            "get device 1 in host": ["device 1 in host 1"],
            "get device 2 in host": ["device 2 in host 2"],
            "get device 3 in host": ["device 3 in host 3"],
            "get device 4 in host": ["device 4 in host 4"],
        }
    )
    driver = make_driver(transport)
    driver.connect()

    state = driver.get_state()

    assert transport.commands == [
        "get device 1 in host",
        "get device 2 in host",
        "get device 3 in host",
        "get device 4 in host",
    ]
    assert state["state_status"] == "observed"
    assert state["routes"] == {"1": "1", "2": "2", "3": "3", "4": "4"}


def test_ukm404_driver_requires_port_payload() -> None:
    driver = make_driver(ScriptedTransport())
    action = DriverAction(action_type="usb_route", payload={"host_port": 1})

    validation = driver.validate_action(action)

    assert not validation.valid
    assert validation.errors[0].category == DriverIssueCategory.INVALID_ACTION.value
    assert validation.errors[0].path == "$.payload.device_port"


def test_ukm404_driver_rejects_non_integer_port_payload() -> None:
    driver = make_driver(ScriptedTransport())
    action = DriverAction(
        action_type="usb_route",
        payload={
            "device_port": "keyboard",
            "host_port": 1,
        },
    )

    validation = driver.validate_action(action)

    assert not validation.valid
    assert validation.errors[0].category == DriverIssueCategory.INVALID_ACTION.value
    assert validation.errors[0].path == "$.payload.device_port"


def test_ukm404_driver_rejects_invalid_port() -> None:
    driver = make_driver(ScriptedTransport())
    action = driver.route_action(device_port=5, host_port=1)

    validation = driver.validate_action(action)

    assert not validation.valid
    assert validation.errors[0].category == DriverIssueCategory.INVALID_PORT.value
    assert validation.errors[0].path == "$.payload.device_port"


def test_ukm404_driver_rejects_unknown_action_type() -> None:
    driver = make_driver(ScriptedTransport())

    result = driver.apply_action(DriverAction(action_type="video_route"))

    assert result.status == DriverActionStatus.FAILED_VALIDATION
    assert result.errors[0].category == DriverIssueCategory.INVALID_ACTION.value


def test_ukm404_driver_reports_hardware_rejected_route_response() -> None:
    transport = ScriptedTransport(
        {
            "set device 1 in host 2": ["device 1 in host 3"],
            "get device 1 in host": ["device 1 in host 3"],
            "get device 2 in host": ["device 2 in host 1"],
            "get device 3 in host": ["device 3 in host 1"],
            "get device 4 in host": ["device 4 in host 1"],
        }
    )
    driver = make_driver(transport)
    action = driver.route_action(device_port=1, host_port=2)

    result = driver.apply_action(action)

    assert result.status == DriverActionStatus.FAILED_APPLY
    assert result.errors[0].category == DriverIssueCategory.HARDWARE_REJECTED_COMMAND.value


def test_ukm404_driver_reports_timeout_without_followup_query() -> None:
    timeout = OreiUkm404TimeoutError("route timed out")
    transport = ScriptedTransport({"set device 1 in host 2": [timeout]})
    driver = make_driver(transport)
    action = driver.route_action(device_port=1, host_port=2)

    result = driver.apply_action(action)

    assert result.status == DriverActionStatus.FAILED_APPLY
    assert result.errors[0].category == DriverIssueCategory.TIMEOUT.value
    assert result.observed_state["state_status"] == "unknown"
    assert transport.commands == ["set device 1 in host 2"]


def test_ukm404_driver_reports_connection_failure() -> None:
    transport = ScriptedTransport(
        connect_error=OreiUkm404ConnectionError("no route to host"),
    )
    driver = make_driver(transport)
    action = driver.route_action(device_port=1, host_port=2)

    result = driver.apply_action(action)

    assert result.status == DriverActionStatus.FAILED_APPLY
    assert result.errors[0].category == DriverIssueCategory.CONNECTION_FAILED.value
    assert transport.commands == []


def test_ukm404_driver_returns_warning_when_state_query_fails_after_apply() -> None:
    timeout = OreiUkm404TimeoutError("query timed out")
    transport = ScriptedTransport(
        {
            "set device 1 in host 2": ["set device 1 in host 2"],
            "get device 1 in host": [timeout],
        }
    )
    driver = make_driver(transport)
    action = driver.route_action(device_port=1, host_port=2)

    result = driver.apply_action(action)

    assert result.status == DriverActionStatus.SUCCESS
    assert result.warnings[0].category == DriverIssueCategory.STATE_QUERY_FAILED.value
    assert result.observed_state["state_status"] == "last_known"
    assert result.observed_state["routes"] == {"1": "2"}


def test_ukm404_from_config_builds_telnet_socket_transport() -> None:
    driver = OreiUkm404UsbDriver.from_config(
        DriverConfig(
            id="ukm404",
            type="orei_ukm404",
            fabric="local_workspace",
            connection={
                "transport": "telnet",
                "host": "192.0.2.10",
            },
        )
    )

    assert isinstance(driver, OreiUkm404UsbDriver)
    assert isinstance(driver._transport, SocketCommandTransport)


def test_ukm404_from_config_builds_serial_transport_without_connecting() -> None:
    driver = OreiUkm404UsbDriver.from_config(
        DriverConfig(
            id="ukm404",
            type="orei_ukm404",
            fabric="local_workspace",
            connection={
                "transport": "serial",
                "port": "COM3",
            },
        )
    )

    assert isinstance(driver, OreiUkm404UsbDriver)
    assert isinstance(driver._transport, SerialCommandTransport)


def test_ukm404_from_config_rejects_unsupported_transport() -> None:
    with pytest.raises(ValueError, match="expected 'tcp', 'telnet', or 'serial'"):
        OreiUkm404UsbDriver.from_config(
            DriverConfig(
                id="ukm404",
                type="orei_ukm404",
                fabric="local_workspace",
                connection={"transport": "bluetooth"},
            )
        )
