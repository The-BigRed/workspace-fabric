from __future__ import annotations

import socket
from collections.abc import Mapping

from workspace_fabric.drivers import (
    DriverAction,
    DriverActionStatus,
    DriverIssueCategory,
    VideoMatrixDriver,
)
from workspace_fabric_driver_orei_uhd808.driver import (
    OreiUhd808ConnectionError,
    OreiUhd808TimeoutError,
    OreiUhd808VideoDriver,
    SocketCommandTransport,
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


class ChunkedSocket:
    def __init__(self, chunks: list[bytes]) -> None:
        self.chunks = list(chunks)
        self.sent: list[bytes] = []
        self.timeouts: list[float] = []
        self.closed = False

    def settimeout(self, timeout: float) -> None:
        self.timeouts.append(timeout)

    def sendall(self, data: bytes) -> None:
        self.sent.append(data)

    def recv(self, size: int) -> bytes:
        if self.chunks:
            return self.chunks.pop(0)
        raise TimeoutError("idle")

    def close(self) -> None:
        self.closed = True


def make_driver(transport: ScriptedTransport) -> OreiUhd808VideoDriver:
    return OreiUhd808VideoDriver(
        "uhd808",
        transport=transport,
    )


def make_socket_transport(
    monkeypatch,
    chunks: list[bytes],
) -> tuple[SocketCommandTransport, ChunkedSocket]:
    fake_socket = ChunkedSocket(chunks)
    monkeypatch.setattr(
        socket,
        "create_connection",
        lambda address, timeout: fake_socket,
    )
    transport = SocketCommandTransport(
        "172.24.2.192",
        port=23,
        read_timeout_seconds=2.0,
        idle_timeout_seconds=0.25,
    )
    return transport, fake_socket


def test_uhd808_route_command_matches_vendor_syntax() -> None:
    assert route_command(1, 2) == "s in 1 av out 2!"


def test_uhd808_socket_transport_sends_crlf_and_reads_split_response(monkeypatch) -> None:
    transport, fake_socket = make_socket_transport(
        monkeypatch,
        [
            b"Welcome to UHD-808\r\n",
            b"r av out 0!\r\n",
            b"input 1 -> output 1\r\n",
        ],
    )

    response = transport.send_command("r av out 0!")

    assert fake_socket.sent == [b"r av out 0!\r\n"]
    assert response == "Welcome to UHD-808\r\nr av out 0!\r\ninput 1 -> output 1"
    assert parse_route_response(response, echo_command="r av out 0!") == {1: 1}


def test_uhd808_socket_transport_discards_telnet_negotiation_bytes(monkeypatch) -> None:
    telnet_negotiation = bytes(
        [
            255,
            251,
            1,
            255,
            253,
            3,
        ]
    )
    transport, fake_socket = make_socket_transport(
        monkeypatch,
        [
            telnet_negotiation[:1],
            telnet_negotiation[1:4],
            telnet_negotiation[4:] + b"r av out 0!\r\n",
            b"input 1 -> output 1\r\n",
        ],
    )

    response = transport.send_command("r av out 0!")

    assert fake_socket.sent == [b"r av out 0!\r\n"]
    assert "\ufffd" not in response
    assert response == "r av out 0!\r\ninput 1 -> output 1"
    assert parse_route_response(response, echo_command="r av out 0!") == {1: 1}


def test_uhd808_route_response_parser_reads_query_output() -> None:
    response = """
    input 1 -> output 1
    input 3 -> output 2
    """

    assert parse_route_response(response) == {1: 1, 2: 3}
    assert response_confirms_route(response, input_port=3, output_port=2)
    assert not response_confirms_route(response, input_port=2, output_port=2)


def test_uhd808_route_parser_ignores_echo_welcome_and_firmware_banner() -> None:
    response = """
    r av out 0!
    Welcome to UHD-808
    MCU BOOT: 1.0.0
    WEB GUI: 2.0.0
    input 1 -> output 1
    input 3 -> output 2
    """

    assert parse_route_response(response, echo_command="r av out 0!") == {1: 1, 2: 3}


def test_uhd808_route_confirmation_requires_actual_route_response() -> None:
    command = route_command(2, 2)
    response = f"""
    {command}
    Welcome to UHD-808
    input 2 -> output 2
    """

    assert response_confirms_route(
        response,
        input_port=2,
        output_port=2,
        echo_command=command,
    )
    assert not response_confirms_route(
        command,
        input_port=2,
        output_port=2,
        echo_command=command,
    )


def test_uhd808_route_parser_reads_full_eight_output_query() -> None:
    route_lines = [
        f"input {input_port} -> output {output_port}"
        for output_port, input_port in enumerate(range(8, 0, -1), start=1)
    ]
    response = "\r\n".join(
        [
            "r av out 0!",
            "Welcome to UHD-808",
            *route_lines,
        ]
    )

    assert parse_route_response(response, echo_command="r av out 0!") == {
        1: 8,
        2: 7,
        3: 6,
        4: 5,
        5: 4,
        6: 3,
        7: 2,
        8: 1,
    }


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


def test_uhd808_echo_only_route_query_reports_state_query_failure() -> None:
    transport = ScriptedTransport({"r av out 0!": ["r av out 0!"]})
    driver = make_driver(transport)
    driver.connect()

    state = driver.get_state()

    assert state["state_status"] == "unknown"
    assert state["routes"] == {}
    assert "raw response" in state["state_error"]
    assert "r av out 0!" in state["state_error"]


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
