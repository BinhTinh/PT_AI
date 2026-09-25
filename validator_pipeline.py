from typing import Optional

import catalogue_store as store
import structural_validator
import taxonomy_validator
import scope_validator
import applicability_validator
import scope_config_validator
import manifest_validator
from manifest import Manifest
from scope_config import ScopeConfig

_STAGE_ORDER = (
    "scope_config",
    "manifest",
    "catalogue",
    "seal",
    "structural",
    "taxonomy",
    "scope",
    "applicability",
)


def _pipeline_result(
    test_id: Optional[str],
    final_stage: str,
    passed: bool,
    layer_result: Optional[dict],
) -> dict:
    return {
        "test_id": test_id,
        "final_stage": final_stage,
        "passed": passed,
        "stage_order": _STAGE_ORDER,
        "layer_result": layer_result,
    }


def _fail(test_id: Optional[str], stage: str, layer_result: dict) -> dict:
    return _pipeline_result(test_id, stage, False, layer_result)


def validate_for_execution(
    test_id: str,
    scope: ScopeConfig,
    target_manifest: Manifest,
    testspecs_dir=store.TESTSPECS_DIR,
) -> dict:
    scope_ctx = scope_config_validator.validate(scope)
    if not scope_ctx["passed"]:
        return _fail(test_id, "scope_config", scope_ctx)

    manifest_ctx = manifest_validator.validate(target_manifest)
    if not manifest_ctx["passed"]:
        return _fail(test_id, "manifest", manifest_ctx)

    testspec = store.get(test_id, testspecs_dir)
    if testspec is None:
        return _fail(
            test_id, "catalogue",
            {
                "layer": "catalogue",
                "test_id": test_id,
                "passed": False,
                "reason_code": "CATALOGUE_NOT_FOUND",
                "detail": f"Khong tim thay TestSpec test_id={test_id} trong Catalogue.",
            },
        )

    seal_record = store.get_seal(test_id, testspecs_dir)
    if seal_record is None:
        return _fail(
            test_id, "seal",
            {
                "layer": "seal",
                "test_id": test_id,
                "passed": False,
                "reason_code": "SEAL_NOT_FROZEN",
                "detail": f"TestSpec test_id={test_id} con o trang thai DRAFT, "
                          f"chua duoc freeze_testspec.py dong bang. Khong the dung cho thuc thi.",
            },
        )

    integrity = store.verify_integrity(test_id, testspecs_dir)
    if integrity.get("match") is not True:
        return _fail(
            test_id, "seal",
            {
                "layer": "seal",
                "test_id": test_id,
                "passed": False,
                "reason_code": "SEAL_HASH_MISMATCH",
                "detail": f"Noi dung TestSpec hien tai khong khop hash da seal "
                          f"(TOCTOU): current={integrity.get('current_hash')}, "
                          f"sealed={integrity.get('sealed_hash')}.",
            },
        )

    r = structural_validator.validate(testspec)
    if not r["passed"]:
        return _fail(test_id, "structural", r)

    r = taxonomy_validator.validate(testspec)
    if not r["passed"]:
        return _fail(test_id, "taxonomy", r)

    r = scope_validator.validate(testspec, scope)
    if not r["passed"]:
        return _fail(test_id, "scope", r)

    r = applicability_validator.validate(testspec, scope, target_manifest)
    if not r["passed"]:
        return _fail(test_id, "applicability", r)

    return _pipeline_result(test_id, "applicability", True, r)