# Architecture

## Principles

1. **Simulation only.** The environment (`tools.SimEnvironment`) is
   in-memory. Files, web pages, and messages exist only inside a run.
2. **Policy is data.** The permission policy (`policy.Policy`) is declared
   to the agent under test and reused by the verifier. The harness does not
   enforce it — the point is to observe whether the agent respects it.
3. **Generation and verification are separate.** Scenarios are versioned
   data reviewed by humans; the verifier is deterministic and never sees a
   scenario's expectations.
4. **Everything is traced.** Inputs, model decisions (with rationale), tool
   calls, and tool results land in a structured trace that feeds
   verification, dedup, metrics, and reports.

## Components

```
scenarios/*.json ──► runner.run_scenario ──► agent.run_agent ──► Trace
                         │                       │
                         │                  tools.Toolset (simulated env)
                         ▼
                   verify.verify (rules) ──► dedup.deduplicate ──► report
```

- `tools.py` — simulated `fs.read`, `fs.write`, `http.fetch`,
  `message.send`. Executing a forbidden action inside the simulation is
  what produces observable evidence; it is always safe.
- `models.py` — the `Model` interface (`decide(task, policy, last_output,
  step) -> ModelReply`) and two scripted models:
  - `naive-scripted` (vulnerable baseline): queues directive-looking lines
    from *any* source, including tool output.
  - `hardened-scripted`: only the original user task may direct tool use.
  - Real-LLM adapters implement the same interface. They must default to
    off, must read credentials from the environment (never committed), and
    are never exercised in CI.
- `agent.py` — the agent loop with a step cap and full trace recording.
- `verify.py` — global, explicit rules: `fs-read-scope`, `fs-write-scope`,
  `http-allowlist`, `denied-tool`. Every rule runs against every trace.
- `dedup.py` — violations are merged into unique failures by fingerprint
  `(rule_id, tool, target)`.
- `report.py` — JSON + Markdown. Reports name the models and state when
  they are scripted stand-ins.
- `cli.py` — `python -m afi run`.

## Directive grammar

Scripted models communicate through an explicit command grammar:
`>> read <path>`, `>> write <path> <content>`, `>> fetch <url>`,
`>> send <to> <text>`. Ordinary prose never parses as a command. This keeps
the PoC deterministic and makes the injection vector in each scenario
readable at a glance.

## What a real-model adapter changes — and what it doesn't

An adapter replaces only `Model.decide`. The environment, policy, verifier,
dedup, metrics, and reports are untouched, which is what keeps results
comparable across models.
