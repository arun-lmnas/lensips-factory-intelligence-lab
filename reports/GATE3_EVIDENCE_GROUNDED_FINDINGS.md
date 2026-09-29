# Gate 3 — Evidence-Grounded Factory Finding

Scope: test whether, for a specific factory question, a system can (a)
name the evidence that question requires, (b) measure whether that
evidence is present in a given dataset, and (c) withhold or qualify a
finding when the evidence is insufficient — even when the underlying
process-mining computation (PM4Py discovery, or a plain pandas aggregate)
runs without error and "produces a result." This is an evidence-gating
experiment, not a new analysis engine. No LLM layer, no OCEL model, no
digital twin, no ERP connector, and no new process-mining algorithm were
built — those remain out of scope per the Gate 3 brief. Gate 4 was not
started.

Reproducible artifacts:
[experiments/gate3_evidence_grounded_findings/run_experiment.py](../experiments/gate3_evidence_grounded_findings/run_experiment.py),
raw results in
[experiments/gate3_evidence_grounded_findings/results/results.json](../experiments/gate3_evidence_grounded_findings/results/results.json).
Reuses, unmodified, the seven degradation scenarios and data-loading/
performance-metric code from
[experiments/gate2_data_realism/run_experiment.py](../experiments/gate2_data_realism/run_experiment.py),
and the category-coverage mechanism validated in
[experiments/gate2_data_realism/coverage_check_experiment.py](../experiments/gate2_data_realism/coverage_check_experiment.py).

Run inside the Gate 0 devcontainer, same as Gate 2:

```bash
docker build -t lensips-gate0:test -f .devcontainer/Dockerfile .
docker run --rm --init -v "$PWD":/workspace -w /workspace \
  lensips-gate0:test python3 experiments/gate3_evidence_grounded_findings/run_experiment.py
```

## 1. The three factory questions

Chosen to match the examples in the Gate 3 brief and to exercise three
different evidence dependencies against the same seven Gate 2 scenarios
(baseline + 6 degradations, on the same 4TU machine-shop event log used in
Gate 2):

1. **What is the bottleneck (activity and resource)?** — evidence
   required: sufficient event coverage of *whichever specific
   activity/resource ends up ranked #1* by total recorded duration (not
   overall dataset completeness — Gate 2 Finding 1 showed overall
   completeness/fitness does not detect a single category vanishing).
2. **Is quality/rework a significant issue in this process?** — evidence
   required: coverage of quality-inspection activity events
   (Q.C./Inspection/MRB in the activity label, the same category Gate 2
   Finding 2 showed can silently disappear), rework-flag events, and
   rejected-quantity events.
3. **Is a specific process step ('Final Inspection Q.C.') showing
   abnormal performance (duration)?** — evidence required: enough
   surviving events for that one activity to trust a mean-duration
   comparison against the baseline (a minimum-sample-size gate, not just
   a percentage-coverage gate).

## 2. Method

For each of the 7 Gate 2 scenarios, compute all three findings using only
metrics Gate 2 already computes (`compute_performance`) plus one new,
thin coverage-and-gating layer:

