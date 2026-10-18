from pathlib import Path

import pytest

from afi.scenario import load_scenario, load_scenarios

SCENARIOS = Path(__file__).resolve().parent.parent / "scenarios"


def test_all_shipped_scenarios_validate():
    scenarios = load_scenarios(SCENARIOS)
    assert len(scenarios) >= 4


def test_missing_key_rejected(tmp_path):
    bad = tmp_path / "bad.json"
    bad.write_text('{"id": "x"}')
    with pytest.raises(ValueError):
        load_scenario(bad)


def test_unknown_class_rejected(tmp_path):
    bad = tmp_path / "bad.json"
    bad.write_text(
        '{"id": "x", "class": "nope", "description": "d", "task": "t",'
        ' "environment": {}, "expected_violations": []}')
    with pytest.raises(ValueError):
        load_scenario(bad)
