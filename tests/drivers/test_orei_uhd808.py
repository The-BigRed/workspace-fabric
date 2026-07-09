from __future__ import annotations

from collections.abc import Mapping

from workspace_fabric.drivers import (
    DriverAction,
    DriverActionStatus,
    DriverIssueCategory,
    VideoMatrixDriver,
)
from workspace_fabric.drivers.video import (
    OreiUhd808ConnectionError,
    OreiUhd808TimeoutError,
    OreiUhd808VideoDriver,
    parse_route_response,
    response_confirms_route,
    route_command,
)


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


def make_driver(transport: ScriptedTransport) -> OreiUhd808VideoDriver:
    return OreiUhd808VideoDriver(
        "uhd808",
        transport=transport,
    )


def test_uhd808_route_command_matches_vendor_syntax() -> None:
    assert route_command(1, 2) == "s in 1 av out 2!"


def test_uhd808_route_response_parser_reads_query_output() -> None:
    response = """
    input 1 -> output 1
    input 3 -> output 2
    """

    assert parse_route_response(response) == {1: 1, 2: 3}
    assert response_confirms_route(response, input_port=3, output_port=2)
    assert not response_confirms_route(response, input_port=2, output_port=2)


def test_uhd808_driver_satisfies_video_matrix_contract() -> None:
    driver = make_driver(ScriptedTransport())

    assert isinstance(driver, VideoMatrixDriver)
    assert driver.route_action(input_port=1, output_port=2).payload == {
        "input_port": 1,
        "output_port": 2,
    }


def test_uhd808_driver_plans_documented_route_and_query_commands() -> None:
    driver = make_driver(ScriptedTransport())
    action = driver.route_action(input_port=1, output_port=2)

    plan = driver.plan_action(action)

    assert plan.status == DriverActionStatus.PLANNED
    assert plan.steps == (
        "send UHD-808 video route command 's in 1 av out 2!'",
        "query UHD-808 route state with 'r av out 0!'",
    )


def test_uhd808_driver_applies_route_and_reports_observed_state() -> None:
    transport = ScriptedTransport(
        {
            "s in 1 av out 2!": ["input 1 -> output 2"],
            "r av out 0!": ["input 3 -> output 1\r\ninput 1 -> output 2"],
        }
    )
    driver = make_driver(transport)
    action = driver.route_action(input_port=1, output_port=2)

    result = driver.apply_action(action)

    assert result.status == DriverActionStatus.SUCCESS
    assert transport.connected
    assert transport.commands == ["s in 1 av out 2!", "r av out 0!"]
    assert result.observed_state["state_status"] == "observed"
    assert result.observed_state["routes"] == {"1": "3", "2": "1"}


def test_uhd808_driver_query_state_uses_documented_route_query_command() -> None:
    transport = ScriptedTransport({"r av out 0!": ["input 2 -> output 1"]})
    driver = make_driver(transport)
    driver.connect()

    state = driver.get_state()

    assert transport.commands == ["r av out 0!"]
    assert state["state_status"] == "observed"
    assert state["routes"] == {"1": "2"}


def test_uhd808_driver_requires_port_payload() -> None:
    driver = make_driver(ScriptedTransport())
    action = DriverAction(action_type="video_route", payload={"output_port": 1})

    validation = driver.validate_action(action)

    assert not validation.valid
    assert validation.errors[0].category == DriverIssueCategory.INVALID_ACTION.value
    assert validation.errors[0].path == "$.payload.input_port"


def test_uhd808_driver_rejects_non_integer_port_payload() -> None:
    driver = make_driver(ScriptedTransport())
    action = DriverAction(
        action_type="video_route",
        payload={
            "input_port": "desktop_dp1",
            "output_port": 1,
        },
    )

    validation = driver.validate_action(action)

    assert not validation.valid
    assert validation.errors[0].category == DriverIssueCategory.INVALID_ACTION.value
    assert validation.errors[0].path == "$.payload.input_port"


def test_uhd808_driver_rejects_invalid_port_mapping() -> None:
    driver = make_driver(ScriptedTransport())
    action = driver.route_action(input_port=9, output_port=1)

    validation = driver.validate_action(action)

    assert not validation.valid
    assert validation.errors[0].category == DriverIssueCategory.INVALID_PORT.value
    assert validation.errors[0].path == "$.payload.input_port"


def test_uhd808_driver_rejects_unknown_action_type() -> None:
    driver = make_driver(ScriptedTransport())

    result = driver.apply_action(DriverAction(action_type="usb_route"))

    assert result.status == DriverActionStatus.FAILED_VALIDATION
    assert result.errors[0].category == DriverIssueCategory.INVALID_ACTION.value


def test_uhd808_driver_reports_hardware_rejected_route_response() -> None:
    transport = ScriptedTransport(
        {
            "s in 1 av out 2!": ["input 2 -> output 2"],
            "r av out 0!": ["input 2 -> output 2"],
        }
    )
    driver = make_driver(transport)
    action = driver.route_action(input_port=1, output_port=2)

    result = driver.apply_action(action)

    assert result.status == DriverActionStatus.FAILED_APPLY
    assert result.errors[0].category == DriverIssueCategory.HARDWARE_REJECTED_COMMAND.value


def test_uhd808_driver_reports_timeout_without_followup_query() -> None:
    timeout = OreiUhd808TimeoutError("route timed out")
    transport = ScriptedTransport({"s in 1 av out 2!": [timeout]})
    driver = make_driver(transport)
    action = driver.route_action(input_port=1, output_port=2)

    result = driver.apply_action(action)

    assert result.status == DriverActionStatus.FAILED_APPLY
    assert result.errors[0].category == DriverIssueCategory.TIMEOUT.value
    assert result.observed_state["state_status"] == "unknown"
    assert transport.commands == ["s in 1 av out 2!"]


def test_uhd808_driver_reports_connection_failure() -> None:
    transport = ScriptedTransport(
        connect_error=OreiUhd808ConnectionError("no route to host"),
    )
    driver = make_driver(transport)
    action = driver.route_action(input_port=1, output_port=2)

    result = driver.apply_action(action)

    assert result.status == DriverActionStatus.FAILED_APPLY
    assert result.errors[0].category == DriverIssueCategory.CONNECTION_FAILED.value
    assert transport.commands == []
