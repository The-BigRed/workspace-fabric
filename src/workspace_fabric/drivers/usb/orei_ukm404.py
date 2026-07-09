from __future__ import annotations

import re
import socket
from collections.abc import Mapping
from typing import Any, Protocol

from workspace_fabric.config.models import DriverConfig
from workspace_fabric.drivers.base import (
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

UKM404_DRIVER_TYPE = "orei_ukm404"
USB_ROUTE_ACTION = DriverActionType.USB_ROUTE.value
USB_ROUTING_CAPABILITY = "usb_routing"
ROUTE_QUERY_CAPABILITY = "route_query"
MIN_USB_PORT = 1
MAX_USB_PORT = 4

_ROUTE_PATTERN = re.compile(
    r"device\s*(\d+)\s*(?:->\s*|in\s+|connect\s+to\s+)host\s*(\d+)",
    re.IGNORECASE,
)


class OreiUkm404TransportError(Exception):
    """Base transport error for the UKM-404 driver."""


class OreiUkm404ConnectionError(OreiUkm404TransportError):
    """Raised when the command transport cannot connect or send."""


class OreiUkm404TimeoutError(OreiUkm404TransportError):
    """Raised when the command transport times out waiting for a response."""


class OreiUkm404CommandTransport(Protocol):
    def connect(self) -> None: ...

    def disconnect(self) -> None: ...

    def send_command(self, command: str, *, timeout_seconds: float | None = None) -> str: ...


class SocketCommandTransport:
    """Socket transport for UKM-404 TCP/Telnet-style ASCII commands."""

    def __init__(
        self,
        host: str,
        *,
        port: int,
        connect_timeout_seconds: float = 5.0,
        read_timeout_seconds: float = 2.0,
        encoding: str = "ascii",
        line_ending: str = "\r\n",
    ) -> None:
        self.host = host
        self.port = port
        self.connect_timeout_seconds = connect_timeout_seconds
        self.read_timeout_seconds = read_timeout_seconds
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
            raise OreiUkm404TimeoutError(
                f"Timed out connecting to UKM-404 at {self.host}:{self.port}"
            ) from exc
        except OSError as exc:
            raise OreiUkm404ConnectionError(
                f"Could not connect to UKM-404 at {self.host}:{self.port}: {exc}"
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
        self._socket.settimeout(read_timeout)
        framed_command = f"{command}{self.line_ending}".encode(self.encoding)

        try:
            self._socket.sendall(framed_command)
            chunks: list[bytes] = []
            while True:
                try:
                    chunk = self._socket.recv(4096)
                except TimeoutError as exc:
                    if chunks:
                        break
                    raise OreiUkm404TimeoutError(
                        f"Timed out waiting for UKM-404 response to {command!r}"
                    ) from exc

                if not chunk:
                    break
                chunks.append(chunk)

            return b"".join(chunks).decode(self.encoding, errors="replace").strip()
        except OreiUkm404TransportError:
            raise
        except OSError as exc:
            self.disconnect()
            raise OreiUkm404ConnectionError(
                f"Transport error while sending UKM-404 command {command!r}: {exc}"
            ) from exc


class SerialCommandTransport:
    """Serial transport for UKM-404 RS-232 ASCII commands."""

    def __init__(
        self,
        port: str,
        *,
        baud_rate: int = 115200,
        read_timeout_seconds: float = 2.0,
        encoding: str = "ascii",
        line_ending: str = "\r\n",
    ) -> None:
        self.port = port
        self.baud_rate = baud_rate
        self.read_timeout_seconds = read_timeout_seconds
        self.encoding = encoding
        self.line_ending = line_ending
        self._serial: Any | None = None

    def connect(self) -> None:
        if self._serial is not None:
            return

        try:
            import serial  # type: ignore[import-not-found]
        except ImportError as exc:
            raise OreiUkm404ConnectionError(
                "pyserial is required for UKM-404 serial transport"
            ) from exc

        try:
            self._serial = serial.Serial(
                port=self.port,
                baudrate=self.baud_rate,
                bytesize=8,
                stopbits=1,
                parity=serial.PARITY_NONE,
                timeout=self.read_timeout_seconds,
                write_timeout=self.read_timeout_seconds,
            )
        except serial.SerialTimeoutException as exc:
            raise OreiUkm404TimeoutError(
                f"Timed out opening UKM-404 serial port {self.port!r}"
            ) from exc
        except serial.SerialException as exc:
            raise OreiUkm404ConnectionError(
                f"Could not open UKM-404 serial port {self.port!r}: {exc}"
            ) from exc

    def disconnect(self) -> None:
        if self._serial is None:
            return

        try:
            self._serial.close()
        finally:
            self._serial = None

    def send_command(self, command: str, *, timeout_seconds: float | None = None) -> str:
        self.connect()
        assert self._serial is not None

        timeout = timeout_seconds or self.read_timeout_seconds
        self._serial.timeout = timeout
        self._serial.write_timeout = timeout
        framed_command = f"{command}{self.line_ending}".encode(self.encoding)

        try:
            self._serial.write(framed_command)
            self._serial.flush()
            chunks: list[bytes] = []
            while True:
                chunk = self._serial.read(4096)
                if not chunk:
                    break
                chunks.append(chunk)
            return b"".join(chunks).decode(self.encoding, errors="replace").strip()
        except OreiUkm404TransportError:
            raise
        except TimeoutError as exc:
            raise OreiUkm404TimeoutError(
                f"Timed out waiting for UKM-404 response to {command!r}"
            ) from exc
        except OSError as exc:
            self.disconnect()
            raise OreiUkm404ConnectionError(
                f"Transport error while sending UKM-404 command {command!r}: {exc}"
            ) from exc


class OreiUkm404UsbDriver:
    driver_type = UKM404_DRIVER_TYPE

    def __init__(
        self,
        driver_id: str,
        *,
        transport: OreiUkm404CommandTransport,
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
    def from_config(cls, config: DriverConfig) -> OreiUkm404UsbDriver:
        connection = config.connection
        transport_name = str(connection.get("transport", "telnet"))
        timeout_seconds = _optional_float(connection, "timeout_seconds", default=2.0)
        line_ending = _optional_str(connection, "line_ending", default="\r\n")

        if transport_name in {"tcp", "telnet"}:
            host = connection.get("host")
            if not isinstance(host, str) or not host:
                raise ValueError(
                    f"Driver {config.id!r} connection.host is required for {transport_name}"
                )
            port = _optional_int(
                connection,
                "port",
                default=8000 if transport_name == "tcp" else 23,
            )
            transport: OreiUkm404CommandTransport = SocketCommandTransport(
                host,
                port=port,
                connect_timeout_seconds=timeout_seconds,
                read_timeout_seconds=timeout_seconds,
                line_ending=line_ending,
            )
        elif transport_name == "serial":
            serial_port = connection.get("port")
            if not isinstance(serial_port, str) or not serial_port:
                raise ValueError(
                    f"Driver {config.id!r} connection.port is required for serial transport"
                )
            transport = SerialCommandTransport(
                serial_port,
                baud_rate=_optional_int(connection, "baud_rate", default=115200),
                read_timeout_seconds=timeout_seconds,
                line_ending=line_ending,
            )
        else:
            raise ValueError(
                f"Driver {config.id!r} transport {transport_name!r} is unsupported; "
                "expected 'tcp', 'telnet', or 'serial'"
            )

        return cls(config.id, transport=transport, capabilities=config.capabilities)

    def connect(self) -> DriverHealth:
        try:
            self._transport.connect()
        except OreiUkm404TransportError as exc:
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
        except OreiUkm404TransportError as exc:
            self._last_error = str(exc)
            return self._state_from_routes(
                self._last_known_routes,
                DriverObservedStateStatus.UNKNOWN,
                state_error=str(exc),
            )

        self._last_known_routes = routes
        self._last_error = None
        return self._state_from_routes(routes, DriverObservedStateStatus.OBSERVED)

    def route_action(
        self,
        *,
        device_port: int,
        host_port: int,
        device: str | None = None,
        host: str | None = None,
    ) -> DriverAction:
        payload: dict[str, Any] = {
            "device_port": device_port,
            "host_port": host_port,
        }
        if device is not None:
            payload["device"] = device
        if host is not None:
            payload["host"] = host
        return DriverAction(action_type=USB_ROUTE_ACTION, payload=payload)

    def validate_action(self, action: DriverAction) -> DriverValidationResult:
        errors: list[DriverIssue] = []

        if action.action_type != USB_ROUTE_ACTION:
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

        errors.extend(_validate_required_payload(action, ("device_port", "host_port")))
        errors.extend(_validate_int_payload(action, ("device_port", "host_port")))
        errors.extend(_validate_optional_string_payload(action, ("device", "host")))

        capability_error = self._validate_capability(
            USB_ROUTING_CAPABILITY,
            "$.capabilities.usb_routing",
        )
        if capability_error is not None:
            errors.append(capability_error)

        if not errors:
            errors.extend(
                (
                    *self._validate_usb_port(
                        action.payload["device_port"],
                        "device",
                        "$.payload.device_port",
                    ),
                    *self._validate_usb_port(
                        action.payload["host_port"],
                        "host",
                        "$.payload.host_port",
                    ),
                )
            )

        return DriverValidationResult(valid=not errors, errors=tuple(errors))

    def plan_action(self, action: DriverAction) -> DriverActionPlan:
        validation = self.validate_action(action)
        steps: tuple[str, ...] = ()
        if validation.valid:
            device_port = action.payload["device_port"]
            host_port = action.payload["host_port"]
            steps = (
                f"send UKM-404 USB route command {route_command(device_port, host_port)!r}",
                f"query UKM-404 route state with {query_route_command(device_port)!r}",
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

        device_port = action.payload["device_port"]
        host_port = action.payload["host_port"]
        command = route_command(device_port, host_port)

        try:
            response = self._transport.send_command(
                command,
                timeout_seconds=action.timeout_seconds,
            )
        except OreiUkm404TransportError as exc:
            return self._transport_failure_result(action, exc)

        if not response_confirms_route(
            response,
            device_port=device_port,
            host_port=host_port,
        ):
            return DriverActionResult(
                driver_id=self.id,
                action=action,
                status=DriverActionStatus.FAILED_APPLY,
                errors=(
                    DriverIssue(
                        category=DriverIssueCategory.HARDWARE_REJECTED_COMMAND.value,
                        message=(
                            f"UKM-404 response did not confirm route command {command!r}: "
                            f"{response!r}"
                        ),
                    ),
                ),
                observed_state=dict(self.get_state()),
            )

        self._last_known_routes[device_port] = host_port
        warnings: list[DriverIssue] = []

        try:
            routes = self._query_route(device_port, timeout_seconds=action.timeout_seconds)
        except OreiUkm404TransportError as exc:
            self._last_error = str(exc)
            warnings.append(
                DriverIssue(
                    category=DriverIssueCategory.STATE_QUERY_FAILED.value,
                    message=f"Route applied, but UKM-404 state query failed: {exc}",
                )
            )
            observed_state = self._state_from_routes(
                self._last_known_routes,
                DriverObservedStateStatus.LAST_KNOWN,
                state_error=str(exc),
            )
        else:
            self._last_known_routes.update(routes)
            self._last_error = None
            observed_state = self._state_from_routes(
                self._last_known_routes,
                DriverObservedStateStatus.OBSERVED,
            )

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
            message=health.message or "Could not connect to UKM-404",
        )

    def _query_routes(self, *, timeout_seconds: float | None = None) -> dict[int, int]:
        routes: dict[int, int] = {}
        for device_port in range(MIN_USB_PORT, MAX_USB_PORT + 1):
            routes.update(self._query_route(device_port, timeout_seconds=timeout_seconds))
        return routes

    def _query_route(
        self,
        device_port: int,
        *,
        timeout_seconds: float | None = None,
    ) -> dict[int, int]:
        command = query_route_command(device_port)
        response = self._transport.send_command(command, timeout_seconds=timeout_seconds)
        routes = parse_route_response(response)
        if device_port not in routes:
            raise OreiUkm404TransportError(
                f"UKM-404 route query returned no route for device port {device_port}: {response!r}"
            )
        return {device_port: routes[device_port]}

    def _transport_failure_result(
        self,
        action: DriverAction,
        error: OreiUkm404TransportError,
    ) -> DriverActionResult:
        category = DriverIssueCategory.CONNECTION_FAILED.value
        if isinstance(error, OreiUkm404TimeoutError):
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

    def _validate_usb_port(
        self,
        port: int,
        port_kind: str,
        path: str,
    ) -> tuple[DriverIssue, ...]:
        if not _is_valid_usb_port(port):
            return (
                DriverIssue(
                    category=DriverIssueCategory.INVALID_PORT.value,
                    message=f"UKM-404 {port_kind} port {port!r} must be between 1 and 4",
                    path=path,
                ),
            )
        return ()

    def _state_from_routes(
        self,
        routes_by_device_port: Mapping[int, int],
        state_status: DriverObservedStateStatus,
        *,
        state_error: str | None = None,
    ) -> dict[str, Any]:
        routes = {
            str(device_port): str(host_port)
            for device_port, host_port in sorted(routes_by_device_port.items())
        }

        state: dict[str, Any] = {
            "connected": self._connected,
            "state_status": state_status.value,
            "routes": routes,
        }
        if state_error:
            state["state_error"] = state_error
        return state


def route_command(device_port: int, host_port: int) -> str:
    return f"set device {device_port} in host {host_port}"


def query_route_command(device_port: int) -> str:
    return f"get device {device_port} in host"


def parse_route_response(response: str) -> dict[int, int]:
    routes: dict[int, int] = {}
    for match in _ROUTE_PATTERN.finditer(response):
        device_port = int(match.group(1))
        host_port = int(match.group(2))
        routes[device_port] = host_port
    return routes


def response_confirms_route(response: str, *, device_port: int, host_port: int) -> bool:
    return parse_route_response(response).get(device_port) == host_port


def _default_capabilities() -> dict[str, str]:
    return {
        USB_ROUTING_CAPABILITY: DriverCapabilityStatus.SUPPORTED.value,
        "per_device_routing": DriverCapabilityStatus.SUPPORTED.value,
        ROUTE_QUERY_CAPABILITY: DriverCapabilityStatus.SUPPORTED.value,
        "usb3": DriverCapabilityStatus.SUPPORTED.value,
        "host_emulation": DriverCapabilityStatus.UNKNOWN.value,
        "device_emulation": DriverCapabilityStatus.UNKNOWN.value,
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


def _validate_optional_string_payload(
    action: DriverAction,
    fields: tuple[str, ...],
) -> tuple[DriverIssue, ...]:
    errors: list[DriverIssue] = []
    for field in fields:
        value = action.payload.get(field)
        if field in action.payload and not isinstance(value, str):
            errors.append(
                DriverIssue(
                    category=DriverIssueCategory.INVALID_ACTION.value,
                    message=f"Payload field {field!r} must be a string",
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
        raise ValueError(f"UKM-404 connection.{field} must be a number")
    if value <= 0:
        raise ValueError(f"UKM-404 connection.{field} must be positive")
    return float(value)


def _optional_str(connection: Mapping[str, Any], field: str, *, default: str) -> str:
    if field not in connection:
        return default
    value = connection[field]
    if not isinstance(value, str):
        raise ValueError(f"UKM-404 connection.{field} must be a string")
    return value


def _coerce_int(value: Any, path: str) -> int:
    if isinstance(value, bool):
        raise ValueError(f"UKM-404 {path} must be an integer")
    if isinstance(value, int):
        return value
    if isinstance(value, str) and value.isdecimal():
        return int(value)
    raise ValueError(f"UKM-404 {path} must be an integer")


def _is_valid_usb_port(port: int) -> bool:
    return MIN_USB_PORT <= port <= MAX_USB_PORT
