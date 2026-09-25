
from typing import Optional

import taxonomy_registry as registry
import attack_type_framework as framework
import capability_vocabulary as vocab

TAXONOMY_VERSION = "2026"


def _result(
    test_id: Optional[str],
    passed: bool,
    reason_code: Optional[str],
    detail: str,
    taxonomy_version: str = TAXONOMY_VERSION,
    capability_version: str = vocab.CAPABILITY_VERSION,
) -> dict:
    return {
        "layer": "taxonomy",
        "test_id": test_id,
        "passed": passed,
        "reason_code": reason_code,
        "detail": detail,
        "taxonomy_version": taxonomy_version,
        "capability_version": capability_version,
    }


def validate(testspec: dict) -> dict:
    test_id = testspec.get("test_id")
    asi_id = testspec.get("asi_id", "")

    if not registry.is_valid(asi_id, TAXONOMY_VERSION):
        return _result(
            test_id, False, "TAXO_UNKNOWN_ASI",
            f"asi_id '{asi_id}' khong ton tai hoac khong ACTIVE trong taxonomy_version={TAXONOMY_VERSION}.",
        )

    definition = framework.get_definition(asi_id)
    if definition is None:
        return _result(
            test_id, False, "TAXO_NO_FRAMEWORK_DEFINED",
            f"asi_id '{asi_id}' hop le trong Registry nhung chua co AttackTypeDefinition.",
        )

    mechanism = testspec.get("mechanism", {})
    required_mechanism = set(framework.required_mechanism_fields(asi_id))
    actual_mechanism = set(mechanism.keys())
    if actual_mechanism != required_mechanism:
        missing = required_mechanism - actual_mechanism
        extra = actual_mechanism - required_mechanism
        return _result(
            test_id, False, "TAXO_MECHANISM_FIELD_MISMATCH",
            f"mechanism khong khop attack_type='{definition.attack_type}'. "
            f"Thieu: {sorted(missing)}, Du: {sorted(extra)}.",
        )

    evidence = testspec.get("evidence", {})
    required_evidence = set(framework.required_evidence_fields(asi_id))
    actual_evidence = set(evidence.keys())
    if actual_evidence != required_evidence:
        missing = required_evidence - actual_evidence
        extra = actual_evidence - required_evidence
        return _result(
            test_id, False, "TAXO_EVIDENCE_FIELD_MISMATCH",
            f"evidence khong khop attack_type='{definition.attack_type}'. "
            f"Thieu: {sorted(missing)}, Du: {sorted(extra)}.",
        )

    for namespace_name, namespace in (("mechanism", mechanism), ("evidence", evidence)):
        for key, value in namespace.items():
            if not isinstance(value, str) or not value.strip():
                return _result(
                    test_id, False, "TAXO_EMPTY_FIELD_VALUE",
                    f"Field '{namespace_name}.{key}' phai la str non-empty "
                    f"(attack_type='{definition.attack_type}').",
                )

    prerequisites = testspec.get("prerequisites", [])
    for tag in prerequisites:
        if not vocab.is_known(tag):
            return _result(
                test_id, False, "TAXO_UNKNOWN_CAPABILITY_TAG",
                f"Capability tag '{tag}' khong ton tai trong CAPABILITY_VERSION={vocab.CAPABILITY_VERSION}.",
            )

    return _result(test_id, True, None, "Taxonomy OK.")