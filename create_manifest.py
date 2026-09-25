from pathlib import Path

import capability_vocabulary as vocab
import manifest_validator as validator
from manifest import Manifest, CapabilityRecord, build_manifest, save

OUTPUT_DIR = Path(__file__).resolve().parent / "manifests"
MANIFEST_VERSION = "1"

_SOURCE_CHOICES = ("code_review", "manual_test", "tool_descriptor", "agent_log")


def ask(prompt: str, allow_empty: bool = False) -> str:
    while True:
        value = input(prompt).strip()
        if value or allow_empty:
            return value
        print(" -> Khong duoc de trong, nhap lai.")


def ask_yes_no(prompt: str) -> bool:
    while True:
        value = ask(prompt + " (y/n): ").lower()
        if value in ("y", "yes"):
            return True
        if value in ("n", "no"):
            return False
        print(" -> Chi nhap y hoac n.")


def ask_source() -> str:
    print(f"  Nguon xac nhan hop le: {', '.join(_SOURCE_CHOICES)}")
    while True:
        value = ask("  source: ")
        if value in _SOURCE_CHOICES:
            return value
        print(f" -> source phai la mot trong: {_SOURCE_CHOICES}.")


def collect_capabilities() -> dict:
    capabilities = {}
    print(f"\nKhai bao tung capability tag (CAPABILITY_VERSION={vocab.CAPABILITY_VERSION}), "
          f"BAT BUOC du 100%, ke ca khi target khong co:")
    for tag in vocab.list_all():
        print(f"\n[{tag}] {vocab.describe(tag)}")
        present = ask_yes_no("  Target co capability nay khong?")
        source = ask_source()
        detail = ask("  detail (bang chung/ly do cu the): ")
        capabilities[tag] = CapabilityRecord(present=present, source=source, detail=detail)
    return capabilities


def collect_structural_properties() -> dict:
    print("\nNhap structural_properties dang key=value, de trong key de dung lai:")
    props = {}
    while True:
        raw = ask("  key=value: ", allow_empty=True)
        if not raw:
            break
        if "=" not in raw:
            print(" -> Phai dung dinh dang key=value.")
            continue
        key, _, value = raw.partition("=")
        key, value = key.strip(), value.strip()
        if not key or not value:
            print(" -> key va value deu khong duoc rong.")
            continue
        props[key] = value
    return props


def collect_source_paths() -> tuple:
    print("\nNhap duong dan file source can hash de theo doi staleness, de trong de dung lai:")
    paths = []
    while True:
        raw = ask("  path: ", allow_empty=True)
        if not raw:
            break
        p = Path(raw)
        if not p.exists() or not p.is_file():
            print(f" -> File '{raw}' khong ton tai, nhap lai.")
            continue
        paths.append(p)
    return tuple(paths)


def build_target_manifest() -> Manifest:
    target_ref = ask("target_ref: ")
    capabilities = collect_capabilities()
    structural_properties = collect_structural_properties()
    source_paths = collect_source_paths()
    return build_manifest(
        manifest_version=MANIFEST_VERSION,
        target_ref=target_ref,
        capabilities=capabilities,
        structural_properties=structural_properties,
        source_paths=source_paths,
    )


def save_manifest(manifest: Manifest) -> Path:
    OUTPUT_DIR.mkdir(exist_ok=True)
    path = OUTPUT_DIR / f"{manifest.target_ref}_{manifest.manifest_version}.json"
    save(manifest, path)
    print(f"\nDa luu Manifest vao: {path}")
    return path


def main() -> None:
    print("=== Khao sat va tao Manifest moi ===")
    while True:
        manifest = build_target_manifest()
        result = validator.validate(manifest)
        if result["passed"]:
            break
        print(f"\n -> Manifest khong hop le: [{result['reason_code']}] {result['detail']}")
        print(" -> Nhap lai toan bo Manifest.\n")
    save_manifest(manifest)


if __name__ == "__main__":
    main()