from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ConfigValidationIssue:
    path: str
    message: str

    def __str__(self) -> str:
        return f"{self.path}: {self.message}"


class ConfigValidationError(ValueError):
    def __init__(self, issues: Sequence[ConfigValidationIssue]) -> None:
        if not issues:
            raise ValueError("ConfigValidationError requires at least one issue")

        self.issues = tuple(issues)
        super().__init__(self._format_message())

    def _format_message(self) -> str:
        details = "\n".join(f"- {issue}" for issue in self.issues)
        return f"Configuration validation failed:\n{details}"
