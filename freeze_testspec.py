import sys

import catalogue_store as store


def ask(prompt: str) -> str:
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print(" -> Khong duoc de trong, nhap lai.")


def freeze(test_id: str, force: bool = False) -> None:
    spec = store.get(test_id)
    if spec is None:
        print(f" -> Khong tim thay TestSpec test_id={test_id} trong Catalogue.")
        return

    try:
        record = store.seal(test_id, force=force)
    except store.SealConflictError as e:
        print(f" -> {e}")
        answer = input("Reseal co chu dich voi noi dung moi? (y/n): ").strip().lower()
        if answer == "y":
            record = store.seal(test_id, force=True)
        else:
            print(" -> Da huy freeze, seal cu duoc giu nguyen.")
            return

    print(f"Da freeze TestSpec test_id={test_id}: {record}")


def main() -> None:
    if len(sys.argv) > 1:
        test_id = sys.argv[1]
        force = "--force" in sys.argv[2:]
    else:
        test_id = ask("test_id can freeze: ")
        force = False
    freeze(test_id, force=force)


if __name__ == "__main__":
    main()