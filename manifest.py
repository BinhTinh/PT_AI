"""
manifest.py — Ground truth ve kha nang thuc te cua target, sinh tu soi source code.
Doc lap voi ScopeConfig va TestSpec. Khong tu suy dien, chi luu lai ket qua khao sat.
"""

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Tuple


@dataclass(frozen=True)
class CapabilityRecord:
    present: bool
    source: str
    detail: str


@dataclass(frozen=True)
class SourceFile:
    path: str
    sha256: str


@dataclass(frozen=True)
class Manifest:
    manifest_version: str
    target_ref: str
    generated_at: str
    capabilities: Dict[str, CapabilityRecord] = field(default_factory=dict)
    structural_properties: Dict[str, str] = field(default_factory=dict)
    source_files: Tuple[SourceFile, ...] = field(default_factory=tuple)


def hash_file(path: Path) -> str:
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def build_manifest(
    manifest_version: str,
    target_ref: str,
    capabilities: Dict[str, CapabilityRecord],
    structural_properties: Dict[str, str],
    source_paths: Tuple[Path, ...],
) -> Manifest:
    source_files = tuple(
        SourceFile(path=str(p), sha256=hash_file(p)) for p in source_paths
    )
    return Manifest(
        manifest_version=manifest_version,
        target_ref=target_ref,
        generated_at=datetime.now(timezone.utc).isoformat(),
        capabilities=capabilities,
        structural_properties=structural_properties,
        source_files=source_files,
    )


def save(manifest: Manifest, path: Path) -> Path:
    data = {
        "manifest_version": manifest.manifest_version,
        "target_ref": manifest.target_ref,
        "generated_at": manifest.generated_at,
        "capabilities": {
            tag: {
                "present": rec.present,
                "source": rec.source,
                "detail": rec.detail,
            }
            for tag, rec in manifest.capabilities.items()
        },
        "structural_properties": manifest.structural_properties,
        "source_files": [
            {"path": sf.path, "sha256": sf.sha256} for sf in manifest.source_files
        ],
    }
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def load(path: Path) -> Manifest:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    capabilities = {
        tag: CapabilityRecord(
            present=rec["present"], source=rec["source"], detail=rec["detail"]
        )
        for tag, rec in data["capabilities"].items()
    }
    source_files = tuple(
        SourceFile(path=sf["path"], sha256=sf["sha256"]) for sf in data["source_files"]
    )

    return Manifest(
        manifest_version=data["manifest_version"],
        target_ref=data["target_ref"],
        generated_at=data["generated_at"],
        capabilities=capabilities,
        structural_properties=data["structural_properties"],
        source_files=source_files,
    )


def has_capability(manifest: Manifest, tag: str) -> bool:
    record = manifest.capabilities.get(tag)
    return record is not None and record.present


def is_stale(manifest: Manifest) -> dict:
    mismatches = []
    for sf in manifest.source_files:
        current_path = Path(sf.path)
        if not current_path.exists():
            mismatches.append({"path": sf.path, "reason": "missing"})
            continue
        current_hash = hash_file(current_path)
        if current_hash != sf.sha256:
            mismatches.append(
                {"path": sf.path, "reason": "hash_mismatch", "current_sha256": current_hash}
            )
    return {"stale": bool(mismatches), "mismatches": mismatches}
