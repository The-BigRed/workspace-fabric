from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any, Protocol


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
