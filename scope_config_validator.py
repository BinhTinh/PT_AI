from datetime import datetime
from typing import Optional, Tuple

import taxonomy_registry as registry
import capability_vocabulary as vocab
from scope_config import ScopeConfig

TAXONOMY_VERSION = "2026"


def _result(campaign_id: Optional[str], passed: bool, reason_code: Optional[str], detail: str) -> dict:
    return {
        "layer": "scope_config",
        "campaign_id": campaign_id,
        "passed": passed,
        "reason_code": reason_code,
        "detail": detail,
    }


def _parse_aware(value: str, field_name: str) -> Tuple[Optional[datetime], Optional[str]]:
    try:
        dt = datetime.fromisoformat(value)
    except (ValueError, TypeError):
        return None, f"{field_name}='{value}' khong phai ISO8601 hop le."
    if dt.tzinfo is None:
        return None, f"{field_name}='{value}' thieu timezone offset (vd '+00:00' hoac 'Z')."
    return dt, None


def validate(scope: ScopeConfig) -> dict:
    campaign_id = scope.campaign_id if isinstance(scope.campaign_id, str) else None

    if not isinstance(scope.campaign_id, str) or not scope.campaign_id.strip():
        return _result(None, False, "SCOPECFG_MISSING_CAMPAIGN_ID", "campaign_id phai la str non-empty.")

    if not isinstance(scope.target_ref, str) or not scope.target_ref.strip():
        return _result(campaign_id, False, "SCOPECFG_MISSING_TARGET_REF", "target_ref phai la str non-empty.")

    if not isinstance(scope.authorized_asi, tuple) or not scope.authorized_asi:
        return _result(
            campaign_id, False, "SCOPECFG_EMPTY_AUTHORIZED_ASI",
            "authorized_asi phai co it nhat 1 ma ASI.",
        )
    for asi_id in scope.authorized_asi:
        if not registry.is_valid(asi_id, TAXONOMY_VERSION):
            return _result(
                campaign_id, False, "SCOPECFG_UNKNOWN_ASI",
                f"authorized_asi chua ma '{asi_id}' khong hop le hoac khong ACTIVE "
                f"trong taxonomy_version={TAXONOMY_VERSION}.",
            )

    if not isinstance(scope.capability_ceiling, tuple):
        return _result(
            campaign_id, False, "SCOPECFG_INVALID_CAPABILITY_CEILING",
            "capability_ceiling phai la tuple.",
        )
    for tag in scope.capability_ceiling:
        if not vocab.is_known(tag):
            return _result(
                campaign_id, False, "SCOPECFG_UNKNOWN_CAPABILITY_TAG",
                f"capability_ceiling chua tag '{tag}' khong ton tai trong "
                f"CAPABILITY_VERSION={vocab.CAPABILITY_VERSION}.",
            )

    start_dt, err = _parse_aware(scope.testing_window.start, "testing_window.start")
    if err:
        return _result(campaign_id, False, "SCOPECFG_INVALID_DATETIME", err)
    end_dt, err = _parse_aware(scope.testing_window.end, "testing_window.end")
    if err:
        return _result(campaign_id, False, "SCOPECFG_INVALID_DATETIME", err)
    if start_dt >= end_dt:
        return _result(
            campaign_id, False, "SCOPECFG_INVALID_WINDOW_ORDER",
            f"testing_window.start ({scope.testing_window.start}) phai truoc "
            f"testing_window.end ({scope.testing_window.end}).",
        )

    if not isinstance(scope.prohibited_actions, tuple):
        return _result(
            campaign_id, False, "SCOPECFG_INVALID_PROHIBITED_ACTIONS",
            "prohibited_actions phai la tuple (co the rong).",
        )
    if not all(isinstance(item, str) and item.strip() for item in scope.prohibited_actions):
        return _result(
            campaign_id, False, "SCOPECFG_INVALID_PROHIBITED_ACTIONS",
            "Moi phan tu trong prohibited_actions phai la str non-empty.",
        )

    if not isinstance(scope.stop_conditions, tuple) or not scope.stop_conditions:
        return _result(
            campaign_id, False, "SCOPECFG_EMPTY_STOP_CONDITIONS",
            "stop_conditions phai co it nhat 1 dieu kien dung khan cap.",
        )
    if not all(isinstance(item, str) and item.strip() for item in scope.stop_conditions):
        return _result(
            campaign_id, False, "SCOPECFG_INVALID_STOP_CONDITIONS",
            "Moi phan tu trong stop_conditions phai la str non-empty.",
        )

    if not isinstance(scope.authorization_statement, str) or not scope.authorization_statement.strip():
        return _result(
            campaign_id, False, "SCOPECFG_MISSING_AUTHORIZATION_STATEMENT",
            "authorization_statement phai la str non-empty.",
        )

    return _result(campaign_id, True, None, "ScopeConfig OK.")