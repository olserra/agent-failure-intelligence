"""CLI: python -m afi run --scenarios scenarios/ --models naive-scripted,hardened-scripted --out benchmarks/results"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from .models import MODELS
from .policy import Policy
from .report import to_json, to_markdown
from .runner import run_benchmark
from .scenario import load_scenarios


def _git_sha() -> str:
    try:
        return subprocess.run(["git", "rev-parse", "--short", "HEAD"],
                              capture_output=True, text=True, check=True).stdout.strip()
    except Exception:
        return "unknown"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="afi")
    sub = parser.add_subparsers(dest="command", required=True)
    run = sub.add_parser("run", help="run the scenario benchmark")
    run.add_argument("--scenarios", default="scenarios")
    run.add_argument("--models", default=",".join(MODELS))
    run.add_argument("--out", default="benchmarks/results")
    args = parser.parse_args(argv)

    if args.command == "run":
        scenarios = load_scenarios(args.scenarios)
        names = [n.strip() for n in args.models.split(",") if n.strip()]
        unknown = [n for n in names if n not in MODELS]
        if unknown:
            print(f"unknown models: {unknown}; available: {sorted(MODELS)}", file=sys.stderr)
            return 2
        models = [MODELS[n]() for n in names]
        bench = run_benchmark(scenarios, models, Policy())
        sha = _git_sha()
        out = Path(args.out)
        out.mkdir(parents=True, exist_ok=True)
        (out / "latest.json").write_text(to_json(bench, sha), encoding="utf-8")
        (out / "latest.md").write_text(to_markdown(bench, sha), encoding="utf-8")
        print(to_markdown(bench, sha))
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
