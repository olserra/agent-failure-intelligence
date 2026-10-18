"""Regression suite: every scenario runs against the vulnerable baseline and
the hardened variant. A fix is only accepted when the previously reproduced
violation disappears on the hardened model while detection on the baseline
still works (so we know the detector did not go blind)."""
from pathlib import Path

import pytest

from afi.models import MODELS
from afi.policy import Policy
from afi.runner import run_scenario
from afi.scenario import load_scenarios

SCENARIOS = load_scenarios(Path(__file__).resolve().parent.parent / "scenarios")
POLICY = Policy()


@pytest.mark.parametrize("scenario", SCENARIOS, ids=lambda s: s.id)
def test_baseline_violations_match_labels(scenario):
    """Detector finds exactly the labeled violations on the naive baseline."""
    result = run_scenario(scenario, MODELS["naive-scripted"](), POLICY)
    found = {v.rule_id for v in result.violations}
    assert found == set(scenario.expected_violations)
    assert result.false_positives == []
    assert result.missed == []


@pytest.mark.parametrize("scenario", SCENARIOS, ids=lambda s: s.id)
def test_hardened_model_has_no_violations(scenario):
    """The fix holds: hardened model stays inside the policy everywhere."""
    result = run_scenario(scenario, MODELS["hardened-scripted"](), POLICY)
    assert result.violations == []
