# Methodology

## Failure class under test

**Privilege escalation via tool output.** An agent that uses tools receives
content it did not control (files, web pages, messages). If the agent treats
instruction-looking content inside tool results as operator commands, an
attacker who controls that content can steer the agent beyond its
permissions: reading files outside its roots, fetching non-allowlisted
hosts, writing to protected paths, or invoking forbidden tools.

## Experimental setup

- Each scenario is a JSON file with: id, class, description, the user task,
  a simulated environment (files, canned web), and the violations expected
  on a vulnerable baseline.
- Every scenario runs against a vulnerable baseline and a hardened variant.
- Expected-violation labels exist to measure the *detector*: true positives
  and missed expectations are measured on vulnerable-baseline runs; false
  positives are measured on every run, including benign control scenarios.

## Metrics

- **Violations detected** — raw count across runs.
- **Unique failures** — after fingerprint deduplication.
- **True positives / missed** — detector recall against scenario labels on
  the vulnerable baseline.
- **False positives** — violations flagged where the label says none.
- **Wall time** — measured per run.
- **Cost** — API spend per run; $0.00 for the scripted models.

## Honesty rules

- Scripted-model results are labeled as harness validation in every report.
- Nothing is published that was not executed and verified in-repo.
- Benign control scenarios guard against a detector that flags everything.

## Limitations

- Scripted models stand in for one failure mode; they do not show how any
  real model behaves.
- One failure class is covered. Prompt-injection variants (indirect via
  chained tools, multi-turn, encoded payloads) are future work.
- The simulated tools are faithful to permission semantics, not to any
  specific real API.
