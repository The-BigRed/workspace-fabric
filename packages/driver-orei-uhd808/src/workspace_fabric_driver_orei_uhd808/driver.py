from __future__ import annotations

import re
import socket
import time
from collections.abc import Mapping
from typing import Any, Protocol

from workspace_fabric_driver_api import (
    DriverAction,
    DriverActionPlan,
    DriverActionResult,
    DriverActionStatus,
    DriverActionType,
    DriverCapabilityStatus,
    DriverHealth,
    DriverHealthStatus,
    DriverIssue,
    DriverIssueCategory,
    DriverObservedStateStatus,
    DriverValidationResult,
)

try:
    from workspace_fabric.config.models import DriverConfig
except ImportError:
    from dataclasses import dataclass

    @dataclass
    class DriverConfig:
        id: str
        type: str
        fabric: str
        connection: dict[str, Any] | None = None
        capabilities: dict[str, Any] | None = None


UHD808_DRIVER_TYPE = "orei_uhd808"
VIDEO_ROUTE_ACTION = DriverActionType.VIDEO_ROUTE.value
VIDEO_ROUTING_CAPABILITY = "video_routing"
ROUTE_QUERY_CAPABILITY = "route_query"
ROUTE_QUERY_COMMAND = "r av out 0!"
MIN_HDMI_PORT = 1
MAX_HDMI_PORT = 8
TELNET_IAC = 255
TELNET_SE = 240
TELNET_SB = 250
TELNET_COMMANDS_WITH_OPTION = frozenset({251, 252, 253, 254})

_ROUTE_PATTERN = re.compile(
    r"^\s*input\s+(\d+)\s*->\s*output\s+(\d+)\s*$",
    re.IGNORECASE,
)


class OreiUhd808TransportError(Exception):
    """Base transport error for the UHD-808 driver."""


class OreiUhd808ConnectionError(OreiUhd808TransportError):
    """Raised when the command transport cannot connect or send."""


class OreiUhd808TimeoutError(OreiUhd808TransportError):
    """Raised when the command transport times out waiting for a response."""


class OreiUhd808CommandTransport(Protocol):
    def connect(self) -> None: ...

    def disconnect(self) -> None: ...

    def send_command(self, command: str, *, timeout_seconds: float | None = None) -> str: ...


class SocketCommandTransport:
    """Socket transport for UHD-808 TCP/Telnet-style ASCII commands."""

    def __init__(
        self,
        host: str,
        *,
        port: int,
        connect_timeout_seconds: float = 5.0,
        read_timeout_seconds: float = 2.0,
        idle_timeout_seconds: float = 0.5,
        encoding: str = "ascii",
        line_ending: str = "\r\n",
    ) -> None:
        self.host = host
        self.port = port
        self.connect_timeout_seconds = connect_timeout_seconds
        self.read_timeout_seconds = read_timeout_seconds
        self.idle_timeout_seconds = idle_timeout_seconds
        self.encoding = encoding
        self.line_ending = line_ending
        self._socket: socket.socket | None = None

    def connect(self) -> None:
        if self._socket is not None:
            return

        try:
            self._socket = socket.create_connection(
                (self.host, self.port),
                timeout=self.connect_timeout_seconds,
            )
        except TimeoutError as exc:
            raise OreiUhd808TimeoutError(
                f"Timed out connecting to UHD-808 at {self.host}:{self.port}"
            ) from exc
        except OSError as exc:
            raise OreiUhd808ConnectionError(
                f"Could not connect to UHD-808 at {self.host}:{self.port}: {exc}"
            ) from exc

    def disconnect(self) -> None:
        if self._socket is None:
            return

        try:
            self._socket.close()
        finally:
            self._socket = None

    def send_command(self, command: str, *, timeout_seconds: float | None = None) -> str:
        self.connect()
        assert self._socket is not None

        read_timeout = timeout_seconds or self.read_timeout_seconds
        idle_timeout = min(self.idle_timeout_seconds, read_timeout)
        deadline = time.monotonic() + read_timeout
        framed_command = f"{command}{self.line_ending}".encode(self.encoding)

        try:
            self._socket.sendall(framed_command)
            chunks: list[bytes] = []
            pending_telnet_bytes = b""
            while True:
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    if chunks:
                        break
                    raise OreiUhd808TimeoutError(
                        f"Timed out waiting for UHD-808 response to {command!r}"
                    )

                recv_timeout = min(idle_timeout if chunks else read_timeout, remaining)
                self._socket.settimeout(recv_timeout)
                try:
                    chunk = self._socket.recv(4096)
                except TimeoutError as exc:
                    if chunks:
                        break
                    raise OreiUhd808TimeoutError(
                        f"Timed out waiting for UHD-808 response to {command!r}"
                    ) from exc

                if not chunk:
                    break
                cleaned_chunk, pending_telnet_bytes = _strip_telnet_negotiation(
                    chunk,
                    pending=pending_telnet_bytes,
                )
                if cleaned_chunk:
                    chunks.append(cleaned_chunk)

            return b"".join(chunks).decode(self.encoding, errors="replace").strip()
        except OreiUhd808TransportError:
            raise
        except OSError as exc:
            self.disconnect()
            raise OreiUhd808ConnectionError(
                f"Transport error while sending UHD-808 command {command!r}: {exc}"
            ) from exc


