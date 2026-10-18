"""JSON and Markdown reports. Every report states which models produced it,
so scripted-model results are never mistaken for real-model benchmarks."""
from __future__ import annotations

import json
from datetime import datetime, timezone


def to_json(bench: dict, git_sha: str = "unknown") -> str:
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "git_sha": git_sha,
        "models": bench["metrics"]["models"],
        "model_kind": "scripted (harness validation, not a real-model benchmark)",
        "metrics": bench["metrics"],
        "unique_failures": [f.__dict__ for f in bench["unique_failures"]],
        "runs": [
            {
                "scenario_id": r.scenario.id,
                "model": r.model,
                "violations": [v.__dict__ for v in r.violations],
                "true_positives": r.true_positives,
                "false_positives": r.false_positives,
                "missed": r.missed,
                "trace": r.trace.to_dict(),
            }
            for r in bench["results"]
        ],
    }
    return json.dumps(payload, indent=2)


def to_markdown(bench: dict, git_sha: str = "unknown") -> str:
    m = bench["metrics"]
    lines = [
        "# Agent Failure Intelligence - benchmark report",
        "",
        f"- Generated: {datetime.now(timezone.utc).isoformat()}",
        f"- Commit: `{git_sha}`",
        f"- Models: {', '.join(m['models'])} (**scripted** - harness validation, not a real-model benchmark)",
        "",
        "## Metrics",
        "",
        f"- Scenarios: {m['scenarios']} ({', '.join(m['scenario_classes'])})",
        f"- Runs: {m['runs']}",
        f"- Violations detected: {m['violations_detected']}",
        f"- Unique failures after dedup: {m['unique_failures']}",
        f"- True positives: {m['true_positives']} | False positives: {m['false_positives']} | Missed expected: {m['missed_expected']}",
        f"- Wall time: {m['total_wall_time_ms']} ms | Model API cost: ${m['model_api_cost_usd']:.2f}",
        "",
        "## Unique failures",
        "",
        "| Fingerprint | Rule | Tool | Target | First scenario | Occurrences |",
        "|---|---|---|---|---|---|",
    ]
    for f in bench["unique_failures"]:
        lines.append(f"| {f.fingerprint} | {f.rule_id} | {f.tool} | `{f.target}` | {f.first_scenario} | {f.occurrences} |")
    lines += ["", "## Per-run detail", ""]
    for r in bench["results"]:
        status = "violations: " + ", ".join(v.rule_id for v in r.violations) if r.violations else "clean"
        lines.append(f"- `{r.scenario.id}` on `{r.model}`: {status}")
    lines.append("")
    return "\n".join(lines)
