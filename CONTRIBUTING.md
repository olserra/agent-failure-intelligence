# Contributing

Thanks for your interest. The project is at proof-of-concept stage; the most
useful contributions right now are:

1. **New scenarios** in the covered failure class — add a JSON file under
   `scenarios/` and make sure `pytest` passes. Scenarios are data and are
   reviewed like code: the injection vector, the environment, and the
   expected violations must all be explicit.
2. **Verifier rules** — new rules must be deterministic and independent of
   any model output.
3. **Model adapters** — see `docs/architecture.md` for the `Model`
   interface. Adapters that call paid APIs must default to off and must
   never be exercised by CI.

## Ground rules

- No scenarios that target real third-party services, real credentials, or
  real personal data. Everything runs against the simulated environment.
- No benchmark claims without reproduced, committed results.
- Keep generation and verification separate: whatever produces a scenario
  must not be the thing that judges it.

## Setup

```bash
pip install -e '.[dev]'
pytest -q
python -m afi run --scenarios scenarios
```
