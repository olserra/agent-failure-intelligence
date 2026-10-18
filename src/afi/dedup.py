"""Deduplicate violations into unique failures by fingerprint."""
from __future__ import annotations

import hashlib
from dataclasses import dataclass

from .verify import Violation


@dataclass(frozen=True)
class Failure:
    fingerprint: str
    rule_id: str
    tool: str
    target: str
    first_scenario: str
    occurrences: int


def fingerprint(violation: Violation) -> str:
    raw = f"{violation.rule_id}|{violation.tool}|{violation.target}"
    return hashlib.sha256(raw.encode()).hexdigest()[:12]


def deduplicate(items: list[tuple[str, Violation]]) -> list[Failure]:
    """items: (scenario_id, violation) pairs, in run order."""
    seen: dict[str, Failure] = {}
    order: list[str] = []
    for scenario_id, v in items:
        fp = fingerprint(v)
        if fp in seen:
            prev = seen[fp]
            seen[fp] = Failure(fp, v.rule_id, v.tool, v.target,
                               prev.first_scenario, prev.occurrences + 1)
        else:
            seen[fp] = Failure(fp, v.rule_id, v.tool, v.target, scenario_id, 1)
            order.append(fp)
    return [seen[fp] for fp in order]
