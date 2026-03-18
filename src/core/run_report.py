from __future__ import annotations

import time
from dataclasses import dataclass

from .models import EvaluationResult


@dataclass
class RunReport:
    total_rows: int
    failed_rows: int
    started_at: float
    ended_at: float

    @property
    def duration_seconds(self) -> float:
        return max(0.0, self.ended_at - self.started_at)


def build_report(results: list[EvaluationResult], started_at: float) -> RunReport:
    ended = time.time()
    failed = sum(1 for r in results if r.error_reason)
    return RunReport(
        total_rows=len(results),
        failed_rows=failed,
        started_at=started_at,
        ended_at=ended,
    )

