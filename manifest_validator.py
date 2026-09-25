import re
from datetime import datetime
from typing import Optional

import capability_vocabulary as vocab
from manifest import Manifest

_SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")


def _result(target_ref: Optional[str], passed: bool, reason_code: Optional[str], detail: str) -> dict:
    return {
        "layer": "manifest",
        "target_ref": target_ref,
        "passed": passed,
        "reason_code": reason_code,
        "detail": detail,
    }


def validate(manifest: Manifest) -> dict:
    target_ref = manifest.target_ref if isinstance(manifest.target_ref, str) else None

    if not isinstance(manifest.manifest_version, str) or not manifest.manifest_version.strip():
        return _result(target_ref, False, "MANIFEST_MISSING_VERSION", "manifest_version phai la str non-empty.")

    if not isinstance(manifest.target_ref, str) or not manifest.target_ref.strip():
        return _result(None, False, "MANIFEST_MISSING_TARGET_REF", "target_ref phai la str non-empty.")

    try:
        generated_dt = datetime.fromisoformat(manifest.generated_at)
    except (ValueError, TypeError):
        return _result(
            target_ref, False, "MANIFEST_INVALID_GENERATED_AT",
            f"generated_at='{manifest.generated_at}' khong phai ISO8601 hop le.",
        )
    if generated_dt.tzinfo is None:
        return _result(
            target_ref, False, "MANIFEST_NAIVE_GENERATED_AT",
            f"generated_at='{manifest.generated_at}' thieu timezone offset.",
        )

    if not isinstance(manifest.capabilities, dict) or not manifest.capabilities:
        return _result(
            target_ref, False, "MANIFEST_EMPTY_CAPABILITIES",
            "capabilities phai co it nhat 1 entry (ke ca present=False).",
        )

    known_tags = set(vocab.list_all())
    declared_tags = set(manifest.capabilities.keys())

    unknown_tags = declared_tags - known_tags
    if unknown_tags:
        return _result(
            target_ref, False, "MANIFEST_UNKNOWN_CAPABILITY_TAG",
            f"capabilities chua tag khong ton tai trong CAPABILITY_VERSION="
            f"{vocab.CAPABILITY_VERSION}: {sorted(unknown_tags)}.",
        )

    missing_tags = known_tags - declared_tags
    if missing_tags:
        return _result(
            target_ref, False, "MANIFEST_INCOMPLETE_CAPABILITIES",
            f"capabilities thieu khai bao cho tag: {sorted(missing_tags)} "
            f"(phai khai bao ro present=False neu target khong co, khong duoc bo qua).",
        )

    for tag, record in manifest.capabilities.items():
        if not isinstance(record.source, str) or not record.source.strip():
            return _result(
                target_ref, False, "MANIFEST_INVALID_CAPABILITY_SOURCE",
                f"CapabilityRecord cho '{tag}' thieu source hop le.",
            )
        if not isinstance(record.detail, str) or not record.detail.strip():
            return _result(
                target_ref, False, "MANIFEST_INVALID_CAPABILITY_DETAIL",
                f"CapabilityRecord cho '{tag}' thieu detail hop le.",
            )

    for sf in manifest.source_files:
        if not isinstance(sf.path, str) or not sf.path.strip():
            return _result(
                target_ref, False, "MANIFEST_INVALID_SOURCE_FILE_PATH",
                "source_files chua path rong.",
            )
        if not _SHA256_PATTERN.match(sf.sha256):
            return _result(
                target_ref, False, "MANIFEST_INVALID_SOURCE_FILE_HASH",
                f"source_files['{sf.path}'].sha256 khong dung dinh dang sha256 hex.",
            )

    return _result(target_ref, True, None, "Manifest OK.")