from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

from workspace_fabric_driver_api import (
    DriverAction,
    DriverActionPlan,
    DriverActionResult,
    DriverActionStatus,
    DriverCapabilityStatus,
    DriverHealth,
    DriverHealthStatus,
    DriverIssue,
    DriverIssueCategory,
    DriverValidationResult,
)

try:
    from workspace_fabric.config.models import DriverConfig
except ImportError:
    # Fallback for when running driver tests independently
    from dataclasses import dataclass

    @dataclass
    class DriverConfig:
        id: str
        type: str
        fabric: str
        connection: dict[str, Any] | None = None
        capabilities: dict[str, Any] | None = None


CAPABILITY_SUPPORTED = DriverCapabilityStatus.SUPPORTED.value
CAPABILITY_UNKNOWN = DriverCapabilityStatus.UNKNOWN.value
CAPABILITY_UNSUPPORTED = DriverCapabilityStatus.UNSUPPORTED.value


class MockDriverBase:
    driver_type = "mock"

    def __init__(
        self,
        driver_id: str,
        *,
        capabilities: Mapping[str, str] | None = None,
    ) -> None:
        self.id = driver_id
        self._capabilities = dict(capabilities or {})
        self._connected = False
        self._fail_next: dict[str, DriverIssue] = {}
        self._failed_action_types: dict[str, DriverIssue] = {}

    @classmethod
    def from_config(cls, config: DriverConfig) -> MockDriverBase:
        return cls(config.id, capabilities=config.capabilities)

    def connect(self) -> DriverHealth:
        self._connected = True
        return DriverHealth(DriverHealthStatus.HEALTHY)

    def disconnect(self) -> DriverHealth:
        self._connected = False
        return DriverHealth(DriverHealthStatus.UNKNOWN, "Driver is disconnected")

    def health(self) -> DriverHealth:
        if self._connected:
            return DriverHealth(DriverHealthStatus.HEALTHY)
        return DriverHealth(DriverHealthStatus.UNKNOWN, "Driver is disconnected")

    def get_capabilities(self) -> Mapping[str, str]:
        return dict(self._capabilities)

    def get_state(self) -> Mapping[str, Any]:
        return {"connected": self._connected}

    def fail_next_action(
        self,
        action_type: str,
        message: str = "Injected mock driver failure",
        *,
        category: str = DriverIssueCategory.MOCK_FAILURE.value,
    ) -> None:
        self._fail_next[action_type] = DriverIssue(category=category, message=message)

    def fail_action_type(
        self,
        action_type: str,
        message: str = "Injected mock driver failure",
        *,
        category: str = DriverIssueCategory.MOCK_FAILURE.value,
    ) -> None:
        self._failed_action_types[action_type] = DriverIssue(category=category, message=message)

    def clear_failures(self) -> None:
        self._fail_next.clear()
        self._failed_action_types.clear()

    def _validate_capability(self, capability: str, path: str) -> DriverIssue | None:
        status = self._capabilities.get(capability, CAPABILITY_UNKNOWN)
        if status == CAPABILITY_SUPPORTED:
            return None

        return DriverIssue(
            category=DriverIssueCategory.UNSUPPORTED_CAPABILITY.value,
            message=f"Capability {capability!r} is {status!r} for driver {self.id!r}",
            path=path,
        )

    def _validate_required_payload(
        self,
        action: DriverAction,
        required_fields: Iterable[str],
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

    def _validation_failure_result(
        self,
        action: DriverAction,
        validation: DriverValidationResult,
    ) -> DriverActionResult:
        return DriverActionResult(
            driver_id=self.id,
            action=action,
            status=DriverActionStatus.FAILED_VALIDATION,
            warnings=validation.warnings,
            errors=validation.errors,
            observed_state=dict(self.get_state()),
        )

    def _failure_for(self, action_type: str) -> DriverIssue | None:
        if action_type in self._fail_next:
            return self._fail_next.pop(action_type)
        return self._failed_action_types.get(action_type)

    def _failure_result(self, action: DriverAction, issue: DriverIssue) -> DriverActionResult:
        return DriverActionResult(
            driver_id=self.id,
            action=action,
            status=DriverActionStatus.FAILED_APPLY,
            errors=(issue,),
            observed_state=dict(self.get_state()),
        )

    def _planned_steps(
        self,
        action: DriverAction,
        validation: DriverValidationResult,
        steps: tuple[str, ...],
    ) -> DriverActionPlan:
        status = DriverActionStatus.PLANNED
        if not validation.valid:
            status = DriverActionStatus.FAILED_VALIDATION

        return DriverActionPlan(
            driver_id=self.id,
            action=action,
            status=status,
            steps=steps if validation.valid else (),
            warnings=validation.warnings,
            errors=validation.errors,
        )
