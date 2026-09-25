
from typing import Optional

from manifest import Manifest, has_capability, is_stale
from scope_config import ScopeConfig


def _result(
    test_id: Optional[str],
    passed: bool,
    reason_code: Optional[str],
    detail: str,
    manifest_version: str,
) -> dict:
    return {
        "layer": "applicability",
        "test_id": test_id,
        "passed": passed,
        "reason_code": reason_code,
        "detail": detail,
        "manifest_version": manifest_version,
    }


def validate(testspec: dict, scope: ScopeConfig, target_manifest: Manifest) -> dict:
    test_id = testspec.get("test_id")

    if target_manifest.target_ref != scope.target_ref:
        return _result(
            test_id, False, "APPLIC_MANIFEST_TARGET_MISMATCH",
            f"Manifest.target_ref='{target_manifest.target_ref}' khong khop "
            f"ScopeConfig.target_ref='{scope.target_ref}'.",
            target_manifest.manifest_version,
        )

    staleness = is_stale(target_manifest)
    if staleness["stale"]:
        return _result(
            test_id, False, "APPLIC_MANIFEST_STALE",
            f"Manifest khong con khop voi source hien tai: {staleness['mismatches']}.",
            target_manifest.manifest_version,
        )

    prerequisites = testspec.get("prerequisites", [])
    for tag in prerequisites:
        if not has_capability(target_manifest, tag):
            return _result(
                test_id, False, "APPLIC_CAPABILITY_NOT_PRESENT",
                f"Capability '{tag}' khong co trong Manifest cua target "
                f"'{target_manifest.target_ref}'.",
                target_manifest.manifest_version,
            )

    return _result(test_id, True, None, "Applicability OK.", target_manifest.manifest_version)