class OreiUhd808VideoDriver:
    driver_type = UHD808_DRIVER_TYPE

    def __init__(
        self,
        driver_id: str,
        *,
        transport: OreiUhd808CommandTransport,
        capabilities: Mapping[str, str] | None = None,
    ) -> None:
        self.id = driver_id
        self._transport = transport
        self._capabilities = _default_capabilities()
        self._capabilities.update(capabilities or {})
        self._connected = False
        self._last_known_routes: dict[int, int] = {}
        self._last_error: str | None = None

    @classmethod
    def from_config(cls, config: DriverConfig) -> OreiUhd808VideoDriver:
        connection = config.connection
        host = connection.get("host")
        if not isinstance(host, str) or not host:
            raise ValueError(
                f"Driver {config.id!r} connection.host is required for {UHD808_DRIVER_TYPE}"
            )

        transport_name = str(connection.get("transport", "telnet"))
        if transport_name not in {"tcp", "telnet"}:
            raise ValueError(
                f"Driver {config.id!r} transport {transport_name!r} is unsupported; "
                "expected 'tcp' or 'telnet'"
            )

        port = _optional_int(
            connection,
            "port",
            default=8000 if transport_name == "tcp" else 23,
        )
        timeout_seconds = _optional_float(connection, "timeout_seconds", default=2.0)
        transport = SocketCommandTransport(
            host,
            port=port,
            connect_timeout_seconds=timeout_seconds,
            read_timeout_seconds=timeout_seconds,
        )

        return cls(
            config.id,
            transport=transport,
            capabilities=config.capabilities,
        )

    def connect(self) -> DriverHealth:
        try:
            self._transport.connect()
        except OreiUhd808TransportError as exc:
            self._connected = False
            self._last_error = str(exc)
            return DriverHealth(DriverHealthStatus.UNREACHABLE, str(exc))

        self._connected = True
        self._last_error = None
        return DriverHealth(DriverHealthStatus.HEALTHY)

    def disconnect(self) -> DriverHealth:
        self._transport.disconnect()
        self._connected = False
        return DriverHealth(DriverHealthStatus.UNKNOWN, "Driver is disconnected")

    def health(self) -> DriverHealth:
        if self._connected:
            return DriverHealth(DriverHealthStatus.HEALTHY)
        return DriverHealth(DriverHealthStatus.UNKNOWN, "Driver is disconnected")

    def get_capabilities(self) -> Mapping[str, str]:
        return dict(self._capabilities)

    def get_state(self) -> Mapping[str, Any]:
        if not self._connected:
            return self._state_from_routes(
                self._last_known_routes,
                DriverObservedStateStatus.UNKNOWN,
                state_error=self._last_error,
            )

        try:
            routes = self._query_routes()
        except OreiUhd808TransportError as exc:
            self._last_error = str(exc)
            return self._state_from_routes(
                self._last_known_routes,
                DriverObservedStateStatus.UNKNOWN,
                state_error=str(exc),
            )

        self._last_known_routes = routes
        self._last_error = None
        return self._state_from_routes(routes, DriverObservedStateStatus.OBSERVED)

    def route_action(self, *, input_port: int, output_port: int) -> DriverAction:
        return DriverAction(
            action_type=VIDEO_ROUTE_ACTION,
            payload={
                "input_port": input_port,
                "output_port": output_port,
            },
        )

    def validate_action(self, action: DriverAction) -> DriverValidationResult:
        errors: list[DriverIssue] = []

        if action.action_type != VIDEO_ROUTE_ACTION:
            return DriverValidationResult(
                valid=False,
                errors=(
                    DriverIssue(
                        category=DriverIssueCategory.INVALID_ACTION.value,
                        message=f"Unsupported action type {action.action_type!r}",
                        path="$.action_type",
                    ),
                ),
            )

        errors.extend(_validate_required_payload(action, ("input_port", "output_port")))
        errors.extend(_validate_int_payload(action, ("input_port", "output_port")))

        capability_error = self._validate_capability(
            VIDEO_ROUTING_CAPABILITY,
            "$.capabilities.video_routing",
        )
        if capability_error is not None:
            errors.append(capability_error)

        if not errors:
            errors.extend(
                (
                    *self._validate_hdmi_port(
                        action.payload["input_port"],
                        "input",
                        "$.payload.input_port",
                    ),
                    *self._validate_hdmi_port(
                        action.payload["output_port"],
                        "output",
                        "$.payload.output_port",
                    ),
                )
            )

        return DriverValidationResult(valid=not errors, errors=tuple(errors))

    def plan_action(self, action: DriverAction) -> DriverActionPlan:
        validation = self.validate_action(action)
        steps: tuple[str, ...] = ()
        if validation.valid:
            input_port = action.payload["input_port"]
            output_port = action.payload["output_port"]
            steps = (
                f"send UHD-808 video route command {route_command(input_port, output_port)!r}",
                f"query UHD-808 route state with {ROUTE_QUERY_COMMAND!r}",
            )

        return DriverActionPlan(
            driver_id=self.id,
            action=action,
            status=(
                DriverActionStatus.PLANNED
                if validation.valid
                else DriverActionStatus.FAILED_VALIDATION
            ),
            steps=steps,
            warnings=validation.warnings,
            errors=validation.errors,
        )

    def apply_action(self, action: DriverAction) -> DriverActionResult:
        validation = self.validate_action(action)
        if not validation.valid:
            return DriverActionResult(
                driver_id=self.id,
                action=action,
                status=DriverActionStatus.FAILED_VALIDATION,
                warnings=validation.warnings,
                errors=validation.errors,
                observed_state=dict(self.get_state()),
            )

        connection_issue = self._ensure_connected()
        if connection_issue is not None:
            return DriverActionResult(
                driver_id=self.id,
                action=action,
                status=DriverActionStatus.FAILED_APPLY,
                errors=(connection_issue,),
                observed_state=dict(self.get_state()),
            )

        input_port = action.payload["input_port"]
        output_port = action.payload["output_port"]
        command = route_command(input_port, output_port)

        try:
            response = self._transport.send_command(
                command,
                timeout_seconds=action.timeout_seconds,
            )
        except OreiUhd808TransportError as exc:
            return self._transport_failure_result(action, exc)

        if not response_confirms_route(
            response,
            input_port=input_port,
            output_port=output_port,
            echo_command=command,
        ):
            return DriverActionResult(
                driver_id=self.id,
                action=action,
                status=DriverActionStatus.FAILED_APPLY,
                errors=(
                    DriverIssue(
                        category=DriverIssueCategory.HARDWARE_REJECTED_COMMAND.value,
                        message=(
                            f"UHD-808 response did not contain confirmed route "
                            f"{input_port!r} -> {output_port!r} for command {command!r}; "
                            f"raw response: {response!r}"
                        ),
                    ),
                ),
                observed_state=dict(self.get_state()),
            )

        self._last_known_routes[output_port] = input_port
        warnings: list[DriverIssue] = []

        try:
            routes = self._query_routes(timeout_seconds=action.timeout_seconds)
        except OreiUhd808TransportError as exc:
            self._last_error = str(exc)
            warnings.append(
                DriverIssue(
                    category=DriverIssueCategory.STATE_QUERY_FAILED.value,
                    message=f"Route applied, but UHD-808 state query failed: {exc}",
                )
            )
            observed_state = self._state_from_routes(
                self._last_known_routes,
                DriverObservedStateStatus.LAST_KNOWN,
                state_error=str(exc),
            )
        else:
            self._last_known_routes = routes
            self._last_error = None
            observed_state = self._state_from_routes(routes, DriverObservedStateStatus.OBSERVED)

        return DriverActionResult(
            driver_id=self.id,
            action=action,
            status=DriverActionStatus.SUCCESS,
            warnings=tuple(warnings),
            observed_state=observed_state,
        )

    def _ensure_connected(self) -> DriverIssue | None:
        if self._connected:
            return None

        health = self.connect()
        if health.status is DriverHealthStatus.HEALTHY:
            return None

        return DriverIssue(
            category=DriverIssueCategory.CONNECTION_FAILED.value,
            message=health.message or "Could not connect to UHD-808",
        )

    def _query_routes(self, *, timeout_seconds: float | None = None) -> dict[int, int]:
        response = self._transport.send_command(
            ROUTE_QUERY_COMMAND, timeout_seconds=timeout_seconds
        )
        routes = parse_route_response(response, echo_command=ROUTE_QUERY_COMMAND)
        if not routes:
            raise OreiUhd808TransportError(
                f"UHD-808 route query returned no parseable routes; raw response: {response!r}"
            )
        return routes

    def _transport_failure_result(
        self,
        action: DriverAction,
        error: OreiUhd808TransportError,
    ) -> DriverActionResult:
        category = DriverIssueCategory.CONNECTION_FAILED.value
        if isinstance(error, OreiUhd808TimeoutError):
            category = DriverIssueCategory.TIMEOUT.value
        else:
            self._connected = False

        self._last_error = str(error)
        return DriverActionResult(
            driver_id=self.id,
            action=action,
            status=DriverActionStatus.FAILED_APPLY,
            errors=(DriverIssue(category=category, message=str(error)),),
            observed_state=self._state_from_routes(
                self._last_known_routes,
                DriverObservedStateStatus.UNKNOWN,
                state_error=str(error),
            ),
        )

    def _validate_capability(self, capability: str, path: str) -> DriverIssue | None:
        status = self._capabilities.get(capability, DriverCapabilityStatus.UNKNOWN.value)
        if status == DriverCapabilityStatus.SUPPORTED.value:
            return None

        return DriverIssue(
            category=DriverIssueCategory.UNSUPPORTED_CAPABILITY.value,
            message=f"Capability {capability!r} is {status!r} for driver {self.id!r}",
            path=path,
        )

    def _validate_hdmi_port(
        self,
        port: int,
        port_kind: str,
        path: str,
    ) -> tuple[DriverIssue, ...]:
        if not _is_valid_hdmi_port(port):
            return (
                DriverIssue(
                    category=DriverIssueCategory.INVALID_PORT.value,
                    message=f"UHD-808 {port_kind} port {port!r} must be between 1 and 8",
                    path=path,
                ),
            )
        return ()

    def _state_from_routes(
        self,
        routes_by_output_port: Mapping[int, int],
        state_status: DriverObservedStateStatus,
        *,
        state_error: str | None = None,
    ) -> dict[str, Any]:
        routes = {
            str(output_port): str(input_port)
            for output_port, input_port in sorted(routes_by_output_port.items())
        }

        state: dict[str, Any] = {
            "connected": self._connected,
            "state_status": state_status.value,
            "routes": routes,
        }
        if state_error:
            state["state_error"] = state_error
        return state


