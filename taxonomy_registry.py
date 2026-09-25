"""
Taxonomy Registry - OWASP Top 10 for Agentic Applications (ASI01-ASI10)
Nguon: OWASP Top 10 for Agentic Applications 2026
       (OWASP GenAI Security Project - Agentic Security Initiative, Version 2026)
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class TaxonomyStatus(Enum):
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    SUPERSEDED = "superseded"


@dataclass(frozen=True)
class TaxonomyEntry:
    asi_id: str
    title: str
    taxonomy_version: str
    status: TaxonomyStatus


_REGISTRY: tuple[TaxonomyEntry, ...] = (
    TaxonomyEntry("ASI01", "Agent Goal Hijack", "2026", TaxonomyStatus.ACTIVE),
    TaxonomyEntry("ASI02", "Tool Misuse and Exploitation", "2026", TaxonomyStatus.ACTIVE),
    TaxonomyEntry("ASI03", "Identity and Privilege Abuse", "2026", TaxonomyStatus.ACTIVE),
    TaxonomyEntry("ASI04", "Agentic Supply Chain Vulnerabilities", "2026", TaxonomyStatus.ACTIVE),
    TaxonomyEntry("ASI05", "Unexpected Code Execution (RCE)", "2026", TaxonomyStatus.ACTIVE),
    TaxonomyEntry("ASI06", "Memory and Context Poisoning", "2026", TaxonomyStatus.ACTIVE),
    TaxonomyEntry("ASI07", "Insecure Inter-Agent Communication", "2026", TaxonomyStatus.ACTIVE),
    TaxonomyEntry("ASI08", "Cascading Failures", "2026", TaxonomyStatus.ACTIVE),
    TaxonomyEntry("ASI09", "Human-Agent Trust Exploitation", "2026", TaxonomyStatus.ACTIVE),
    TaxonomyEntry("ASI10", "Rogue Agents", "2026", TaxonomyStatus.ACTIVE),
)


_INDEX: dict[tuple[str, str], TaxonomyEntry] = {
    (e.asi_id, e.taxonomy_version): e for e in _REGISTRY
}


def lookup(asi_id: str, taxonomy_version: str) -> Optional[TaxonomyEntry]:
    return _INDEX.get((asi_id.upper(), taxonomy_version))


def list_all(taxonomy_version: str) -> tuple[TaxonomyEntry, ...]:
    return tuple(e for e in _REGISTRY if e.taxonomy_version == taxonomy_version)


def is_valid(asi_id: str, taxonomy_version: str) -> bool:
    entry = lookup(asi_id, taxonomy_version)
    return entry is not None and entry.status is TaxonomyStatus.ACTIVE


if __name__ == "__main__":
    all_entries = list_all("2026")
    print(f"Tong so ma ASI da nap: {len(all_entries)}")
    for entry in all_entries:
        print(f"{entry.asi_id} - {entry.title} - {entry.status.value}")

    print()
    print("Lookup ASI06:", lookup("ASI06", "2026"))
    print("Lookup ASI99 (khong ton tai):", lookup("ASI99", "2026"))
    print("is_valid ASI02:", is_valid("ASI02", "2026"))