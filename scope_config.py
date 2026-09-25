import json
from dataclasses import dataclass
from pathlib import Path
from typing import Tuple


@dataclass(frozen=True)
class TestingWindow:
    start: str
    end: str


@dataclass(frozen=True)
class ScopeConfig:
    campaign_id: str
    target_ref: str
    authorized_asi: Tuple[str, ...]
    capability_ceiling: Tuple[str, ...]
    testing_window: TestingWindow
    prohibited_actions: Tuple[str, ...]
    stop_conditions: Tuple[str, ...]
    authorization_statement: str


def load(path: Path) -> ScopeConfig:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    testing_window = TestingWindow(
        start=data["testing_window"]["start"],
        end=data["testing_window"]["end"],
    )

    return ScopeConfig(
        campaign_id=data["campaign_id"],
        target_ref=data["target_ref"],
        authorized_asi=tuple(data["authorized_asi"]),
        capability_ceiling=tuple(data["capability_ceiling"]),
        testing_window=testing_window,
        prohibited_actions=tuple(data["prohibited_actions"]),
        stop_conditions=tuple(data["stop_conditions"]),
        authorization_statement=data["authorization_statement"],
    )


def save(scope: ScopeConfig, path: Path) -> Path:
    data = {
        "campaign_id": scope.campaign_id,
        "target_ref": scope.target_ref,
        "authorized_asi": list(scope.authorized_asi),
        "capability_ceiling": list(scope.capability_ceiling),
        "testing_window": {
            "start": scope.testing_window.start,
            "end": scope.testing_window.end,
        },
        "prohibited_actions": list(scope.prohibited_actions),
        "stop_conditions": list(scope.stop_conditions),
        "authorization_statement": scope.authorization_statement,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return path