def route_command(input_port: int, output_port: int) -> str:
    return f"s in {input_port} av out {output_port}!"


def parse_route_response(response: str, *, echo_command: str | None = None) -> dict[int, int]:
    response_to_parse = _remove_exact_echoed_command(response, echo_command)
    routes: dict[int, int] = {}
    for line in response_to_parse.splitlines():
        match = _ROUTE_PATTERN.fullmatch(line)
        if match is not None:
            input_port = int(match.group(1))
            output_port = int(match.group(2))
            routes[output_port] = input_port
    return routes


def response_confirms_route(
    response: str,
    *,
    input_port: int,
    output_port: int,
    echo_command: str | None = None,
) -> bool:
    return parse_route_response(response, echo_command=echo_command).get(output_port) == input_port


def _remove_exact_echoed_command(response: str, echo_command: str | None) -> str:
    if echo_command is None:
        return response

    lines = response.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    for index, line in enumerate(lines):
        if line.strip() == echo_command:
            return "\n".join([*lines[:index], *lines[index + 1 :]])
    return response


def _strip_telnet_negotiation(chunk: bytes, *, pending: bytes = b"") -> tuple[bytes, bytes]:
    data = pending + chunk
    stripped = bytearray()
    index = 0

    while index < len(data):
        byte = data[index]
        if byte != TELNET_IAC:
            stripped.append(byte)
            index += 1
            continue

        if index + 1 >= len(data):
            return bytes(stripped), data[index:]

        command = data[index + 1]
        if command == TELNET_IAC:
            stripped.append(TELNET_IAC)
            index += 2
        elif command in TELNET_COMMANDS_WITH_OPTION:
            if index + 2 >= len(data):
                return bytes(stripped), data[index:]
            index += 3
        elif command == TELNET_SB:
            index += 2
            while index + 1 < len(data) and not (
                data[index] == TELNET_IAC and data[index + 1] == TELNET_SE
            ):
                index += 1
            if index + 1 >= len(data):
                return bytes(stripped), data[index:]
            index += 2
        else:
            index += 2

    return bytes(stripped), b""


