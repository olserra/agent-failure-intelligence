"""Versioned failure scenarios. Scenarios are data (JSON), reviewed like code,
and loaded through a strict validator so a malformed file fails loudly."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

REQUIRED_KEYS = {"id", "class", "description", "task", "environment", "expected_violations"}
ENV_KEYS = {"files", "web"}
CLASSES = {"privilege-escalation-via-tool-output"}


@dataclass
class Scenario:
    id: str
    cls: str
    description: str
    task: str
    files: dict[str, str] = field(default_factory=dict)
    web: dict[str, str] = field(default_factory=dict)
    expected_violations: list[str] = field(default_factory=list)  # rule ids


def load_scenario(path: str | Path) -> Scenario:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    missing = REQUIRED_KEYS - data.keys()
    if missing:
        raise ValueError(f"{path}: missing keys {sorted(missing)}")
    if data["class"] not in CLASSES:
        raise ValueError(f"{path}: unknown class {data['class']!r}; known: {sorted(CLASSES)}")
    env = data["environment"]
    unknown_env = set(env) - ENV_KEYS
    if unknown_env:
        raise ValueError(f"{path}: unknown environment keys {sorted(unknown_env)}")
    if not isinstance(data["expected_violations"], list):
        raise ValueError(f"{path}: expected_violations must be a list of rule ids")
    return Scenario(
        id=data["id"], cls=data["class"], description=data["description"],
        task=data["task"], files=env.get("files", {}), web=env.get("web", {}),
        expected_violations=list(data["expected_violations"]))


def load_scenarios(directory: str | Path) -> list[Scenario]:
    paths = sorted(Path(directory).glob("*.json"))
    if not paths:
        raise FileNotFoundError(f"no scenario JSON files in {directory}")
    return [load_scenario(p) for p in paths]
