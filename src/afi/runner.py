"""Execute scenarios against one or more models and collect traces + verdicts."""
from __future__ import annotations

from dataclasses import dataclass, field

from .agent import run_agent, Trace
from .dedup import deduplicate, Failure
from .models import Model
from .policy import Policy
from .scenario import Scenario
from .tools import SimEnvironment, Toolset
from .verify import verify, Violation


@dataclass
class ScenarioResult:
    scenario: Scenario
    model: str
    trace: Trace
    violations: list[Violation]
    true_positives: list[str] = field(default_factory=list)
    false_positives: list[str] = field(default_factory=list)
    missed: list[str] = field(default_factory=list)  # expected but not detected


def run_scenario(scenario: Scenario, model: Model, policy: Policy) -> ScenarioResult:
    model.reset()
    env = SimEnvironment(files=dict(scenario.files), web=dict(scenario.web))
    trace = run_agent(model, Toolset(env), scenario.id, scenario.task, policy.describe())
    violations = verify(trace, policy)
    found = {v.rule_id for v in violations}
    expected = set(scenario.expected_violations)
    return ScenarioResult(
        scenario=scenario, model=model.name, trace=trace, violations=violations,
        true_positives=sorted(found & expected),
        false_positives=sorted(found - expected),
        missed=sorted(expected - found))


def model_role(models: list[Model], name: str) -> str:
    return next((m.role for m in models if m.name == name), "subject")


def run_benchmark(scenarios: list[Scenario], models: list[Model], policy: Policy) -> dict:
    results = [run_scenario(s, m, policy) for s in scenarios for m in models]
    pairs = [(r.scenario.id, v) for r in results for v in r.violations]
    failures: list[Failure] = deduplicate(pairs)
    return {
        "results": results,
        "unique_failures": failures,
        "metrics": {
            "note": "true positives and missed expectations are measured on vulnerable-baseline runs; false positives on all runs",
            "scenarios": len(scenarios),
            "scenario_classes": sorted({s.cls for s in scenarios}),
            "models": [m.name for m in models],
            "runs": len(results),
            "violations_detected": len(pairs),
            "unique_failures": len(failures),
            "true_positives": sum(len(r.true_positives) for r in results
                                  if model_role(models, r.model) == "vulnerable-baseline"),
            "false_positives": sum(len(r.false_positives) for r in results),
            "missed_expected": sum(len(r.missed) for r in results
                                   if model_role(models, r.model) == "vulnerable-baseline"),
            "total_wall_time_ms": round(sum(r.trace.wall_time_ms for r in results), 2),
            "model_api_cost_usd": 0.0,
        },
    }
