from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from workspace_fabric.config.models import DriverConfig
from workspace_fabric.drivers.base import (
    DriverAction,
    DriverActionPlan,
    DriverActionResult,
    DriverActionStatus,
    DriverActionType,
    DriverIssue,
    DriverIssueCategory,
    DriverValidationResult,
)
from workspace_fabric.drivers.mock.base import CAPABILITY_SUPPORTED, MockDriverBase

USB_ROUTE_ACTION = DriverActionType.USB_ROUTE.value
USB_ROUTING_CAPABILITY = "usb_routing"


class MockUsbMatrixDriver(MockDriverBase):
    driver_type = "mock_usb_matrix"

    def __init__(
        self,
        driver_id: str,
        *,
        capabilities: Mapping[str, str] | None = None,
    ) -> None:
        default_capabilities = {
            USB_ROUTING_CAPABILITY: CAPABILITY_SUPPORTED,
            "route_query": CAPABILITY_SUPPORTED,
        }
        default_capabilities.update(capabilities or {})
        super().__init__(driver_id, capabilities=default_capabilities)
        self._routes: dict[str, str] = {}

    @classmethod
    def from_config(cls, config: DriverConfig) -> MockUsbMatrixDriver:
        return cls(config.id, capabilities=config.capabilities)

    def get_state(self) -> Mapping[str, Any]:
        state = dict(super().get_state())
        state["routes"] = dict(self._routes)
        return state

    def route_action(
        self,
        *,
        device_port: int,
        host_port: int,
        device: str | None = None,
        host: str | None = None,
    ) -> DriverAction:
        device_id = device if device is not None else f"device_{device_port}"
        host_id = host if host is not None else f"host_{host_port}"
        return DriverAction(
            action_type=USB_ROUTE_ACTION,
            payload={
                "device": device_id,
                "host": host_id,
                "device_port": device_port,
                "host_port": host_port,
            },
        )

    def validate_action(self, action: DriverAction) -> DriverValidationResult:
        errors: list[DriverIssue] = []
        if action.action_type != USB_ROUTE_ACTION:
            errors.append(
                DriverIssue(
                    category=DriverIssueCategory.INVALID_ACTION.value,
                    message=f"Unsupported action type {action.action_type!r}",
                    path="$.action_type",
                )
            )
            return DriverValidationResult(valid=False, errors=tuple(errors))

        errors.extend(
            self._validate_required_payload(action, ("device", "host", "device_port", "host_port"))
        )
        errors.extend(self._validate_string_payload(action, ("device", "host")))
        errors.extend(self._validate_positive_int_payload(action, ("device_port", "host_port")))
        capability_error = self._validate_capability(
            USB_ROUTING_CAPABILITY,
            "$.capabilities.usb_routing",
        )
        if capability_error is not None:
            errors.append(capability_error)

        return DriverValidationResult(valid=not errors, errors=tuple(errors))

    def plan_action(self, action: DriverAction) -> DriverActionPlan:
        validation = self.validate_action(action)
        return self._planned_steps(
            action,
            validation,
            (
                (
                    "route USB device "
                    f"{action.payload.get('device')!r} to host {action.payload.get('host')!r}"
                ),
            ),
        )

    def apply_action(self, action: DriverAction) -> DriverActionResult:
        validation = self.validate_action(action)
        if not validation.valid:
            return self._validation_failure_result(action, validation)

        failure = self._failure_for(action.action_type)
        if failure is not None:
            return self._failure_result(action, failure)

        device = action.payload["device"]
        host = action.payload["host"]
        self._routes[device] = host
        return DriverActionResult(
            driver_id=self.id,
            action=action,
            status=DriverActionStatus.SUCCESS,
            observed_state=dict(self.get_state()),
        )

    def _validate_string_payload(
        self,
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

    def _validate_positive_int_payload(
        self,
        action: DriverAction,
        fields: tuple[str, ...],
    ) -> tuple[DriverIssue, ...]:
        errors: list[DriverIssue] = []
        for field in fields:
            value = action.payload.get(field)
            if field not in action.payload:
                continue
            if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
                errors.append(
                    DriverIssue(
                        category=DriverIssueCategory.INVALID_PORT.value,
                        message=f"Payload field {field!r} must be a positive integer",
                        path=f"$.payload.{field}",
                    )
                )
        return tuple(errors)
