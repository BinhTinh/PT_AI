import re
from typing import Optional

REQUIRED_BASE_FIELDS = (
    "test_id",
    "asi_id",
    "prerequisites",
    "target_surface",
    "attack_objective",
    "setup",
    "payload_template",
    "execution_method",
    "expected_evidence",
    "rule",
    "success_condition",
    "inconclusive_condition",
)

REQUIRED_STR_FIELDS = (
    "test_id",
    "asi_id",
    "target_surface",
    "attack_objective",
    "setup",
    "payload_template",
    "execution_method",
    "expected_evidence",
    "rule",
    "success_condition",
    "inconclusive_condition",
)

ALLOWED_EXTRA_FIELDS = {
    "mechanism",
    "evidence",
    "taxonomy_version",
    "capability_version",
    "attack_type",
    "_source_file",
}

ASI_ID_PATTERN = re.compile(r"^ASI\d{2}$")


def _result(test_id: Optional[str], passed: bool, reason_code: Optional[str], detail: str) -> dict:
    return {
        "layer": "structural",
        "test_id": test_id,
        "passed": passed,
        "reason_code": reason_code,
        "detail": detail,
    }


def validate(testspec: dict) -> dict:
    test_id = testspec.get("test_id") if isinstance(testspec, dict) else None

    if not isinstance(testspec, dict):
        return _result(None, False, "STRUCT_INVALID_TYPE", "TestSpec khong phai dict.")

    for field in REQUIRED_BASE_FIELDS:
        if field not in testspec:
            return _result(test_id, False, "STRUCT_MISSING_FIELD", f"Thieu field bat buoc: {field}")

    for field in REQUIRED_STR_FIELDS:
        value = testspec.get(field)
        if not isinstance(value, str) or not value.strip():
            return _result(test_id, False, "STRUCT_INVALID_TYPE", f"Field '{field}' phai la str non-empty.")

    prerequisites = testspec.get("prerequisites")
    if not isinstance(prerequisites, list) or not prerequisites or not all(
        isinstance(item, str) and item.strip() for item in prerequisites
    ):
        return _result(
            test_id, False, "STRUCT_INVALID_TYPE",
            "Field 'prerequisites' phai la list[str] non-empty.",
        )

    asi_id = testspec.get("asi_id", "")
    if not ASI_ID_PATTERN.match(asi_id):
        return _result(
            test_id, False, "STRUCT_MALFORMED_ASI_ID",
            f"asi_id '{asi_id}' khong dung dinh dang ASIxx.",
        )

    success_condition = testspec.get("success_condition", "").strip()
    inconclusive_condition = testspec.get("inconclusive_condition", "").strip()
    if success_condition == inconclusive_condition:
        return _result(
            test_id, False, "STRUCT_CONTRADICTORY_CONDITIONS",
            "success_condition va inconclusive_condition trung nhau hoac deu rong.",
        )

    for field in ("mechanism", "evidence"):
        if field not in testspec or not isinstance(testspec[field], dict):
            return _result(
                test_id, False, "STRUCT_MISSING_FIELD",
                f"Thieu namespace mo rong bat buoc '{field}' (phai la dict).",
            )
        namespace = testspec[field]
        if not namespace:
            return _result(
                test_id, False, "STRUCT_EMPTY_NAMESPACE",
                f"Namespace '{field}' khong duoc rong.",
            )
        for key, value in namespace.items():
            if not isinstance(value, str) or not value.strip():
                return _result(
                    test_id, False, "STRUCT_EMPTY_FIELD_VALUE",
                    f"Field '{field}.{key}' phai la str non-empty.",
                )

    allowed_fields = set(REQUIRED_BASE_FIELDS) | ALLOWED_EXTRA_FIELDS
    unknown_fields = set(testspec.keys()) - allowed_fields
    if unknown_fields:
        return _result(
            test_id, False, "STRUCT_UNKNOWN_FIELD",
            f"Field khong nam trong schema: {sorted(unknown_fields)}",
        )

    return _result(test_id, True, None, "Structural OK.")