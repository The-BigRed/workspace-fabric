from __future__ import annotations

from collections.abc import Mapping
from typing import Protocol

from workspace_fabric.config.models import CapabilityRequestConfig
from workspace_fabric.core.capabilities.models import (
    CapabilityDecision,
    CapabilityDecisionAction,
    CapabilityPolicy,
    CapabilityRequest,
    CapabilityStatus,
    CapabilityValidationIssue,
    CapabilityValidationResult,
)
from workspace_fabric.core.graph import ResourceGraph, ResourceGraphError


class CapabilityProvider(Protocol):
    id: str

    def get_capabilities(self) -> Mapping[str, str]: ...


def validate_capability_request(
    capabilities: Mapping[str, str],
    request: CapabilityRequest,
    *,
    driver_id: str | None = None,
) -> CapabilityValidationResult:
    policy, policy_error = _coerce_policy(request.policy, request)
    status, status_error = _coerce_status(capabilities.get(request.name), request, driver_id)
    if policy_error is not None or status_error is not None:
        return CapabilityValidationResult(
            errors=tuple(issue for issue in (policy_error, status_error) if issue is not None),
            decisions=(
                _decision(request, policy, status, CapabilityDecisionAction.BLOCK, driver_id),
            ),
        )

    if policy is CapabilityPolicy.IGNORE:
        return CapabilityValidationResult(
            decisions=(
                _decision(request, policy, status, CapabilityDecisionAction.IGNORE, driver_id),
            )
        )

    if policy is CapabilityPolicy.DISABLE:
        action = (
            CapabilityDecisionAction.DISABLE
            if status is CapabilityStatus.SUPPORTED
            else CapabilityDecisionAction.IGNORE
        )
        return CapabilityValidationResult(
            decisions=(_decision(request, policy, status, action, driver_id),)
        )

    if status is CapabilityStatus.SUPPORTED:
        return CapabilityValidationResult(
            decisions=(
                _decision(request, policy, status, CapabilityDecisionAction.APPLY, driver_id),
            )
        )

    issue = _support_issue(request, policy, status, driver_id)
    action = (
        CapabilityDecisionAction.IGNORE
        if policy is CapabilityPolicy.PREFER
        else CapabilityDecisionAction.BLOCK
    )
    result = CapabilityValidationResult(
        decisions=(_decision(request, policy, status, action, driver_id),)
    )
    if policy is CapabilityPolicy.PREFER:
        return CapabilityValidationResult(
            warnings=(issue,),
            decisions=result.decisions,
        )

    return CapabilityValidationResult(
        errors=(issue,),
        decisions=result.decisions,
    )


def validate_capability_requests(
    capabilities: Mapping[str, str],
    requests: Mapping[str, CapabilityRequest],
    *,
    driver_id: str | None = None,
) -> CapabilityValidationResult:
    result = CapabilityValidationResult()
    for request in requests.values():
        result = result.combine(
            validate_capability_request(capabilities, request, driver_id=driver_id)
        )
    return result


def validate_workspace_capabilities(
    graph: ResourceGraph,
    workspace_id: str,
    drivers: Mapping[str, CapabilityProvider],
) -> CapabilityValidationResult:
    workspace = graph.config.workspaces.get(workspace_id)
    if workspace is None:
        return CapabilityValidationResult(
            errors=(
                CapabilityValidationIssue(
                    category="unknown_workspace",
                    message=f"Unknown workspace {workspace_id!r}",
                    path=f"$.workspaces.{workspace_id}",
                ),
            )
        )

    result = CapabilityValidationResult()
    for display_id, route in workspace.video.items():
        if not route.capabilities:
            continue

        route_path = f"$.workspaces.{workspace_id}.video.{display_id}"
        try:
            resolution = graph.resolve_video_route(display_id, route.source)
        except ResourceGraphError as exc:
            result = result.combine(_graph_error_result(route_path, exc))
            continue

        driver_id = resolution.driver.id
        driver = drivers.get(driver_id)
        if driver is None:
            result = result.combine(_missing_driver_result(driver_id, route_path))
            continue

        result = result.combine(
            validate_capability_requests(
                driver.get_capabilities(),
                _workspace_capability_requests(route.capabilities, route_path),
                driver_id=driver_id,
            )
        )

    return result