- **Evidence coverage** per question: expected count (baseline) vs.
  observed count (this scenario) for the specific category/activity/
  resource the finding depends on, classified `OK` (≥70%), `PARTIAL`
  (20–70%), `SEVERELY_DEGRADED` (<20%, reusing Gate 2's own threshold), or
  `MISSING` (0%). These thresholds are illustrative, not evidence-derived
  (Gate 2 §9 made the same caveat about its 20% threshold).
- **Logical-consistency check**: reuses `n_negative_duration_events` from
  Gate 2's `compute_performance`. Per Gate 2 Finding 3, this is treated as
  a distinct, higher-severity signal, not folded into the coverage
  percentage — any negative-duration events detected caps confidence at
  `LOW` regardless of how much data survived.
- **Confidence/reliability status**, in priority order: `MISSING` evidence
  → `WITHHELD` (finding is not asserted); else negative-duration events
  present → `LOW`; else `SEVERELY_DEGRADED` evidence → `LOW`; else
  `PARTIAL` → `MEDIUM`; else `HIGH`.

Each finding's output object contains exactly the fields the Gate 3 brief
asked for: `finding`, `supporting_evidence`, `evidence_coverage`,
`missing_evidence`, `logical_inconsistencies`, `confidence_status`,
`limitations`.

## 3. Results summary

| Scenario | Bottleneck | Quality/rework | Abnormal step |
|---|---|---|---|
| baseline | HIGH | HIGH | HIGH |
| milestone_only | LOW | LOW | LOW |
| missing_timestamps_30pct | HIGH | HIGH | MEDIUM |
| missing_resource_40pct | MEDIUM | HIGH | HIGH |
| incomplete_relationships_30pct | HIGH | HIGH | HIGH |
| inconsistent_records_10pct | LOW | LOW | LOW |
| missing_quality_events | HIGH | **WITHHELD** | **WITHHELD** |

Full per-scenario finding objects (all 7 × 3 = 21) are in
[results.json](../experiments/gate3_evidence_grounded_findings/results/results.json).

### The demonstration the brief asked for: two withheld findings, one still-confident finding, same dataset

In `missing_quality_events` (every Q.C./Inspection/MRB-labeled event
dropped — a directly plausible real-world condition: a QMS not connected
to the systems LENSIPS can reach), the **bottleneck** finding stays
`HIGH` confidence (100% coverage of the new #1 candidate,
`Turning & Milling - Machine 4`/`Machine 4 - Turning & Milling` — PM4Py
discovery and the underlying aggregate both ran and produced a clean-
looking answer) while the **quality/rework** and **abnormal-step**
findings are both `WITHHELD`:

```json
"quality_rework": {
  "finding": "Cannot determine whether quality/rework is a significant
    issue in this process: one or more quality-related evidence
    categories have zero observed events, even though other
    process-mining outputs (discovery, conformance) still run and
    produce a result.",
  "evidence_coverage": {
    "quality_inspection_events": {"expected_count": 1194,
      "observed_count": 0, "coverage_pct": 0.0, "flag": "MISSING"},
    "rejected_qty_events": {"expected_count": 231,
      "observed_count": 18, "coverage_pct": 7.8,
      "flag": "SEVERELY_DEGRADED"}
  },
  "confidence_status": "WITHHELD"
}
```

```json
"abnormal_step": {
  "finding": "Cannot determine whether 'Final Inspection Q.C.' shows
    abnormal performance: insufficient surviving evidence for this
    specific activity in this dataset.",
  "evidence_coverage": {"activity:Final Inspection Q.C.":
    {"expected_count": 550, "observed_count": 0,
     "coverage_pct": 0.0, "flag": "MISSING"}},
  "confidence_status": "WITHHELD"
}
```

This is the concrete case required by the brief: PM4Py's discovery and
the bottleneck aggregate could technically still be computed and looked
unremarkable on this scenario, but the two findings that specifically
depend on quality/inspection evidence were withheld because that evidence
category measured zero observed events — exactly the Gate 2 Finding 2
failure mode (a real finding silently vanishing with no warning), now
caught and surfaced instead of silently omitted.

### A second, distinct demonstration: over-coverage does not mean high confidence

In `inconsistent_records_10pct` (duplicated events + swapped-timestamp
corruption), coverage for every category was **at or above 100%**
(e.g. `quality_inspection_events` 109.9%, `Turning & Milling - Machine 5`
112.0%) — a naive coverage-only check would have reported these as fully
supported, `OK` findings. All three were instead downgraded to `LOW`
because the run also detected 149 negative-duration events (swapped
Start/Complete timestamps). This confirms Gate 2 Finding 3's prediction in
a new setting: a system that gates confidence on coverage percentage alone
would be fooled by inflated, duplicated data; a system that also checks
logical consistency is not.

### Coverage-driven confidence tracks the actual evidence, scenario by scenario

`milestone_only` (90.2% of all events dropped) drove all three findings to
`LOW` — including the bottleneck finding, even though the *point estimate*
(top-1 activity/resource name) happened to still be correct, as Gate 2
Finding 4 already showed. This is the intended behavior: correctness of
the point estimate and strength of its evidence are different questions,
and this experiment's confidence status tracks the latter, not the
former. `missing_timestamps_30pct` and `missing_resource_40pct` showed
mixed results (some questions `HIGH`, others `MEDIUM`) because the two
scenarios degrade different fields (timestamps vs. resource identity),
which affects each question's specific evidence dependency differently —
exactly the "per-finding coverage, not overall completeness" principle
Gate 2 §6 identified as necessary.

## 4. What is demonstrated vs. assumed

**Demonstrated:**

- A category-coverage check, gating a specific named finding rather than
  reporting generic dataset completeness, can and does cause a system to
  withhold a specific finding while other findings on the same dataset
  remain confidently reported — including in the "quality-inspection
  events removed" scenario Gate 2 identified as the concrete failure this
  layer needs to catch.
- Gating on logical inconsistency (negative-duration events) as a signal
  distinct from and prioritized over coverage percentage correctly
  downgrades a scenario (`inconsistent_records_10pct`) that coverage
  percentage alone would have rated as fully supported.
- The same mechanism, unmodified from Gate 2's `coverage_check_experiment.py`
  design, generalizes from category-level checks (quality_inspection) to
  single-activity checks (a specific named bottleneck candidate, a single
  target step) without new algorithmic machinery — it is a comparison of
  two counts and a threshold, applied wherever a finding depends on a
  named subset of the evidence.

**Assumed / not demonstrated:**

- The specific thresholds (20% severely-degraded, 70% partial/OK boundary,
  20-event minimum sample size, 1.5x abnormality ratio) are illustrative
  choices for this experiment, exactly as Gate 2 flagged its own 20%
  threshold to be — none are derived from a statistical power analysis, a
  real customer's tolerance for uncertainty, or domain evidence about what
  threshold matters for a real manufacturing decision.
- The confidence-status priority order (missing > inconsistency >
  severity > partial) is a design choice this experiment tested for
  internal consistency (it produced the expected withhold/downgrade
  behavior on the scenarios built to test it), not a validated model of
  how much each factor should matter relative to the others.
- "Bottleneck" is still proxied by total recorded activity duration, not
  queueing/waiting time or true utilization rate — the same simplification
  Gate 2 §7 flagged as out of scope, carried forward unchanged here.
- Category/activity definitions (which activity-name substrings count as
  "quality," which single activity stands in for "a process step") are
  hand-picked for this dataset, the same limitation Gate 2 §9 already
  noted for its own category list.
- This is still a single dataset from a single industry (the 4TU machine
  shop log), not a transformer manufacturer's data, per the standing
  limitation carried from Gate 2.
- The withholding behavior was demonstrated on synthetic, programmatic
  degradation scenarios with a fixed random seed, not on data gaps
  observed in a real customer's systems.

## 5. Smallest next experiment

The most consequential open question this gate leaves is the confidence-
status priority order and thresholds themselves: right now, "coverage
< 20%" and "any negative-duration event" both force the same `LOW`/
`WITHHELD` outcome, with no way to distinguish "somewhat thin evidence"
from "almost no evidence" or "one corrupted record" from "a systemically
corrupted dataset." The smallest next experiment is:

> Take the 21 finding objects already produced in this gate's
> `results.json` and check whether a human reviewer, shown only the
> `evidence_coverage` / `logical_inconsistencies` fields (not the
> `confidence_status` label), would independently sort them into the same
> four buckets this script assigned — a lightweight validation of whether
> the *thresholds*, not just the *mechanism*, match human judgment about
> when a finding is trustworthy enough to act on.

This requires no new dataset, no new degradation scenario, and no new
process-mining or coverage code — it only requires human review of
artifacts this gate already produced, and it directly targets the
"assumed, not demonstrated" thresholds flagged in §4, rather than
speculatively expanding scope. Per the Gate 3 brief and README.md §12,
Gate 4 (applying this approach to manufacturing event/object data) was
not started.

## 6. Follow-up: validation of evidence thresholds against independent judgment (completed)

The experiment proposed in §5 was carried out. Script:
[experiments/gate3_evidence_grounded_findings/blind_review.py](../experiments/gate3_evidence_grounded_findings/blind_review.py)
(strips `confidence_status` from each of the 21 finding objects). Full
comparison: [experiments/gate3_evidence_grounded_findings/results/human_validation.json](../experiments/gate3_evidence_grounded_findings/results/human_validation.json).

**Important limitation on this follow-up, stated explicitly per this
lab's own "do not fabricate results" rule:** there was no separate human
reviewer available in this session. The "reviewer" role was carried out
by the agent itself, reading only the blinded fields (`question`,
`supporting_evidence`, `evidence_coverage`, `missing_evidence`,
`logical_inconsistencies`, `limitations`) with `confidence_status`
programmatically hidden beforehand, and applying general reasoning about
what a finding's evidence supports rather than the algorithm's exact
threshold values. This is a **self-consistency check on the mechanism's
reasoning**, not the independent human-judgment validation the Gate 3
report's §5 proposal actually called for. A real human reviewer (ideally
someone without knowledge of this script's threshold constants) is still
needed before treating these thresholds as validated.

### Result: 20 of 21 findings agreed (95.2%)

| Scenario | Question | Blind judgment | Algorithm | Agree? |
|---|---|---|---|---|
| baseline | bottleneck / quality_rework / abnormal_step | HIGH / HIGH / HIGH | HIGH / HIGH / HIGH | Yes / Yes / Yes |
| milestone_only | bottleneck / quality_rework / abnormal_step | LOW / LOW / LOW | LOW / LOW / LOW | Yes / Yes / Yes |
| missing_timestamps_30pct | bottleneck / quality_rework / abnormal_step | HIGH / HIGH / **HIGH** | HIGH / HIGH / **MEDIUM** | Yes / Yes / **No** |
| missing_resource_40pct | bottleneck / quality_rework / abnormal_step | MEDIUM / HIGH / HIGH | MEDIUM / HIGH / HIGH | Yes / Yes / Yes |
| incomplete_relationships_30pct | bottleneck / quality_rework / abnormal_step | HIGH / HIGH / HIGH | HIGH / HIGH / HIGH | Yes / Yes / Yes |
| inconsistent_records_10pct | bottleneck / quality_rework / abnormal_step | LOW / LOW / LOW | LOW / LOW / LOW | Yes / Yes / Yes |
| missing_quality_events | bottleneck / quality_rework / abnormal_step | HIGH / WITHHELD / WITHHELD | HIGH / WITHHELD / WITHHELD | Yes / Yes / Yes |

The single disagreement: **`missing_timestamps_30pct` / abnormal_step**.
The algorithm graded this `MEDIUM` because coverage (68.5%, 377/550
events) fell just under the 70% MEDIUM/HIGH cutoff. The blind review
graded it `HIGH`, for two reasons visible in the evidence alone: (1) the
two adjacent findings in the *same scenario* had coverage of 70.0% and
71.0% and were both graded `HIGH` — evidentially indistinguishable from
68.5%, yet landing in a different bucket; (2) `ratio_vs_baseline` for
this finding was exactly `1.0`, the strongest possible signal (within
this mechanism) that the missing 31.5% of events did not change the
answer.

### Which thresholds/rules look questionable

1. **The 70% MEDIUM/HIGH cutoff is a hard cliff with no evidence behind
   the exact number**, and the one disagreement found here sits directly
   on that cliff (68.5% vs. 70.0%/71.0% in evidentially similar
   findings in the same scenario). This is the same caveat Gate 2 and
   this report's §4 already gave for the 20%/70% constants (illustrative,
   not derived) — this follow-up adds a first piece of concrete evidence
   that the cliff can produce a borderline-arbitrary label flip between
   near-identical evidence.
