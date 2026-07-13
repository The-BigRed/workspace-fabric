from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class CapabilityStatus(StrEnum):
    SUPPORTED = "supported"
    UNSUPPORTED = "unsupported"
    UNKNOWN = "unknown"


class CapabilityPolicy(StrEnum):
    IGNORE = "ignore"
    PREFER = "prefer"
    REQUIRE = "require"
    DISABLE = "disable"


class CapabilityDecisionAction(StrEnum):
    APPLY = "apply"
    DISABLE = "disable"
    IGNORE = "ignore"
    BLOCK = "block"


@dataclass(frozen=True, slots=True)
class CapabilityRequest:
    name: str
    policy: CapabilityPolicy | str | None = CapabilityPolicy.IGNORE
    options: Mapping[str, Any] = field(default_factory=dict)
    path: str | None = None


@dataclass(frozen=True, slots=True)
class CapabilityDecision:
    capability: str
    policy: CapabilityPolicy
    status: CapabilityStatus
    action: CapabilityDecisionAction
    driver_id: str | None = None
    path: str | None = None


@dataclass(frozen=True, slots=True)
class CapabilityValidationIssue:
    category: str
    message: str
    path: str | None = None
    driver_id: str | None = None
    capability: str | None = None


@dataclass(frozen=True, slots=True)
class CapabilityValidationResult:
    warnings: tuple[CapabilityValidationIssue, ...] = ()
    errors: tuple[CapabilityValidationIssue, ...] = ()
    decisions: tuple[CapabilityDecision, ...] = ()

    @property
    def valid(self) -> bool:
        return not self.errors

    def combine(self, other: CapabilityValidationResult) -> CapabilityValidationResult:
        return CapabilityValidationResult(
            warnings=self.warnings + other.warnings,
            errors=self.errors + other.errors,
            decisions=self.decisions + other.decisions,
        )