def _workspace_capability_requests(
    requests: Mapping[str, CapabilityRequestConfig],
    route_path: str,
) -> dict[str, CapabilityRequest]:
    return {
        name: CapabilityRequest(
            name=request.name,
            policy=request.policy,
            options=request.options,
            path=f"{route_path}.{name}",
        )
        for name, request in requests.items()
    }


def _coerce_policy(
    value: CapabilityPolicy | str | None,
    request: CapabilityRequest,
) -> tuple[CapabilityPolicy, CapabilityValidationIssue | None]:
    if value is None:
        return CapabilityPolicy.IGNORE, None
    if isinstance(value, CapabilityPolicy):
        return value, None
    try:
        return CapabilityPolicy(value), None
    except ValueError:
        expected = ", ".join(policy.value for policy in CapabilityPolicy)
        return CapabilityPolicy.IGNORE, CapabilityValidationIssue(
            category="invalid_capability_policy",
            message=(
                f"Capability {request.name!r} uses unknown policy {value!r}; "
                f"expected one of {expected}"
            ),
            path=_request_path(request, "policy"),
            capability=request.name,
        )


def _coerce_status(
    value: str | CapabilityStatus | None,
    request: CapabilityRequest,
    driver_id: str | None,
) -> tuple[CapabilityStatus, CapabilityValidationIssue | None]:
    if value is None:
        return CapabilityStatus.UNKNOWN, None
    if isinstance(value, CapabilityStatus):
        return value, None
    try:
        return CapabilityStatus(value), None
    except ValueError:
        expected = ", ".join(status.value for status in CapabilityStatus)
        return CapabilityStatus.UNKNOWN, CapabilityValidationIssue(
            category="invalid_capability_status",
            message=(
                f"Driver {driver_id!r} reported unknown status {value!r} for "
                f"capability {request.name!r}; expected one of {expected}"
            ),
            path=_request_path(request),
            driver_id=driver_id,
            capability=request.name,
        )


def _decision(
    request: CapabilityRequest,
    policy: CapabilityPolicy,
    status: CapabilityStatus,
    action: CapabilityDecisionAction,
    driver_id: str | None,
) -> CapabilityDecision:
    return CapabilityDecision(
        capability=request.name,
        policy=policy,
        status=status,
        action=action,
        driver_id=driver_id,
        path=_request_path(request),
    )


def _support_issue(
    request: CapabilityRequest,
    policy: CapabilityPolicy,
    status: CapabilityStatus,
    driver_id: str | None,
) -> CapabilityValidationIssue:
    category = (
        "unsupported_capability" if status is CapabilityStatus.UNSUPPORTED else "unknown_capability"
    )
    consequence = (
        "continuing without it"
        if policy is CapabilityPolicy.PREFER
        else "validation cannot continue"
    )
    return CapabilityValidationIssue(
        category=category,
        message=(
            f"Capability {request.name!r} is {status.value!r} for driver {driver_id!r}; "
            f"policy is {policy.value!r}, {consequence}"
        ),
        path=_request_path(request),
        driver_id=driver_id,
        capability=request.name,
    )


def _missing_driver_result(driver_id: str, path: str) -> CapabilityValidationResult:
    return CapabilityValidationResult(
        errors=(
            CapabilityValidationIssue(
                category="missing_driver",
                message=f"No driver instance was provided for {driver_id!r}",
                path=path,
                driver_id=driver_id,
            ),
        )
    )


def _graph_error_result(path: str, error: ResourceGraphError) -> CapabilityValidationResult:
    return CapabilityValidationResult(
        errors=(
            CapabilityValidationIssue(
                category="invalid_resource_route",
                message=str(error),
                path=path,
            ),
        )
    )


def _request_path(request: CapabilityRequest, child: str | None = None) -> str:
    path = request.path or f"$.capabilities.{request.name}"
    if child is None:
        return path
    return f"{path}.{child}"
