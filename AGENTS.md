# Agent instructions for this repository

This is a **disposable research laboratory**, not a product repository. See
[README.md](README.md) for the full business context and architectural
hypothesis. Read it before doing anything else here.

## Current status

- **Gate 0** (reproducible devcontainer) is done — see
  [reports/BOOTSTRAP_REPORT.md](reports/BOOTSTRAP_REPORT.md).
- **Gate 1** (reference architecture, enterprise evidence, and LENSIPS
  capability selection) is done — see
  [reports/CAPABILITY_PORTFOLIO.md](reports/CAPABILITY_PORTFOLIO.md) for
  the MUST/SHOULD/COULD/WON'T decisions and the recommended next
  experiment, and [reports/LENSIPS_GAP_ANALYSIS.md](reports/LENSIPS_GAP_ANALYSIS.md)
  for the reasoning behind them. No implementation happened in Gate 1 —
  it produced research/evidence artifacts only.

Do not start Gate 2 or later without explicit instruction — see README.md
section 12 for the gate sequence.

## Ground rules for every task in this repo

- Every task should have an explicit scope, inputs, outputs, "do not" list,
  and exit criteria. Stop when the exit criteria are met — do not invent
  follow-on work.
- Reuse proven foundations (PM4Py, OCEL, OFacT, DuckDB, etc.) instead of
  reimplementing process mining, digital twins, or simulation engines.
- Do not fork or modify third-party source (PM4Py, OFacT) — treat them as
  external dependencies.
- Do not introduce Frappe, ERPNext, Kubernetes, Redis, PostgreSQL, n8n,
  production credentials, or production data unless a task explicitly
  requires it.
- Do not fabricate results, version numbers, or benchmark figures. Only
  report what was actually run and verified. If something can't be verified,
  say so explicitly in the relevant report.
- All experimentation happens inside the devcontainer (`.devcontainer/`), not
  on the host machine.

See README.md's "Repository layout" section for what each top-level
directory is for.
