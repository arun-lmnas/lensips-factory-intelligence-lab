# Gate 2 — Data Realism & Process Intelligence Experiment

Scope: test whether PM4Py-based process discovery, conformance, and
performance analysis remain useful when a real manufacturing event log is
degraded to resemble the sparse, incomplete, fragmented data documented in
[reports/ENTERPRISE_EVIDENCE.md](ENTERPRISE_EVIDENCE.md) #12 and #17 as
typical for small/medium manufacturers. This is an evidence-gathering
experiment, not product architecture. No OCEL work, no OFacT/digital-twin
work, no LLM reasoning, no customer-specific transformer modeling, and no
production architecture were done — those remain out of scope per the Gate
2 brief.

Reproducible artifacts: [experiments/gate2_data_realism/run_experiment.py](../experiments/gate2_data_realism/run_experiment.py),
raw results in [experiments/gate2_data_realism/results/results.json](../experiments/gate2_data_realism/results/results.json).

---

## 1. Dataset

**"Production Analysis with Process Mining Technology"** (Dafna Levy,
Eindhoven University of Technology; published via 4TU.ResearchData, DOI
`10.4121/uuid:68726926-5ac5-4fab-b873-ee76ea412399`,
https://data.4tu.nl/articles/dataset/Production_Analysis_with_Process_Mining_Technology/12697997/1).
Downloaded directly from 4TU.ResearchData and stored at
`datasets/production_analysis/Production_Data.csv` (4,543 rows), alongside
the dataset's original documentation PDF (`MI_-Eng.pdf`).

This is a **real** manufacturing event log from a machine shop, not a
synthetic dataset:

- 225 cases (work orders), 55 distinct activity labels, 31 distinct
  machine/resource identifiers (e.g. `Machine 4 - Turning & Milling`,
  `Quality Check 1`).
- Each row is one recorded operation with an explicit **Start Timestamp**
  and **Complete Timestamp**, plus quality fields: `Qty Rejected`, `Qty for
  MRB` (material review board / quality hold), and a `Rework` flag.
- This structure (order → sequence of machine operations → quality
  inspection → packing) is a reasonable, if much simpler, analog for a
  transformer order's core/winding/assembly/test flow — close enough to be
  useful for testing data-degradation *mechanics*, while being explicitly
  **not** a transformer manufacturer and **not** proof that findings
  transfer to that domain (see Limitations, §5).

## 2. Method

1. Load the full CSV and sort events by case and completion time. This is
   the **baseline** ("what actually happened," to the extent the recorded
   data reflects it).
2. Discover a **reference process model** from the baseline log using
   PM4Py's inductive miner (`pm4py.discover_petri_net_inductive`). This
   model stands in for "the process," fixed for the whole experiment.
3. Construct seven variants of the raw event data (baseline + six
   degradation scenarios, described below), using a fixed random seed
   (42) for reproducibility.
4. For each variant, independently of the others:
   - Compute **performance metrics**: case count, event count, mean/median
     case duration, top-5 activities and top-5 resources by total recorded
     duration (a simple, directly interpretable bottleneck proxy).
   - Compute **conformance** of the variant's log against the *baseline's*
     reference model (token-based replay: `pm4py.fitness_token_based_replay`).
     Because the reference model is fixed, any fitness drop is attributable
     to the data degradation, not to a different "true" process.
   - Discover the variant's *own* Petri net, to see how model complexity
     (places/transitions/arcs) reacts to the same degradation.
5. Compare each variant's top bottleneck (activity and resource) against
   the baseline's, and record whether the #1 ranking is preserved.

All code runs inside the Gate 0 devcontainer image (`lensips-gate0:test`,
built from the unmodified `.devcontainer/Dockerfile`), not on the host:

```bash
docker build -t lensips-gate0:test -f .devcontainer/Dockerfile .
docker run --rm --init -v "$PWD":/workspace -w /workspace \
  lensips-gate0:test python3 experiments/gate2_data_realism/run_experiment.py
```

(`--init` works around a `psutil`/PID-1 edge case in the container's
process-mining library when running as a bare `docker run` foreground
process; it does not change anything about the devcontainer image itself.)

## 3. Degradation scenarios

| Scenario | What it simulates | Mechanics |
|---|---|---|
| `baseline` | Full, clean data (control) | No change |
| `milestone_only` | Coarse ERP logging — only "order started" / "order finished" milestones, per ENTERPRISE_EVIDENCE.md #12 | Keep only the first and last recorded event per case |
| `missing_timestamps_30pct` | Events that couldn't be reliably timestamped | Randomly drop 30% of events entirely (an untimestamped event cannot be ordered) |
| `missing_resource_40pct` | Machine/operator identity not captured | Null the `Resource` field on 40% of events; event/timestamp data kept |
| `incomplete_relationships_30pct` | Process steps that simply never produced an event | Drop 30% of *middle* events per case (never the case's first or last) |
| `inconsistent_records_10pct` | Manually re-entered/conflicting records from disconnected systems | Duplicate 10% of events with a jittered timestamp, then swap Start/Complete on 3% of all events (creating logically impossible negative-duration records) |
| `missing_quality_events` | A QMS not connected to the systems LENSIPS can reach | Drop every event whose activity name contains "Q.C.", "Inspection", or "MRB" |

## 4. Results

Full machine-readable results:
[experiments/gate2_data_realism/results/results.json](../experiments/gate2_data_realism/results/results.json).
Summary:

| Scenario | Cases | Events (% of baseline) | Fitness vs. reference model | Top-1 activity bottleneck matches baseline? | Top-1 resource bottleneck matches baseline? |
|---|---|---|---|---|---|
| baseline | 225 | 4543 (100%) | 0.9991 | — (is baseline) | — (is baseline) |
| milestone_only | 225 | 444 (9.8%) | **1.0000** | **Yes** | **Yes** |
| missing_timestamps_30pct | 222 | 3181 (70.0%) | 0.9990 | Yes | Yes |
| missing_resource_40pct | 225 | 4543 (100%) | 0.9991 | Yes | Yes |
| incomplete_relationships_30pct | 225 | 3411 (75.1%) | 0.9989 | Yes | Yes |
| inconsistent_records_10pct | 225 | 4997 (110.0%) | 0.9989 | **No** | Yes |
| missing_quality_events | 220 | 3349 (73.7%) | 0.9992 | Yes | **No** |

Baseline top-5 activity bottlenecks (by total recorded duration): Turning &
Milling – Machine 4, Machine 5, Machine 6, **Final Inspection Q.C.**, Round
Grinding – Machine 3. Baseline top-1 *resource* bottleneck: **Quality
Check 1** (the combined resource behind both "Final Inspection Q.C." and
"Turning & Milling Q.C." activities, 1,192 of 4,543 events).

### Finding 1 — Conformance/fitness is not a usable proxy for data completeness

Fitness against the fixed reference model stayed at or above **0.9989** in
*every* scenario, including `milestone_only`, where 90.2% of all events
were removed. It even reached a perfect **1.0000** for `milestone_only`.
This is because the inductive miner discovers a permissive model with many
optional paths, so a 2-event trace trivially "fits." **A LENSIPS
data-reliability layer must not use conformance/fitness scores as a
stand-in for "do we have enough data" — they answer a different question
("is the observed behavior consistent with the model"), not "did we
observe everything that happened."** This is the single most important,
and most non-obvious, finding of this experiment.

### Finding 2 — The one finding that actually mattered (a quality bottleneck) silently disappeared, with no warning signal

In the baseline, the busiest single *resource* was the quality-inspection
station (`Quality Check 1`). In `missing_quality_events` — a directly
plausible real-world condition (a QMS not connected to the systems LENSIPS
can reach) — that finding **vanishes completely** from the top-5 resource
ranking, and the new top-1 resource bottleneck is a turning/milling
machine instead. Nothing else in the output signals that anything is
wrong: fitness against the reference model is actually slightly *higher*
(0.9992) than baseline, and case counts/durations look normal. **A system
that only reports "your bottleneck is Machine 4" without also reporting
"0% of expected quality-inspection events were observed" would give a
confidently wrong-by-omission answer.** This is the concrete evidence
behind the Gate 1 recommendation to make an evidence/reliability layer a
MUST, not a nice-to-have.

### Finding 3 — Missing/sparse data degrades gracefully on this dataset; conflicting data does not

Every "missing data" scenario (`milestone_only`, `missing_timestamps_30pct`,
`missing_resource_40pct`, `incomplete_relationships_30pct`) preserved the
correct #1 activity bottleneck. The **only** scenario that changed which
activity ranked #1 was `inconsistent_records_10pct` (duplicated events
plus swapped timestamps), which also produced 149 logically-impossible
negative-duration events. **Conflicting/duplicated records were more
dangerous to quantitative rankings, in this dataset, than sparse or
missing records were.** This suggests a reliability layer should treat
"detected inconsistency" (e.g. negative durations, duplicate near-identical
events) as a distinct and arguably higher-severity category than "detected
incompleteness" (missing fields/events) — the two need different flags,
not one generic "data quality: low" signal.

### Finding 4 — Robustness to missing events is dataset-structure-dependent, not a general guarantee

`milestone_only` kept only 9.8% of events yet still recovered the correct
top-1 bottleneck and a case-duration estimate within 0.02% of the
baseline. This is **not** evidence that milestone-only data is generally
sufficient — it worked here because the dominant bottleneck machines in
*this* dataset happen to frequently be the first or last operation on a
work order, so they survive the "keep first+last event" degradation by
construction. A different case structure (e.g. the bottleneck being a
middle step, as is plausible for a specific winding or core-assembly step
in transformer manufacturing) would not have this property. **This result
must not be generalized beyond this dataset without direct testing on
data shaped like the target process.**

### Finding 5 — Rare resources can vanish from analysis purely by chance under random missingness

Randomly nulling 40% of `Resource` values (`missing_resource_40pct`)
reduced the number of distinct resources observed from 31 to 29, purely by
chance (two low-frequency resources happened to have all their instances
nulled). The top-1 resource bottleneck ranking was unaffected because it is
high-volume, but a rarer, lower-volume machine's problem could disappear
from a report exactly the way the quality bottleneck did in Finding 2. A
reliability layer should report per-field coverage (e.g. "`Resource`
present on 60% of events; `N` distinct resources observed") rather than
silently proceeding with whatever data survived.

## 5. What data-quality/reliability checks this experiment suggests LENSIPS should expose

Directly justified by the findings above, not by the plans in Gate 1
alone:

1. **Explicit event/field coverage metrics**, separate from and in
   addition to conformance/fitness: event retention rate, per-field null
   rates (timestamp, resource, activity), and count of distinct
   activities/resources observed vs. however many are expected/known to
   exist (Finding 1, 5).
2. **Category-level presence checks for decision-relevant activity types**
   (e.g. "quality inspection events observed: 0%" as an explicit,
   surfaced statement) rather than only a generic completeness percentage,
   because a generic percentage (73.7% of events retained in
   `missing_quality_events`) does not by itself reveal that an entire
   *category* of activity vanished (Finding 2).
3. **Logical-consistency checks as a distinct, higher-severity signal**:
   negative-duration events, duplicate near-identical events, and
   out-of-order timestamps should be counted and flagged explicitly, not
   folded into a generic "data quality: medium" score (Finding 3).
4. **An explicit statement that conformance/fitness scores are not a
   data-completeness indicator**, wherever they are shown to a customer or
   used internally, to prevent the exact false-confidence failure mode in
   Finding 1.
5. **Confidence should scale with, and be reported alongside, coverage** —
   a bottleneck finding backed by 100% event coverage should be
   distinguishable, in what LENSIPS shows the customer, from the same
   finding backed by 10% coverage, even when both currently produce an
   identical-looking discovered model or fitness score.

## 6. Minimum evidence required for a useful factory finding

Based on this experiment: `case_id + activity + a reliable timestamp`
survived every missing-data scenario tested and still produced directionally
correct case-duration and gross-activity-bottleneck findings — **provided**
the missingness was not concentrated in the specific category the finding
is about. The corollary is the important part: **there is no single
"minimum evidence" threshold that works for every finding.** The right
question is not "do we have enough data overall" but "do we have enough
*coverage of the specific thing this finding is about*" — a genuinely
different, per-finding question that a generic completeness percentage
cannot answer on its own (Finding 2, 5).

## 7. Limitations of this experiment

- **Single dataset, single industry.** This is a small machine shop
  (turning, milling, grinding, quality inspection, packing), not a
  transformer manufacturer. Findings about *mechanics* (fitness vs.
  completeness, category-blindness, conflicting-data sensitivity) are
  likely to generalize; findings about *magnitude* (e.g. "90% event loss
  still works") are dataset-structure-dependent and are explicitly flagged
  as such in Finding 4.
- **Synthetic degradation, not real customer data.** The degradation
  scenarios were constructed programmatically with fixed percentages and a
  fixed random seed, not derived from an actual medium manufacturer's real
  data gaps. They are a reasonable proxy for the *kinds* of gaps documented
  in ENTERPRISE_EVIDENCE.md #12, not a measurement of any real customer.
- **PM4Py defaults only.** The inductive miner and token-based replay were
  used with default parameters; no attempt was made to tune discovery
  algorithms or noise thresholds, or to compare against alternative
  discovery/conformance algorithms (e.g. alignments, heuristics miner).
- **No resource-utilization-rate or queueing analysis** was computed
  (only total time by activity/resource) — a fuller performance-analysis
  pass (e.g. waiting time between activities, actual bottleneck-by-queue
  rather than bottleneck-by-total-recorded-time) was out of scope for this
  gate.
- Per the Gate 2 brief, this experiment deliberately did **not** touch
  OCEL/object-centric modeling, OFacT/digital-twin work, LLM reasoning, or
  transformer-specific modeling.

## 8. Next smallest experiment justified by these results

The most valuable next step is not a bigger dataset or more degradation
scenarios — it is validating a **first-cut, concrete implementation of the
"category-level presence check"** from §5 point 2, since Finding 2 is the
single most consequential result here (a silently vanishing finding, with
no warning from any metric already in use). Concretely:

> Build a small prototype "coverage report" function that, given an event
> log and a list of decision-relevant activity categories (e.g. "quality
> inspection," "rework"), reports per-category event counts and flags any
> category with zero or near-zero observed events — then re-run it against
> the `missing_quality_events` variant from this experiment and confirm it
> correctly flags the gap that the fitness score missed. This is a small,
> bounded, terminating task (per this lab's own agent task contract) that
> directly tests the specific mechanism this experiment identified as
> necessary, before any broader Evidence/Reliability Layer design work
> begins.

This does not require a new dataset, does not require OCEL/digital
twin/LLM work, and can be evaluated against the artifacts already produced
in this gate.