def _default_capabilities() -> dict[str, str]:
    return {
        VIDEO_ROUTING_CAPABILITY: DriverCapabilityStatus.SUPPORTED.value,
        ROUTE_QUERY_CAPABILITY: DriverCapabilityStatus.SUPPORTED.value,
        "edid_clone": DriverCapabilityStatus.UNKNOWN.value,
        "edid_profile_apply": DriverCapabilityStatus.UNKNOWN.value,
        "scaler": DriverCapabilityStatus.UNKNOWN.value,
        "upscale": DriverCapabilityStatus.UNKNOWN.value,
        "fast_switching": DriverCapabilityStatus.UNSUPPORTED.value,
        "hpd_control": DriverCapabilityStatus.UNSUPPORTED.value,
        "cec": DriverCapabilityStatus.UNKNOWN.value,
        "audio_routing": DriverCapabilityStatus.UNKNOWN.value,
    }


def _validate_required_payload(
    action: DriverAction,
    required_fields: tuple[str, ...],
) -> tuple[DriverIssue, ...]:
    errors: list[DriverIssue] = []
    for field in required_fields:
        if field not in action.payload:
            errors.append(
                DriverIssue(
                    category=DriverIssueCategory.INVALID_ACTION.value,
                    message=f"Required payload field {field!r} is missing",
                    path=f"$.payload.{field}",
                )
            )
    return tuple(errors)