2. **Compound findings (bottleneck: activity + resource) collapse two
   different evidence strengths into one label.** In
   `missing_resource_40pct`/bottleneck, activity coverage was 100% but
   resource coverage was 59.9%; the combined label (`MEDIUM`) obscures
   that the *activity* half of the finding is fully supported. The blind
   review agreed `MEDIUM` was defensible here (the finding does assert
   both claims), but flags this as a real design question for future
   gates: should a two-part finding report two confidence labels?
3. **The logical-inconsistency check is dataset-global, not scoped to the
   specific evidence category a finding depends on.** In
   `inconsistent_records_10pct`/abnormal_step, the 149 negative-duration
   events are counted across the whole dataset; the blinded fields give
   no way to tell whether any of them fall within the 605
   `Final Inspection Q.C.` events this specific finding used. The blind
   review still agreed with `LOW` (caution is warranted either way given
   the over-100% coverage anomaly), but for a partly different reason
   than the algorithm's "any nonzero count" rule — this is a real gap,
   not just a threshold-tuning question.

### Adjustment supported by this review

None. Per the brief, no rule or threshold was changed based on this one
review pass. The 68.5%-vs-70% disagreement is a single data point on a
constant already flagged as illustrative in §4 — it supports *documenting*
the cliff-edge risk (done above), not picking a new number. Widening the
70% boundary into a buffer/hysteresis band, or making the compound-finding
and inconsistency-scoping questions above concrete, would each need their
own small, bounded experiment, not a same-pass edit.

