from __future__ import annotations

from collections.abc import Mapping
from datetime import UTC, datetime
from typing import Any, Protocol

from workspace_fabric.core.transactions.history import InMemoryTransactionHistory
from workspace_fabric.core.transactions.models import (
    TransactionActionResult,
    TransactionPlan,
    TransactionPlanAction,
    TransactionPlanIssue,
    TransactionResult,
    TransactionResultStatus,
)
from workspace_fabric.drivers import (
    DriverAction,
    DriverActionResult,
    DriverActionStatus,
    DriverIssue,
)


class ExecutionDriver(Protocol):
    id: str

    def apply_action(self, action: DriverAction) -> DriverActionResult: ...

    def get_state(self) -> Mapping[str, Any]: ...


def execute_plan(
    plan: TransactionPlan,
    drivers: Mapping[str, ExecutionDriver],
    *,
    history: InMemoryTransactionHistory | None = None,
) -> TransactionResult:
    return TransactionExecutor(drivers, history=history).execute(plan)


class TransactionExecutor:
    def __init__(
        self,
        drivers: Mapping[str, ExecutionDriver],
        *,
        history: InMemoryTransactionHistory | None = None,
    ) -> None:
        self._drivers = drivers
        self.history = history or InMemoryTransactionHistory()

    def execute(self, plan: TransactionPlan) -> TransactionResult:
        if not plan.valid:
            return self._record(
                TransactionResult(
                    id=plan.id,
                    workspace_id=plan.workspace_id,
                    plan=plan,
                    status=TransactionResultStatus.FAILED_VALIDATION,
                    warnings=plan.warnings,
                    errors=plan.errors,
                    observed_state={},
                    recorded_at=datetime.now(UTC),
                )
            )

        warnings = list(plan.warnings)
        errors: list[TransactionPlanIssue] = []
        action_results: list[TransactionActionResult] = []
        observed_state: dict[str, Any] = {}

        for action_index, planned_action in enumerate(plan.actions):
            action_result = self._execute_action(planned_action, action_index)
            action_results.append(action_result)
            warnings.extend(action_result.warnings)
            errors.extend(action_result.errors)
            if action_result.observed_state is not None:
                observed_state[action_result.driver_id] = action_result.observed_state

        result = TransactionResult(
            id=plan.id,
            workspace_id=plan.workspace_id,
            plan=plan,
            status=_result_status(action_results, warnings, errors),
            action_results=tuple(action_results),
            warnings=tuple(warnings),
            errors=tuple(errors),
            observed_state=observed_state,
            recorded_at=datetime.now(UTC),
        )
        return self._record(result)

    def _execute_action(
        self,
        planned_action: TransactionPlanAction,
        action_index: int,
    ) -> TransactionActionResult:
        driver = self._drivers.get(planned_action.driver_id)
        if driver is None:
            issue = TransactionPlanIssue(
                category="missing_driver",
                message=f"No driver instance was provided for {planned_action.driver_id!r}",
                path=planned_action.path,
                driver_id=planned_action.driver_id,
                action_index=action_index,
            )
            return TransactionActionResult(
                action_index=action_index,
                driver_id=planned_action.driver_id,
                action=planned_action.action,
                path=planned_action.path,
                status=DriverActionStatus.FAILED_APPLY,
                errors=(issue,),
            )

        driver_result = driver.apply_action(planned_action.action)
        warnings = tuple(
            _driver_issue_to_transaction_issue(issue, planned_action, action_index)
            for issue in driver_result.warnings
        )
        errors = tuple(
            _driver_issue_to_transaction_issue(issue, planned_action, action_index)
            for issue in driver_result.errors
        )
        return TransactionActionResult(
            action_index=action_index,
            driver_id=planned_action.driver_id,
            action=planned_action.action,
            path=planned_action.path,
            status=driver_result.status,
            warnings=warnings,
            errors=errors,
            observed_state=dict(driver_result.observed_state),
        )

    def _record(self, result: TransactionResult) -> TransactionResult:
        return self.history.record(result)


def _driver_issue_to_transaction_issue(
    issue: DriverIssue,
    planned_action: TransactionPlanAction,
    action_index: int,
) -> TransactionPlanIssue:
    return TransactionPlanIssue(
        category=issue.category,
        message=issue.message,
        path=issue.path or planned_action.path,
        driver_id=planned_action.driver_id,
        action_index=action_index,
    )


def _result_status(
    action_results: list[TransactionActionResult],
    warnings: list[TransactionPlanIssue],
    errors: list[TransactionPlanIssue],
) -> TransactionResultStatus:
    if not errors:
        if warnings:
            return TransactionResultStatus.SUCCESS_WITH_WARNINGS
        return TransactionResultStatus.SUCCESS

    success_count = sum(1 for action_result in action_results if action_result.successful)
    if success_count:
        return TransactionResultStatus.PARTIAL_SUCCESS

    if any(result.status is DriverActionStatus.FAILED_APPLY for result in action_results):
        return TransactionResultStatus.FAILED_APPLY
    if any(result.status is DriverActionStatus.FAILED_VALIDATION for result in action_results):
        return TransactionResultStatus.FAILED_VALIDATION
    return TransactionResultStatus.UNKNOWN
