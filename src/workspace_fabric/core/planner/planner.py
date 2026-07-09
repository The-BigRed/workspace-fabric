from __future__ import annotations

from collections.abc import Mapping
from typing import Protocol
from uuid import uuid4

from workspace_fabric.core.capabilities import (
    CapabilityProvider,
    CapabilityValidationIssue,
    validate_workspace_capabilities,
)
from workspace_fabric.core.graph import ResourceGraph, ResourceGraphError
from workspace_fabric.core.transactions import (
    TransactionPlan,
    TransactionPlanAction,
    TransactionPlanIssue,
)
from workspace_fabric.drivers import DriverAction, DriverActionPlan, DriverActionType, DriverIssue

VIDEO_ROUTE_ACTION = DriverActionType.VIDEO_ROUTE.value
USB_ROUTE_ACTION = DriverActionType.USB_ROUTE.value


class PlanningDriver(CapabilityProvider, Protocol):
    def plan_action(self, action: DriverAction) -> DriverActionPlan: ...


def plan_workspace(
    graph: ResourceGraph,
    workspace_id: str,
    drivers: Mapping[str, PlanningDriver],
    *,
    transaction_id: str | None = None,
) -> TransactionPlan:
    return TransactionPlanner(graph, drivers).plan_workspace(
        workspace_id,
        transaction_id=transaction_id,
    )


class TransactionPlanner:
    def __init__(
        self,
        graph: ResourceGraph,
        drivers: Mapping[str, PlanningDriver],
    ) -> None:
        self._graph = graph
        self._drivers = drivers

    def plan_workspace(
        self,
        workspace_id: str,
        *,
        transaction_id: str | None = None,
    ) -> TransactionPlan:
        plan_id = transaction_id or f"tx_{uuid4().hex}"
        workspace = self._graph.config.workspaces.get(workspace_id)
        if workspace is None:
            return TransactionPlan(
                id=plan_id,
                workspace_id=workspace_id,
                errors=(
                    TransactionPlanIssue(
                        category="unknown_workspace",
                        message=f"Unknown workspace {workspace_id!r}",
                        path=f"$.workspaces.{workspace_id}",
                    ),
                ),
            )

        capability_result = validate_workspace_capabilities(
            self._graph,
            workspace_id,
            self._drivers,
        )
        warnings = [_capability_issue_to_plan_issue(issue) for issue in capability_result.warnings]
        errors = [_capability_issue_to_plan_issue(issue) for issue in capability_result.errors]
        if errors:
            return TransactionPlan(
                id=plan_id,
                workspace_id=workspace_id,
                warnings=tuple(warnings),
                errors=tuple(errors),
                capability_decisions=capability_result.decisions,
            )

        actions: list[TransactionPlanAction] = []
        for display_id, route in workspace.video.items():
            route_path = f"$.workspaces.{workspace_id}.video.{display_id}"
            try:
                resolution = self._graph.resolve_video_route(display_id, route.source)
            except ResourceGraphError as exc:
                errors.extend(_graph_error_to_plan_issues(exc))
                continue

            self._append_driver_plan(
                actions,
                warnings,
                errors,
                driver_id=resolution.driver.id,
                action=DriverAction(
                    action_type=VIDEO_ROUTE_ACTION,
                    payload={
                        "source": resolution.source.id,
                        "destination": resolution.display.id,
                    },
                ),
                path=route_path,
            )

        for device_id, host_id in workspace.usb.items():
            route_path = f"$.workspaces.{workspace_id}.usb.{device_id}"
            try:
                resolution = self._graph.resolve_usb_route(device_id, host_id)
            except ResourceGraphError as exc:
                errors.extend(_graph_error_to_plan_issues(exc))
                continue

            self._append_driver_plan(
                actions,
                warnings,
                errors,
                driver_id=resolution.driver.id,
                action=DriverAction(
                    action_type=USB_ROUTE_ACTION,
                    payload={
                        "device": resolution.device.id,
                        "host": resolution.host.id,
                        "device_port": resolution.device_port,
                        "host_port": resolution.host_port,
                    },
                ),
                path=route_path,
            )

        return TransactionPlan(
            id=plan_id,
            workspace_id=workspace_id,
            actions=tuple(actions),
            warnings=tuple(warnings),
            errors=tuple(errors),
            capability_decisions=capability_result.decisions,
        )

    def _append_driver_plan(
        self,
        actions: list[TransactionPlanAction],
        warnings: list[TransactionPlanIssue],
        errors: list[TransactionPlanIssue],
        *,
        driver_id: str,
        action: DriverAction,
        path: str,
    ) -> None:
        driver = self._drivers.get(driver_id)
        if driver is None:
            errors.append(
                TransactionPlanIssue(
                    category="missing_driver",
                    message=f"No driver instance was provided for {driver_id!r}",
                    path=path,
                    driver_id=driver_id,
                )
            )
            return

        action_index = len(actions)
        driver_plan = driver.plan_action(action)
        actions.append(
            TransactionPlanAction(
                driver_id=driver_id,
                action=action,
                path=path,
                driver_plan=driver_plan,
            )
        )
        warnings.extend(
            _driver_issue_to_plan_issue(issue, driver_id, action_index)
            for issue in driver_plan.warnings
        )
        errors.extend(
            _driver_issue_to_plan_issue(issue, driver_id, action_index)
            for issue in driver_plan.errors
        )


def _capability_issue_to_plan_issue(issue: CapabilityValidationIssue) -> TransactionPlanIssue:
    return TransactionPlanIssue(
        category=issue.category,
        message=issue.message,
        path=issue.path,
        driver_id=issue.driver_id,
    )


def _driver_issue_to_plan_issue(
    issue: DriverIssue,
    driver_id: str,
    action_index: int,
) -> TransactionPlanIssue:
    return TransactionPlanIssue(
        category=issue.category,
        message=issue.message,
        path=issue.path,
        driver_id=driver_id,
        action_index=action_index,
    )


def _graph_error_to_plan_issues(error: ResourceGraphError) -> list[TransactionPlanIssue]:
    return [
        TransactionPlanIssue(
            category="invalid_resource_route",
            message=issue.message,
            path=issue.path,
        )
        for issue in error.issues
    ]
