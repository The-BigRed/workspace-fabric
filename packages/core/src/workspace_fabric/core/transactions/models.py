from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import Any

from workspace_fabric.core.capabilities import CapabilityDecision
from workspace_fabric.drivers import DriverAction, DriverActionPlan, DriverActionStatus


class TransactionPlanStatus(StrEnum):
    PLANNED = "planned"
    FAILED_VALIDATION = "failed_validation"


class TransactionResultStatus(StrEnum):
    SUCCESS = "success"
    SUCCESS_WITH_WARNINGS = "success_with_warnings"
    PARTIAL_SUCCESS = "partial_success"
    FAILED_VALIDATION = "failed_validation"
    FAILED_APPLY = "failed_apply"
    UNKNOWN = "unknown"


@dataclass(frozen=True, slots=True)
class TransactionPlanIssue:
    category: str
    message: str
    path: str | None = None
    driver_id: str | None = None
    action_index: int | None = None

    def dump(self) -> dict[str, Any]:
        data: dict[str, Any] = {
            "category": self.category,
            "message": self.message,
        }
        if self.path is not None:
            data["path"] = self.path
        if self.driver_id is not None:
            data["driver"] = self.driver_id
        if self.action_index is not None:
            data["action_index"] = self.action_index
        return data


@dataclass(frozen=True, slots=True)
class TransactionPlanAction:
    driver_id: str
    action: DriverAction
    path: str
    driver_plan: DriverActionPlan

    @property
    def action_type(self) -> str:
        return self.action.action_type

    @property
    def payload(self) -> dict[str, Any]:
        return dict(self.action.payload)

    def dump(self) -> dict[str, Any]:
        return {
            "driver": self.driver_id,
            "type": self.action.action_type,
            "path": self.path,
            "status": self.driver_plan.status.value,
            "steps": list(self.driver_plan.steps),
            **self.action.payload,
        }


@dataclass(frozen=True, slots=True)
class TransactionPlan:
    id: str
    workspace_id: str
    actions: tuple[TransactionPlanAction, ...] = ()
    warnings: tuple[TransactionPlanIssue, ...] = ()
    errors: tuple[TransactionPlanIssue, ...] = ()
    capability_decisions: tuple[CapabilityDecision, ...] = ()

    @property
    def valid(self) -> bool:
        return not self.errors

    @property
    def status(self) -> TransactionPlanStatus:
        if self.errors:
            return TransactionPlanStatus.FAILED_VALIDATION
        return TransactionPlanStatus.PLANNED

    def dry_run_output(self) -> dict[str, Any]:
        return {
            "transaction": {
                "id": self.id,
                "workspace": self.workspace_id,
                "status": self.status.value,
                "dry_run": True,
                "actions": [action.dump() for action in self.actions],
                "warnings": [warning.dump() for warning in self.warnings],
                "errors": [error.dump() for error in self.errors],
            }
        }


@dataclass(frozen=True, slots=True)
class TransactionActionResult:
    action_index: int
    driver_id: str
    action: DriverAction
    path: str
    status: DriverActionStatus
    warnings: tuple[TransactionPlanIssue, ...] = ()
    errors: tuple[TransactionPlanIssue, ...] = ()
    observed_state: dict[str, Any] | None = None

    @property
    def successful(self) -> bool:
        return self.status is DriverActionStatus.SUCCESS

    def dump(self) -> dict[str, Any]:
        data: dict[str, Any] = {
            "index": self.action_index,
            "driver": self.driver_id,
            "type": self.action.action_type,
            "path": self.path,
            "status": self.status.value,
            "warnings": [warning.dump() for warning in self.warnings],
            "errors": [error.dump() for error in self.errors],
            **self.action.payload,
        }
        if self.observed_state is not None:
            data["observed_state"] = self.observed_state
        return data


@dataclass(frozen=True, slots=True)
class TransactionResult:
    id: str
    workspace_id: str
    plan: TransactionPlan
    status: TransactionResultStatus
    action_results: tuple[TransactionActionResult, ...] = ()
    warnings: tuple[TransactionPlanIssue, ...] = ()
    errors: tuple[TransactionPlanIssue, ...] = ()
    observed_state: dict[str, Any] | None = None
    recorded_at: datetime | None = None

    @property
    def successful(self) -> bool:
        return self.status in {
            TransactionResultStatus.SUCCESS,
            TransactionResultStatus.SUCCESS_WITH_WARNINGS,
        }

    def dump(self) -> dict[str, Any]:
        transaction: dict[str, Any] = {
            "id": self.id,
            "workspace": self.workspace_id,
            "status": self.status.value,
            "dry_run": False,
            "planned_actions": [action.dump() for action in self.plan.actions],
            "actions": [result.dump() for result in self.action_results],
            "warnings": [warning.dump() for warning in self.warnings],
            "errors": [error.dump() for error in self.errors],
        }
        if self.observed_state is not None:
            transaction["observed_state"] = self.observed_state
        if self.recorded_at is not None:
            transaction["recorded_at"] = self.recorded_at.isoformat()
        return {"transaction": transaction}
