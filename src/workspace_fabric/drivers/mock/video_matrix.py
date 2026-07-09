from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from workspace_fabric.config.models import DriverConfig
from workspace_fabric.drivers.base import (
    DriverAction,
    DriverActionResult,
    DriverActionStatus,
    DriverActionType,
    DriverIssue,
    DriverIssueCategory,
    DriverValidationResult,
)
from workspace_fabric.drivers.mock.base import CAPABILITY_SUPPORTED, MockDriverBase

VIDEO_ROUTE_ACTION = DriverActionType.VIDEO_ROUTE.value
VIDEO_ROUTING_CAPABILITY = "video_routing"


class MockVideoMatrixDriver(MockDriverBase):
    driver_type = "mock_video_matrix"

    def __init__(
        self,
        driver_id: str,
        *,
        capabilities: Mapping[str, str] | None = None,
    ) -> None:
        default_capabilities = {
            VIDEO_ROUTING_CAPABILITY: CAPABILITY_SUPPORTED,
            "route_query": CAPABILITY_SUPPORTED,
        }
        default_capabilities.update(capabilities or {})
        super().__init__(driver_id, capabilities=default_capabilities)
        self._routes: dict[str, str] = {}

    @classmethod
    def from_config(cls, config: DriverConfig) -> MockVideoMatrixDriver:
        return cls(config.id, capabilities=config.capabilities)

    def get_state(self) -> Mapping[str, Any]:
        state = dict(super().get_state())
        state["routes"] = dict(self._routes)
        return state

    def route_action(
        self,
        *,
        source: str | None = None,
        destination: str | None = None,
        input_port: int | None = None,
        output_port: int | None = None,
    ) -> DriverAction:
        source_id = source if source is not None else f"input_{input_port}"
        destination_id = destination if destination is not None else f"output_{output_port}"
        payload: dict[str, Any] = {
            "source": source_id,
            "destination": destination_id,
        }
        if input_port is not None:
            payload["input_port"] = input_port
        if output_port is not None:
            payload["output_port"] = output_port

        return DriverAction(
            action_type=VIDEO_ROUTE_ACTION,
            payload=payload,
        )

    def validate_action(self, action: DriverAction) -> DriverValidationResult:
        errors: list[DriverIssue] = []
        if action.action_type != VIDEO_ROUTE_ACTION:
            errors.append(
                DriverIssue(
                    category=DriverIssueCategory.INVALID_ACTION.value,
                    message=f"Unsupported action type {action.action_type!r}",
                    path="$.action_type",
                )
            )
            return DriverValidationResult(valid=False, errors=tuple(errors))

        errors.extend(self._validate_required_payload(action, ("source", "destination")))
        errors.extend(self._validate_string_payload(action, ("source", "destination")))
        capability_error = self._validate_capability(
            VIDEO_ROUTING_CAPABILITY,
            "$.capabilities.video_routing",
        )
        if capability_error is not None:
            errors.append(capability_error)

        return DriverValidationResult(valid=not errors, errors=tuple(errors))

    def plan_action(self, action: DriverAction):
        validation = self.validate_action(action)
        return self._planned_steps(
            action,
            validation,
            (
                (
                    "route video source "
                    f"{action.payload.get('source')!r} to {action.payload.get('destination')!r}"
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

        destination = action.payload["destination"]
        source = action.payload["source"]
        self._routes[destination] = source
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
