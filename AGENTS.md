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
  the MUST/SHOULD/COULD/WON'T decisions, its "Corrected LENSIPS
  Positioning" section (LENSIPS is not assumed to be the customer's ERP),
  and the recommended next experiment. No implementation happened in
  Gate 1 — it produced research/evidence artifacts only.
- **Gate 2** (data realism experiment) is done — see
  [reports/GATE2_DATA_REALISM_EXPERIMENT.md](reports/GATE2_DATA_REALISM_EXPERIMENT.md).
  Ran PM4Py discovery/conformance/performance analysis against a real
  manufacturing event log under synthetic data-degradation scenarios; the
  key finding is that conformance/fitness scores are not a usable proxy
  for data completeness, and that a category-level coverage check (e.g.
  "were quality-inspection events observed at all?") is needed to catch
  findings that silently vanish under realistic data gaps. Reproducible
  script: [experiments/gate2_data_realism/run_experiment.py](experiments/gate2_data_realism/run_experiment.py).
- **Gate 3** (evidence-grounded factory finding) is done — see
  [reports/GATE3_EVIDENCE_GROUNDED_FINDINGS.md](reports/GATE3_EVIDENCE_GROUNDED_FINDINGS.md).
  Defined 3 concrete factory questions (bottleneck, quality/rework issue,
  abnormal step performance), ran Gate 2's category-coverage mechanism
  against the Gate 2 degraded datasets to gate each question's confidence
  status, and confirmed the system withholds a finding (quality/rework,
  abnormal step) in the `missing_quality_events` scenario even though the
  bottleneck finding on the same dataset still runs and reports high
  confidence. Reproducible script:
  [experiments/gate3_evidence_grounded_findings/run_experiment.py](experiments/gate3_evidence_grounded_findings/run_experiment.py).
- **Gate 4, first attempt** (multi-object manufacturing intelligence
  reconnaissance on the Gate 2/3 machine-shop dataset) is superseded — see
  [reports/GATE4_MULTI_OBJECT_RECONNAISSANCE.md](reports/GATE4_MULTI_OBJECT_RECONNAISSANCE.md)
  for the historical record (not edited). That dataset was judged too
  case-centric (no real material/supplier/quality object) to properly
  test the object-centric hypothesis, so Gate 4 was restarted on a
  different, genuinely multi-object dataset rather than patched.
- **Gate 4, restart ("Gate 4b")** is done — see
  [reports/GATE1_TO_GATE4_RESEARCH_SUMMARY.md](reports/GATE1_TO_GATE4_RESEARCH_SUMMARY.md)
  (primary document) and
  [reports/GATE4_DATASET_SELECTION.md](reports/GATE4_DATASET_SELECTION.md)
  (dataset provenance/sampling). Dataset: a real-data subsample of the BPI
  Challenge 2019 OCEL log (a real coatings/paints manufacturer's
  purchase-to-pay process; PO/POItem/Vendor/Resource object types), loaded
  and analysed as a genuine OCEL with PM4Py (`discover_ocdfg`,
  `discover_objects_graph`, inductive-miner discovery, token-based-replay
  fitness). Re-ran Gate 1's capability classification, Gate 2's
  evidence-degradation test, and Gate 3's evidence-grounded-finding
  mechanism against this new dataset (all reconfirmed), then ran a proper
  object-centric vs case-centric comparison. Key finding: 1,002 of 1,011
  sampled purchase orders (99.1%) sit in one connected component of the
  object-interaction graph, reachable only through shared vendors/
  resources — a genuinely OCEL-required finding (graph connectivity, not
  a group-by) that the case-centric flattened view cannot represent.
  Roughly half of the other object-centric analyses attempted were
  honestly reclassified as "ordinary relational analytics" once OCEL was
  hypothetically removed (see the report's "What PM4Py and OCEL Actually
  Contributed" section). No OCEL framework, digital twin, LLM agent, or
  transformer ontology was built. Reproducible scripts:
  [experiments/gate4b_object_centric_research/run_experiment.py](experiments/gate4b_object_centric_research/run_experiment.py),
  [experiments/gate4b_object_centric_research/scripts/build_sample.py](experiments/gate4b_object_centric_research/scripts/build_sample.py).

Do not start Gate 5 or later without explicit instruction — see README.md
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
