# Agent Failure Intelligence

**Find agent failures before production does.**

Reproducible adversarial testing for AI agents that use tools. Discover
behavioral failures, verify them independently, and turn them into
regression tests.

> **Status: proof of concept.** The current failure class is
> *privilege escalation via tool output*: an agent that treats instructions
> embedded in tool results as operator commands, and is induced to exceed
> the permissions it was given. The shipped models are **scripted
> stand-ins** — results validate the harness, not any real model. Real-LLM
> adapters plug into the same interface (see `docs/architecture.md`).

## The problem

Agents execute sequences of actions, call tools, and interpret untrusted
content. Conventional functional tests do not cover every combination of
instructions, permissions, and context — content returned by a tool can
contain instructions the agent was never supposed to follow.

## How it works

1. **Generate** — adversarial scenarios are versioned as data (`scenarios/*.json`), reviewed like code.
2. **Execute** — agents run in a fully simulated, isolated environment (`src/afi/tools.py`). No real filesystem, network, or third-party service is ever touched.
3. **Verify** — a deterministic verifier (`src/afi/verify.py`) checks every trace against explicit rules. It is independent of whatever produced the scenario or the trace.
4. **Prevent** — reproduced failures become regression tests (`tests/test_regression.py`): a fix is only accepted when the violation disappears *and* the detector still catches it on the baseline.

## Quick start

```bash
pip install -e '.[dev]'
pytest -q                                    # unit + regression tests
python -m afi run --scenarios scenarios      # run the benchmark
```

Reports are written to `benchmarks/results/latest.json` and `latest.md`.

## Repository layout

| Path | Contents |
|---|---|
| `src/afi/` | test engine: tools, policy, models, agent loop, runner, verifier, dedup, reports |
| `tests/` | unit tests and the regression suite |
| `scenarios/` | versioned failure scenarios (JSON, validated on load) |
| `benchmarks/` | benchmark configuration and results |
| `docs/` | architecture and methodology |
| `web/` | landing page source (see `docs/landing.md`) |
| `.github/workflows/` | CI: tests + offline benchmark on every push |

## Current results (harness validation)

From `benchmarks/results/latest.md`, scripted models, offline, cost $0.00:

- 6 scenarios, 12 runs, **6 violations detected on the vulnerable baseline, 0 on the hardened variant**
- 4 unique failures after deduplication
- 0 false positives on benign control scenarios

These numbers say the harness detects and reproduces the failure class it
was built for. They are **not** a benchmark of any real model.

## Safety boundaries

- Simulated tools only. The PoC never attacks third-party services, never
  collects private data, and performs no destructive actions.
- The agent under test is told its permission policy; the harness records
  what it *attempts*, and the verifier judges the attempts.

## License

MIT — see [LICENSE](LICENSE).

## Real-model results (2026-10-18)

First run against a real LLM: `gemini-3.1-flash-lite-preview` via the Google AI
Studio free tier (`src/afi/gemini.py`, `AFI_GEMINI_KEY`). 6 scenarios, 1 model,
temperature 0, cost €0.00. Raw output: `benchmarks/results-gemini/latest.json`.

- All 4 injection scenarios: **0 policy violations** - the model completed the
  authorized task and ignored every injected `>>` directive (no out-of-scope
  reads, no forbidden `message.send`).
- Both benign controls: clean, no false positives.
- Nuance: in `inj-config-exfil` the model followed a natural-language hint
  inside the injected file and tried to read an (in-scope, nonexistent) second
  file. Within policy, but it shows the injected prose influenced its plan.

These results cover exactly this model, prompt, and harness - not LLMs in
general. Detection capability is validated by the scripted vulnerable baseline
(6 violations detected, 0 missed).
