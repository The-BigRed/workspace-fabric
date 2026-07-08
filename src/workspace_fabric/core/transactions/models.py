from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Any

from workspace_fabric.core.capabilities import CapabilityDecision
from workspace_fabric.drivers import DriverAction, DriverActionPlan


class TransactionPlanStatus(StrEnum):
    PLANNED = "planned"
    FAILED_VALIDATION = "failed_validation"


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
