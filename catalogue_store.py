

import hashlib
import json
import logging
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger(__name__)

TESTSPECS_DIR = Path("testspecs")
SEALS_FILE = TESTSPECS_DIR / ".seals.json"

_EXCLUDED_KEYS = {"_source_file"}


def _iter_testspec_files(testspecs_dir: Path = TESTSPECS_DIR):
    if not testspecs_dir.exists():
        return
    for path in sorted(testspecs_dir.glob("*.json")):
        if path.name == SEALS_FILE.name:
            continue
        yield path


def load_all(testspecs_dir: Path = TESTSPECS_DIR) -> list[dict]:
    results = []
    for path in _iter_testspec_files(testspecs_dir):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            logger.warning("Bỏ qua TestSpec lỗi %s: %s", path, e)
            continue
        if not isinstance(data, dict) or "test_id" not in data:
            logger.warning("Bỏ qua TestSpec thiếu test_id: %s", path)
            continue
        data["_source_file"] = str(path)
        results.append(data)
    return results


def get(test_id: str, testspecs_dir: Path = TESTSPECS_DIR) -> dict | None:
    for spec in load_all(testspecs_dir):
        if spec.get("test_id") == test_id:
            return spec
    return None


def list_by_asi(asi_id: str, testspecs_dir: Path = TESTSPECS_DIR) -> list[dict]:
    return [spec for spec in load_all(testspecs_dir) if spec.get("asi_id") == asi_id]


def list_test_ids(testspecs_dir: Path = TESTSPECS_DIR) -> set[str]:
    return {spec["test_id"] for spec in load_all(testspecs_dir)}


def content_hash(testspec: dict) -> str:
    """Hash canonical, độc lập thứ tự key và field nội bộ (_source_file)."""
    clean = {k: v for k, v in testspec.items() if k not in _EXCLUDED_KEYS}
    canonical = json.dumps(clean, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _load_seals(testspecs_dir: Path = TESTSPECS_DIR) -> dict:
    seals_path = testspecs_dir / SEALS_FILE.name
    if not seals_path.exists():
        return {}
    try:
        with open(seals_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        logger.warning("Không đọc được %s: %s", seals_path, e)
        return {}


def _write_seals(seals: dict, testspecs_dir: Path = TESTSPECS_DIR) -> None:
    seals_path = testspecs_dir / SEALS_FILE.name
    testspecs_dir.mkdir(parents=True, exist_ok=True)
    with open(seals_path, "w", encoding="utf-8") as f:
        json.dump(seals, f, ensure_ascii=False, indent=2)


def seal(test_id: str, testspecs_dir: Path = TESTSPECS_DIR) -> dict:
    """Catalogue tự ghi nhận hash + thời điểm ghi cho TestSpec đã tồn tại trên đĩa.
    Gọi ngay sau khi create_testspec.py ghi file. Ghi đè seal cũ nếu gọi lại cho cùng test_id.
    """
    spec = get(test_id, testspecs_dir)
    if spec is None:
        raise ValueError(f"Không tìm thấy TestSpec test_id={test_id} để seal")

    record = {
        "test_id": test_id,
        "content_hash": content_hash(spec),
        "sealed_at": datetime.now(timezone.utc).isoformat(),
    }

    seals = _load_seals(testspecs_dir)
    seals[test_id] = record
    _write_seals(seals, testspecs_dir)
    return record


def get_seal(test_id: str, testspecs_dir: Path = TESTSPECS_DIR) -> dict | None:
    return _load_seals(testspecs_dir).get(test_id)


def verify_integrity(test_id: str, testspecs_dir: Path = TESTSPECS_DIR) -> dict:
    """Trả về dữ liệu so sánh hash hiện tại vs hash đã seal. Không phán quyết pass/fail."""
    spec = get(test_id, testspecs_dir)
    seal_record = get_seal(test_id, testspecs_dir)

    if spec is None:
        return {"test_id": test_id, "status": "not_found", "match": None}
    if seal_record is None:
        return {"test_id": test_id, "status": "unsealed", "match": None}

    current_hash = content_hash(spec)
    sealed_hash = seal_record.get("content_hash")
    return {
        "test_id": test_id,
        "status": "sealed",
        "match": current_hash == sealed_hash,
        "current_hash": current_hash,
        "sealed_hash": sealed_hash,
        "sealed_at": seal_record.get("sealed_at"),
    }
