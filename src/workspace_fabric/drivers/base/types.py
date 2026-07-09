from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any, Protocol, runtime_checkable


class DriverCapabilityStatus(StrEnum):
    SUPPORTED = "supported"
    UNSUPPORTED = "unsupported"
    UNKNOWN = "unknown"


class DriverIssueCategory(StrEnum):
    CONNECTION_FAILED = "connection_failed"
    TIMEOUT = "timeout"
    UNSUPPORTED_CAPABILITY = "unsupported_capability"
    INVALID_RESOURCE = "invalid_resource"
    INVALID_PORT = "invalid_port"
    INVALID_ROUTE = "invalid_route"
    INVALID_ACTION = "invalid_action"
    HARDWARE_REJECTED_COMMAND = "hardware_rejected_command"
    STATE_QUERY_FAILED = "state_query_failed"
    PARTIAL_APPLY = "partial_apply"
    AUTHENTICATION_FAILED = "authentication_failed"
    AUTHORIZATION_FAILED = "authorization_failed"
    MOCK_FAILURE = "mock_failure"
    UNKNOWN_ERROR = "unknown_error"


class DriverActionType(StrEnum):
    VIDEO_ROUTE = "video_route"
    USB_ROUTE = "usb_route"


class DriverObservedStateStatus(StrEnum):
    OBSERVED = "observed"
    LAST_KNOWN = "last_known"
    ASSUMED = "assumed"
    UNKNOWN = "unknown"


class DriverHealthStatus(StrEnum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNREACHABLE = "unreachable"
    UNKNOWN = "unknown"


class DriverActionStatus(StrEnum):
    PLANNED = "planned"
    SUCCESS = "success"
    FAILED_VALIDATION = "failed_validation"
    FAILED_APPLY = "failed_apply"


@dataclass(frozen=True, slots=True)
class DriverIssue:
    category: str
    message: str
    path: str | None = None


@dataclass(frozen=True, slots=True)
class DriverHealth:
    status: DriverHealthStatus
    message: str = ""


@dataclass(frozen=True, slots=True)
class DriverAction:
    action_type: str
    payload: dict[str, Any] = field(default_factory=dict)
    timeout_seconds: float | None = None


@dataclass(frozen=True, slots=True)
class DriverValidationResult:
    valid: bool
    warnings: tuple[DriverIssue, ...] = ()
    errors: tuple[DriverIssue, ...] = ()


@dataclass(frozen=True, slots=True)
class DriverActionPlan:
    driver_id: str
    action: DriverAction
    status: DriverActionStatus
    steps: tuple[str, ...] = ()
    warnings: tuple[DriverIssue, ...] = ()
    errors: tuple[DriverIssue, ...] = ()


@dataclass(frozen=True, slots=True)
class DriverActionResult:
    driver_id: str
    action: DriverAction
    status: DriverActionStatus
    warnings: tuple[DriverIssue, ...] = ()
    errors: tuple[DriverIssue, ...] = ()
    observed_state: dict[str, Any] = field(default_factory=dict)


@runtime_checkable
class Driver(Protocol):
    id: str

    def connect(self) -> DriverHealth: ...

    def disconnect(self) -> DriverHealth: ...

    def health(self) -> DriverHealth: ...

    def get_capabilities(self) -> Mapping[str, str]: ...

    def get_state(self) -> Mapping[str, Any]: ...

    def validate_action(self, action: DriverAction) -> DriverValidationResult: ...

    def plan_action(self, action: DriverAction) -> DriverActionPlan: ...

    def apply_action(self, action: DriverAction) -> DriverActionResult: ...


@runtime_checkable
class VideoMatrixDriver(Driver, Protocol):
    def route_action(self, *, input_port: int, output_port: int) -> DriverAction: ...


@runtime_checkable
class UsbMatrixDriver(Driver, Protocol):
    def route_action(
        self,
        *,
        device: str,
        host: str,
        device_port: int,
        host_port: int,
    ) -> DriverAction: ...
