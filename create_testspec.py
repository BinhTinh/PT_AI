import json
from pathlib import Path

import taxonomy_registry as registry
import attack_type_framework as framework
import capability_vocabulary as vocab
import catalogue_store as store

TAXONOMY_VERSION = "2026"
OUTPUT_DIR = Path("testspecs")


def ask(prompt: str, allow_empty: bool = False) -> str:
    while True:
        value = input(prompt).strip()
        if value or allow_empty:
            return value
        print(" -> Khong duoc de trong, nhap lai.")


def ask_capability_list(prompt: str) -> list:
    known = vocab.list_all()
    print(f"\n{prompt}")
    print("Cac capability tag hop le (CAPABILITY_VERSION=%s):" % vocab.CAPABILITY_VERSION)
    for tag in known:
        print(f"  {tag} - {vocab.describe(tag)}")

    while True:
        raw = ask("Nhap cac tag can, cach nhau boi dau phay: ")
        tags = [t.strip() for t in raw.split(",") if t.strip()]
        invalid = [t for t in tags if not vocab.is_known(t)]
        if invalid:
            print(f" -> Tag khong hop le: {invalid}. Chon lai trong danh sach tren.")
            continue
        if not tags:
            print(" -> Can it nhat 1 tag.")
            continue
        return tags


def ask_unique_test_id() -> str:
    existing_ids = store.list_test_ids()
    while True:
        test_id = ask("test_id (vd: TestSpec1_ASI01): ")
        if test_id in existing_ids:
            print(f" -> test_id '{test_id}' da ton tai trong Catalogue. Chon id khac.")
            continue
        return test_id


def choose_asi_id() -> tuple:
    print("\nCac ma ASI dang co trong Taxonomy Registry (version %s):" % TAXONOMY_VERSION)
    for entry in registry.list_all(TAXONOMY_VERSION):
        has_framework = "co khung tao" if framework.get_definition(entry.asi_id) else "CHUA co khung tao"
        print(f"  {entry.asi_id} - {entry.title} [{entry.status.value}] ({has_framework})")

    while True:
        asi_id = ask("\nChon ma ASI (vd: ASI01): ").upper()

        if not registry.is_valid(asi_id, TAXONOMY_VERSION):
            print(f" -> {asi_id} khong hop le hoac khong ACTIVE trong version {TAXONOMY_VERSION}. Chon lai.")
            continue

        definition = framework.get_definition(asi_id)
        if definition is None:
            print(f" -> {asi_id} hop le trong Registry nhung CHUA co Attack Type Framework tuong ung. Chon lai.")
            continue

        return asi_id, definition


def collect_base_fields(asi_id: str) -> dict:
    print(f"\n--- Nhap cac field khung chung cho {asi_id} ---")
    test_id = ask_unique_test_id()
    prerequisites = ask_capability_list(
        "prerequisites (capability tag target phai co de test nay co y nghia):"
    )
    target_surface = ask("target_surface (be mat agent tiep can): ")
    attack_objective = ask("attack_objective (muc tieu ke tan cong): ")
    setup = ask("setup (trang thai/du lieu can dung san truoc khi bom payload): ")
    payload_template = ask("payload_template (noi dung tan cong thuc su dua vao target): ")
    execution_method = ask("execution_method (cach ky thuat dua payload vao target): ")
    expected_evidence = ask("expected_evidence (tong quan loai bang chung can thu thap): ")
    rule = ask("rule (dieu kien may-kiem-duoc de Oracle cham verdict): ")
    success_condition = ask("success_condition (khi nao coi la tan cong thanh cong thuc su): ")
    inconclusive_condition = ask("inconclusive_condition (khi nao khong du du lieu de ket luan): ")

    return {
        "test_id": test_id,
        "prerequisites": prerequisites,
        "target_surface": target_surface,
        "attack_objective": attack_objective,
        "setup": setup,
        "payload_template": payload_template,
        "execution_method": execution_method,
        "expected_evidence": expected_evidence,
        "rule": rule,
        "success_condition": success_condition,
        "inconclusive_condition": inconclusive_condition,
    }


def collect_extension_fields(definition: "framework.AttackTypeDefinition") -> tuple:
    print(f"\n--- Nhap mechanism_fields rieng cho attack_type = {definition.attack_type} ---")
    mechanism = {}
    for field_name, description in definition.mechanism_fields.items():
        mechanism[field_name] = ask(f"[{field_name}]\n  Goi y: {description}\n> ")

    print(f"\n--- Nhap evidence_fields rieng cho attack_type = {definition.attack_type} ---")
    evidence = {}
    for field_name, description in definition.evidence_fields.items():
        evidence[field_name] = ask(f"[{field_name}]\n  Goi y: {description}\n> ")

    return mechanism, evidence


def build_testspec() -> dict:
    asi_id, definition = choose_asi_id()
    base = collect_base_fields(asi_id)
    mechanism, evidence = collect_extension_fields(definition)

    return {
        "test_id": base["test_id"],
        "asi_id": asi_id,
        "taxonomy_version": TAXONOMY_VERSION,
        "capability_version": vocab.CAPABILITY_VERSION,
        "prerequisites": base["prerequisites"],
        "target_surface": base["target_surface"],
        "attack_objective": base["attack_objective"],
        "setup": base["setup"],
        "payload_template": base["payload_template"],
        "execution_method": base["execution_method"],
        "expected_evidence": base["expected_evidence"],
        "rule": base["rule"],
        "success_condition": base["success_condition"],
        "inconclusive_condition": base["inconclusive_condition"],
        "attack_type": definition.attack_type,
        "mechanism": mechanism,
        "evidence": evidence,
    }


def save_testspec(testspec: dict) -> Path:
    OUTPUT_DIR.mkdir(exist_ok=True)
    filename = f"{testspec['test_id']}_{testspec['asi_id']}.json"
    path = OUTPUT_DIR / filename
    path.write_text(json.dumps(testspec, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nDa luu TestSpec vao: {path}")
    return path


def main() -> None:
    print("=== Tao TestSpec moi (ho tro day du ASI01-ASI10) ===")
    testspec = build_testspec()
    save_testspec(testspec)
    seal_record = store.seal(testspec["test_id"])
    print(f"Da seal TestSpec: {seal_record}")


if __name__ == "__main__":
    main()