from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ResourceGraphIssue:
    path: str
    message: str

    def __str__(self) -> str:
        return f"{self.path}: {self.message}"


class ResourceGraphError(ValueError):
    def __init__(self, issues: Sequence[ResourceGraphIssue]) -> None:
        if not issues:
            raise ValueError("ResourceGraphError requires at least one issue")

        self.issues = tuple(issues)
        super().__init__(self._format_message())

    def _format_message(self) -> str:
        details = "\n".join(f"- {issue}" for issue in self.issues)
        return f"Resource graph validation failed:\n{details}"