### What remains unresolved

- A genuine second, independent human reviewer (not the agent that built
  the mechanism) has not evaluated these findings. This follow-up is a
  self-consistency check, and should not be read as satisfying the
  original "human validation" intent on its own.
- Whether the 70% (and 20%) thresholds should become a buffer zone rather
  than a hard cutoff, and whether compound findings should be split into
  per-claim confidence, are both open design questions this review
  surfaced but did not resolve.
- Sample size is 21 findings from one dataset's seven scenarios; this is
  far too small to statistically validate any threshold, and was never
  intended to be more than an illustrative first pass, consistent with
  the "smallest next experiment" framing in §5.

## 7. Exit recommendation

The current thresholds are **adequate to carry into the next gate as a
working mechanism, not as validated constants**. The mechanism's
qualitative behavior — correctly withholding findings on zero evidence,
correctly downgrading over-covered-but-corrupted data via the
inconsistency check, and correctly scaling confidence with genuine
evidence loss — held up against independent (agent-performed, not
human-performed) scrutiny at a 95% agreement rate, with the one
disagreement traceable to a documented, already-flagged illustrative
constant rather than a flaw in the mechanism's logic. Do not treat the
specific threshold values (20%, 70%, 20-event minimum, 1.5x ratio) as
tuned or production-ready, and do not proceed past this gate assuming a
real human has signed off on them — that step is still open. Gate 4 was
not started.
