from pathlib import Path

import taxonomy_registry as registry
import capability_vocabulary as vocab
import scope_config_validator as validator
from scope_config import ScopeConfig, TestingWindow, save

TAXONOMY_VERSION = "2026"
OUTPUT_DIR = Path(__file__).resolve().parent / "scope_configs"


def ask(prompt: str, allow_empty: bool = False) -> str:
    while True:
        value = input(prompt).strip()
        if value or allow_empty:
            return value
        print(" -> Khong duoc de trong, nhap lai.")


def ask_list(prompt: str, allow_empty: bool = False) -> list:
    while True:
        raw = ask(prompt, allow_empty=True)
        items = [item.strip() for item in raw.split(",") if item.strip()]
        if items or allow_empty:
            return items
        print(" -> Can it nhat 1 muc, nhap lai.")


def ask_authorized_asi() -> tuple:
    print("\nCac ma ASI dang ACTIVE trong Taxonomy Registry (version %s):" % TAXONOMY_VERSION)
    for entry in registry.list_all(TAXONOMY_VERSION):
        print(f"  {entry.asi_id} - {entry.title} [{entry.status.value}]")
    while True:
        raw = ask("Chon cac ma ASI duoc phep test, cach nhau boi dau phay: ")
        asi_ids = [a.strip().upper() for a in raw.split(",") if a.strip()]
        invalid = [a for a in asi_ids if not registry.is_valid(a, TAXONOMY_VERSION)]
        if invalid:
            print(f" -> Ma khong hop le/khong ACTIVE: {invalid}. Chon lai.")
            continue
        if not asi_ids:
            print(" -> Can it nhat 1 ma ASI.")
            continue
        return tuple(asi_ids)


def ask_capability_ceiling() -> tuple:
    known = vocab.list_all()
    print(f"\nCac capability tag hop le (CAPABILITY_VERSION={vocab.CAPABILITY_VERSION}):")
    for tag in known:
        print(f"  {tag} - {vocab.describe(tag)}")
    while True:
        raw = ask("Chon tran capability duoc phep dung, cach nhau boi dau phay: ")
        tags = [t.strip() for t in raw.split(",") if t.strip()]
        invalid = [t for t in tags if not vocab.is_known(t)]
        if invalid:
            print(f" -> Tag khong hop le: {invalid}. Chon lai.")
            continue
        return tuple(tags)


def ask_testing_window() -> TestingWindow:
    print("\ntesting_window can dinh dang ISO8601 co timezone, vd: 2026-09-25T00:00:00+07:00")
    start = ask("testing_window.start: ")
    end = ask("testing_window.end: ")
    return TestingWindow(start=start, end=end)


def build_scope_config() -> ScopeConfig:
    campaign_id = ask("campaign_id: ")
    target_ref = ask("target_ref: ")
    authorized_asi = ask_authorized_asi()
    capability_ceiling = ask_capability_ceiling()
    testing_window = ask_testing_window()
    prohibited_actions = tuple(ask_list(
        "prohibited_actions (hanh dong bi cam du trong scope, cach nhau boi dau phay, "
        "de trong neu khong co): ", allow_empty=True,
    ))
    stop_conditions = tuple(ask_list(
        "stop_conditions (dieu kien dung khan cap, bat buoc it nhat 1, cach nhau boi dau phay): ",
        allow_empty=False,
    ))
    authorization_statement = ask("authorization_statement (xac nhan quyen cho phep test): ")

    return ScopeConfig(
        campaign_id=campaign_id,
        target_ref=target_ref,
        authorized_asi=authorized_asi,
        capability_ceiling=capability_ceiling,
        testing_window=testing_window,
        prohibited_actions=prohibited_actions,
        stop_conditions=stop_conditions,
        authorization_statement=authorization_statement,
    )


def save_scope_config(scope: ScopeConfig) -> Path:
    OUTPUT_DIR.mkdir(exist_ok=True)
    path = OUTPUT_DIR / f"{scope.campaign_id}.json"
    save(scope, path)
    print(f"\nDa luu ScopeConfig vao: {path}")
    return path


def main() -> None:
    print("=== Tao ScopeConfig moi ===")
    while True:
        scope = build_scope_config()
        result = validator.validate(scope)
        if result["passed"]:
            break
        print(f"\n -> ScopeConfig khong hop le: [{result['reason_code']}] {result['detail']}")
        print(" -> Nhap lai toan bo ScopeConfig.\n")
    save_scope_config(scope)


if __name__ == "__main__":
    main()