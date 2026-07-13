from __future__ import annotations

from workspace_fabric.core.transactions.models import TransactionResult


class InMemoryTransactionHistory:
    def __init__(self) -> None:
        self._records: list[TransactionResult] = []

    def record(self, result: TransactionResult) -> TransactionResult:
        self._records.append(result)
        return result

    def all(self) -> tuple[TransactionResult, ...]:
        return tuple(self._records)

    def get(self, transaction_id: str) -> TransactionResult | None:
        for result in reversed(self._records):
            if result.id == transaction_id:
                return result
        return None

    def clear(self) -> None:
        self._records.clear()
