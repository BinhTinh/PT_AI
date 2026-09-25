from datetime import datetime, timezone
from typing import Optional

from scope_config import ScopeConfig


def _result(
    test_id: Optional[str],
    passed: bool,
    reason_code: Optional[str],
    detail: str,
    campaign_id: str,
) -> dict:
    return {
        "layer": "scope",
        "test_id": test_id,
        "passed": passed,
        "reason_code": reason_code,
        "detail": detail,
        "campaign_id": campaign_id,
    }


def validate(testspec: dict, scope: ScopeConfig, now: Optional[datetime] = None) -> dict:
    test_id = testspec.get("test_id")
    asi_id = testspec.get("asi_id", "")
    prerequisites = set(testspec.get("prerequisites", []))

    if asi_id not in scope.authorized_asi:
        return _result(
            test_id, False, "SCOPE_ASI_NOT_AUTHORIZED",
            f"asi_id '{asi_id}' khong nam trong authorized_asi cua campaign '{scope.campaign_id}'.",
            scope.campaign_id,
        )

    ceiling = set(scope.capability_ceiling)
    if not prerequisites.issubset(ceiling):
        exceeded = prerequisites - ceiling
        return _result(
            test_id, False, "SCOPE_CAPABILITY_EXCEEDS_CEILING",
            f"prerequisites vuot capability_ceiling: {sorted(exceeded)}.",
            scope.campaign_id,
        )

    try:
        start = datetime.fromisoformat(scope.testing_window.start)
        end = datetime.fromisoformat(scope.testing_window.end)
    except (ValueError, TypeError):
        return _result(
            test_id, False, "SCOPE_INVALID_DATETIME",
            f"testing_window co gia tri khong phai ISO8601 hop le: "
            f"start='{scope.testing_window.start}', end='{scope.testing_window.end}'.",
            scope.campaign_id,
        )

    if start.tzinfo is None or end.tzinfo is None:
        return _result(
            test_id, False, "SCOPE_NAIVE_DATETIME",
            "testing_window.start/end thieu timezone offset.",
            scope.campaign_id,
        )

    current_time = now or datetime.now(timezone.utc)
    if not (start <= current_time <= end):
        return _result(
            test_id, False, "SCOPE_OUTSIDE_TESTING_WINDOW",
            f"Thoi diem {current_time.isoformat()} nam ngoai testing_window "
            f"[{scope.testing_window.start}, {scope.testing_window.end}].",
            scope.campaign_id,
        )

    return _result(test_id, True, None, "Scope OK.", scope.campaign_id)