def _validate_int_payload(
    action: DriverAction,
    fields: tuple[str, ...],
) -> tuple[DriverIssue, ...]:
    errors: list[DriverIssue] = []
    for field in fields:
        value = action.payload.get(field)
        if field in action.payload and (not isinstance(value, int) or isinstance(value, bool)):
            errors.append(
                DriverIssue(
                    category=DriverIssueCategory.INVALID_ACTION.value,
                    message=f"Payload field {field!r} must be an integer",
                    path=f"$.payload.{field}",
                )
            )
    return tuple(errors)


def _optional_int(connection: Mapping[str, Any], field: str, *, default: int) -> int:
    if field not in connection:
        return default
    return _coerce_int(connection[field], f"connection.{field}")


def _optional_float(connection: Mapping[str, Any], field: str, *, default: float) -> float:
    if field not in connection:
        return default
    value = connection[field]
    if isinstance(value, bool) or not isinstance(value, int | float):
        raise ValueError(f"UHD-808 connection.{field} must be a number")
    if value <= 0:
        raise ValueError(f"UHD-808 connection.{field} must be positive")
    return float(value)


def _coerce_int(value: Any, path: str) -> int:
    if isinstance(value, bool):
        raise ValueError(f"UHD-808 {path} must be an integer")
    if isinstance(value, int):
        return value
    if isinstance(value, str) and value.isdecimal():
        return int(value)
    raise ValueError(f"UHD-808 {path} must be an integer")


def _is_valid_hdmi_port(port: int) -> bool:
    return MIN_HDMI_PORT <= port <= MAX_HDMI_PORT
