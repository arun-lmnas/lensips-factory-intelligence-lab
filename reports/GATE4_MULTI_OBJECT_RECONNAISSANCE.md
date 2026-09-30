# Gate 4 — Multi-Object Manufacturing Intelligence Reconnaissance

## 1. Executive Summary

This is a small, terminating reconnaissance experiment, not a product
decision. It tests one question:

> Does modelling relationships *between* manufacturing objects (order,
> product, operation, machine, worker, quality event) reveal intelligence
> that a conventional order/case-centric process view cannot, and is that
> intelligence worth the added modelling complexity?

Using the same dataset as Gate 2/3
([datasets/production_analysis/Production_Data.csv](../datasets/production_analysis/Production_Data.csv),
225 orders, 4,543 events, 31 machines, 43 products, 49 workers), we ran a
case-centric baseline and a multi-object analysis side by side.

**Headline result:** a small number of cross-order, multi-object questions
— which machines are shared bottlenecks across many products, and which
product/machine combinations concentrate quality rejects — are genuinely
answerable only by aggregating across cases, and the aggregation itself is
cheap (group-by, not a new engine). But one of the more ambitious
multi-object questions we attempted — "did an order's delay come from
waiting on a machine another order was occupying?" — could not be
credibly demonstrated with this dataset: the naive overlap check we built
flagged 3,220 of 3,230 within-case gaps (99.7%) as "on a contended
resource," which shows the check is too coarse to mean anything, not that
contention is pervasive. That result is reported as **NOT DEMONSTRATED**
below rather than presented as a finding.

The dataset has no material, BOM, or supplier fields, so every question in
the brief that depends on those objects is also **NOT DEMONSTRATED** here
— not because the idea is wrong, but because this dataset cannot test it.

## 2. Gate 4 Hypothesis

> Multi-object modelling reveals customer-relevant intelligence that a
> conventional order/case-centric process view cannot obtain, and that
> intelligence is worth the additional data and modelling complexity.

This experiment does not build the multi-object model as reusable
infrastructure (no OCEL framework, no digital twin, no transformer
ontology). It computes a fixed set of relationship-aware metrics directly
with pandas to see whether the *analytical difference* actually shows up.

## 3. Dataset and Experiment Scope

Reused, unmodified: [datasets/production_analysis/Production_Data.csv](../datasets/production_analysis/Production_Data.csv)
(same file as Gate 2/3). Object types already present in the data, with no
synthetic extension required:

| Object | Field |
|---|---|
| Order | `Case ID` (225 distinct) |
| Product | `Part Desc.` (43 distinct) |
| Operation | `Activity` (55 distinct) |
| Machine / work centre | `Resource` (31 distinct) |
| Worker | `Worker ID` (49 distinct) |
| Quality event | Q.C.-labelled activities, `Rework`, `Qty Rejected`, `Qty for MRB` |

**Not present, and not synthesized:** material/BOM, supplier. Per the Gate
4 brief's instruction not to spend time chasing the perfect dataset and to
synthesize only where necessary, we judged the existing object types
sufficient to test the hypothesis, and left the material/supplier
questions unanswered rather than inventing data for them (see §8, §10).

Reproducible script:
[experiments/gate4_multi_object_reconnaissance/run_experiment.py](../experiments/gate4_multi_object_reconnaissance/run_experiment.py).
Full output:
[experiments/gate4_multi_object_reconnaissance/results/results.json](../experiments/gate4_multi_object_reconnaissance/results/results.json).
Run inside the Gate 0 devcontainer image, pandas only — no PM4Py process
model was needed for these metrics.

## 4. Case-Centric Baseline

Treating each `Case ID` as a closed unit, in isolation from every other
case:

- **225 orders**, mean duration 494.9 h, median 333.6 h, max 2,098.9 h
  (Case 199).
- **Longest-duration activities in total** (summed across all orders):
  Turning & Milling – Machine 4 (1,457.2 h), Turning & Milling – Machine 5
  (1,394.9 h), Turning & Milling – Machine 6 (1,328.4 h), Final Inspection
  Q.C. (1,052.4 h), Round Grinding – Machine 3 (1,046.5 h).
- **3,230 within-case waiting gaps** identified (a case's event ends, the
  next event on that same case starts later). The ten longest gaps are all
  900–1,373 hours and mostly precede a Q.C., Lapping, or Packing step.

**What this view can answer:** order duration, which activities/resources
consume the most cumulative time, where in a single order's sequence the
big waits occur.

**What this view cannot answer (its limitations, confirmed by the
experiment):**

1. Whether a waiting gap is because the *next* resource was busy on a
   *different* order, or for some other reason — a case-centric view has
   no other case to compare against.
2. Whether high resource-time for a machine is concentrated on a handful
   of products or spread across many — each case only sees its own share.
3. Whether a quality issue recurs for a specific product+machine or
   worker+machine combination across different orders — each case is
   analysed as a closed unit, so a pattern that only appears when you look
   *across* orders is invisible.

These three are exactly the questions the multi-object view was built to
test.

## 5. Multi-Object Analysis

All numbers from
[results.json](../experiments/gate4_multi_object_reconnaissance/results/results.json),
run once, unmodified.

### 5.1 Cross-order machine contention

For each machine, we found event pairs from *different* orders whose
Start/Complete windows overlap. This relationship (machine ↔ order ↔
order) cannot be expressed in a single case's process view.

| Resource | Distinct orders using it | Cross-order overlapping pairs | Total overlap hours |
|---|---|---|---|
| Quality Check 1 | 214 | 1,646 | 2,341.2 |
| Packing | 175 | 526 | 657.0 |
| Machine 1 – Lapping | 132 | 93 | 120.9 |
| Machine 5 – Turning & Milling | 35 | 17 | 61.1 |
| Machine 6 – Turning & Milling | 39 | 17 | 48.5 |

Most named machines (turning/milling/grinding stations) show only a
handful of overlapping pairs — consistent with those being one-order-at-a-
-time stations. Quality Check 1 and Packing show far more overlap, which
is plausible for a shared inspection/packing station that legitimately
batches multiple orders (see §8 for why this is not proof of contention).

### 5.2 Product × machine quality concentration

Aggregating `Qty Rejected` / `Qty for MRB` / `Rework` by (product,
machine) across all orders of that product — invisible from any single
order's record:

| Product | Machine | Orders | Rejected qty | MRB qty |
|---|---|---|---|---|
| Cable Head | Quality Check 1 | 47 | 215 | 101 |
| Ballnut | Quality Check 1 | 57 | 98 | 0 |
| Punch Holder | Quality Check 1 | 3 | 37 | 0 |
| Spur Gear | Quality Check 1 | 26 | 25 | 0 |
| Hinge | Machine 5 – Turning & Milling | 1 | 13 | 0 |

Cable Head and Ballnut (the two highest-volume products, 1,291 and 875
events respectively) account for the majority of reject and MRB volume —
consistent with their volume, not necessarily a rate anomaly. This is a
genuine cross-order aggregation, but see §8 on why the current data cannot
separate "high volume → high absolute rejects" from "this product/machine
pair has an elevated *rate* of quality problems."

### 5.3 Worker × machine reject rate

Reject rate (`Qty Rejected / (Qty Completed + Qty Rejected)`) by (worker,
machine), restricted to combinations with ≥5 events:

| Worker | Machine | Events | Reject rate |
|---|---|---|---|
| ID4163 | Quality Check 1 | 298 | 4.7% |
| ID4493 | Quality Check 1 | 164 | 1.8% |
| ID4287 | Quality Check 1 | 300 | 1.8% |
| ID4618 | Quality Check 1 | 419 | 1.2% |

All meaningfully-sized reject rates sit at the Quality Check station,
which is expected (that is where rejects are recorded, not necessarily
caused). This did not surface a distinct worker-caused or non-QC-machine
quality signal in this dataset.

### 5.4 Cross-order shared bottleneck vs. order-specific cost

Total processing hours per machine, alongside how many distinct
*products* and *orders* pass through it:

| Machine | Total hours | Distinct products | Distinct orders |
|---|---|---|---|
| Quality Check 1 | 2,077.6 | 41 | 214 |
| Machine 4 – Turning & Milling | 1,511.0 | 13 | 35 |
| Machine 5 – Turning & Milling | 1,412.3 | 6 | 35 |
| Machine 6 – Turning & Milling | 1,328.4 | 6 | 39 |
| Machine 1 – Lapping | 656.8 | 26 | 132 |

Quality Check 1 and Machine 1 – Lapping are used by a broad cross-section
of products and orders (genuine shared-resource candidates); Machines 4/5/6
concentrate their hours on a handful of products — a case-centric view
would report both kinds of machine as "high total activity time"
identically, without distinguishing "many different orders queue here"
from "this machine is just expensive for a few product families."

### 5.5 Attempted: delay attribution to a shared resource — NOT DEMONSTRATED

We tested whether a within-case waiting gap coincides with the *next*
resource being one this experiment separately flagged as cross-order-
-contended. Result: 3,220 of 3,230 gaps (99.7%) matched. This is not a
finding — it shows the check, as built, is too coarse to distinguish
anything (almost every machine in this dataset is used by more than one
order at some point, so almost every gap "matches"). A credible version of
this question needs actual resource-occupancy/queue modelling (was the
specific machine slot occupied at the specific moment the waiting order
needed it), which is materially more complex than a timestamp-overlap
proxy and was out of scope for this reconnaissance. Recorded here as
**NOT DEMONSTRATED**, not as a negative result — we did not build the
correct check, we built a check and it failed to discriminate.

## 6. Questions Enabled / Not Enabled

| # | Question | Case-centric? | Multi-object? | Additional data needed | Additional relationship needed | Insight materially different? | Potentially relevant to a factory decision? |
|---|---|---|---|---|---|---|---|
| 1 | Which machines create cross-order contention? | No | Partially (§5.1) | None (timestamps + resource already present) | Order↔Machine, cross-order | Yes — reveals shared-station load a single order's view can't show | Yes, if contention is real (see §8 caveat) |
| 2 | Which material shortages affect multiple production orders? | No | No | Material/lot, supplier | Material↔Order | Not demonstrated | Unknown |
| 3 | Which supplier/material issue propagates into production delays? | No | No | Supplier, material, PO data | Supplier↔Material↔Order | Not demonstrated | Unknown |
| 4 | Which machines are associated with delays across different orders/products? | Weak (only within one order) | Yes (§5.4) | None | Machine↔Order, Machine↔Product | Yes — separates shared-bottleneck machines from order-specific-cost machines | Yes |
| 5 | Which quality issue is associated with a particular material, machine or operation? | Weak (per-order only) | Partial — machine/operation yes (§5.2), material no | Material/lot for the material dimension | Product↔Machine↔QualityEvent | Yes for machine/product; not demonstrated for material | Yes for machine/product |
| 6 | Does a delay in one object propagate into another object? | No | Attempted, not demonstrated (§5.5) | Real queue/occupancy log, not just start/complete timestamps | Order↔Machine↔Order (time-indexed) | Attempted; check too coarse to conclude | Would be high value if it could be shown reliably |
| 7 | Are several apparently independent order delays actually caused by the same shared resource? | No | Attempted, not demonstrated (§5.5) | Same as #6 | Same as #6 | Not demonstrated | Would be high value if it could be shown reliably |
| 8 | Can a production bottleneck be distinguished from a material or quality bottleneck? | No | Partial — machine bottleneck yes (§5.4), material bottleneck no (no material data) | Material/lot | Machine↔Order + Material↔Order | Partially — only the machine side demonstrated | Yes for the machine side |

## 7. Complexity vs Additional Intelligence

| Insight | Case-centric possible? | Multi-object required? | Additional data | Additional modelling complexity | Potential factory value |
|---|---|---|---|---|---|
| Shared-bottleneck machine vs. product-specific-cost machine (§5.4) | No | Yes | None (already in data) | Low (group-by across orders instead of within one) | Medium |
| Product × machine quality concentration (§5.2) | No | Yes | None (already in data) | Low (group-by) | Medium — but rate vs. volume confound not resolved (§8) |
| Cross-order machine contention as a raw overlap signal (§5.1) | No | Yes | None (already in data) | Low to compute, but interpretation is unreliable (§8) | Not demonstrated |
| Delay propagation via shared resource (§5.5) | No | Yes, and more: a real occupancy/queue model | Resource-occupancy or scheduling log, not just start/complete pairs | High — timestamp overlap is not sufficient; needs a genuine queueing/simulation-adjacent model | High, if it could be demonstrated |
| Material-shortage / supplier propagation to delay | No | Yes | Material/lot, supplier, PO data — not present here | High (new object types, new relationships, new data source) | Not demonstrated (no data to test) |

The clearest, cheapest wins (bottleneck-vs-product-cost, quality
concentration by product/machine) need no new data and only a group-by —
this is not "OCEL-required" territory, it is ordinary cross-case
aggregation that a case-centric tool could also produce if it were asked
to compare across cases rather than treat each as an island. The
genuinely hard multi-object questions (delay propagation, material/supplier
chains) need materially more data and materially more modelling than this
reconnaissance attempted, and in this experiment the attempted shortcut
(timestamp overlap as a contention proxy) did not hold up.

## 8. Evidence Reliability and Limitations

Carrying forward the Gate 2/3 principle: a relationship is not established
just because two fields can be joined.

- **Quality-event coverage:** 214 of 225 cases (95.1%) have at least one
  Q.C.-labelled event. The 11 cases without one are a small gap, not
  large enough on its own to withhold the quality findings above, but
  worth noting the same way Gate 2/3 would.
- **Machine contention (§5.1) is a proxy, not a direct observation.** The
  dataset has no queue, scheduling, or resource-lock log — only
  Start/Complete timestamps per event. Two events on the same named
  resource with overlapping windows could reflect genuine simultaneous
  use, a shared batch-processing station (plausible for Quality Check 1 /
  Packing), or a timestamp/data-entry granularity artefact. This
  experiment cannot distinguish those causes, so §5.1's numbers should be
  read as "candidate contention," not "confirmed contention."
- **Product/machine quality concentration (§5.2) conflates volume and
  rate.** Cable Head and Ballnut have the most events overall, so they
  also have the most absolute rejects. We did not compute a rate
  normalised by volume with enough per-cell sample size to be confident
  it isn't noise — flagged as a limitation, not corrected here, to avoid
  overstating the finding.
- **Worker reject rate (§5.3) is correlational only.** A reject recorded
  while a given worker was active at Quality Check 1 does not mean that
  worker caused the reject — it could be the part, the upstream machine,
  or the material. The dataset gives no way to attribute cause.
- **Delay attribution (§5.5) is explicitly withheld** — see §5.5 for why
  the check as built does not discriminate.
- **Material and supplier objects are absent from this dataset.**
  Questions 2, 3, and the material half of question 8 in §6 are marked
  NOT DEMONSTRATED for this reason, not because they are judged
  unimportant.

## 9. Potential Transformer Relevance

Mapping the demonstrated pattern types onto a transformer manufacturing
chain (Sales Order → Transformer/Design → BOM/Materials → Operations →
Machines/Work Centres → Subcontracting → Testing/Quality) — conceptually
only, no transformer-specific model was built:

- **Shared-bottleneck vs. order-specific-cost machine (§5.4):** plausible
  fit — a winding machine or a core-cutting line used across many
  transformer designs is a natural analogue to "Machine 1 – Lapping used
  by 132 of 225 orders."
- **Product × machine quality concentration (§5.2):** plausible fit — e.g.
  a specific winding station or tank-welding station showing
  disproportionate rejects for a specific transformer rating/design
  family.
- **Cross-order contention (§5.1) and delay propagation (§5.5):**
  conceptually the most valuable for transformer manufacturing (long lead
  times, expensive shared capital equipment like large ovens/impregnation
  tanks/test bays), but this experiment shows the *naive* version of this
  check does not work — it would need real scheduling/occupancy data, not
  just start/complete timestamps, to be credible in a transformer factory
  either.
- **Material/supplier propagation:** the most obviously relevant pattern
  for transformers (e.g. a copper or CRGO steel supply issue affecting
  multiple orders) but entirely untested here — no material/supplier data
  existed in this dataset to test it against.

## 10. Demonstrated vs Plausible vs Unknown

**Demonstrated** (in this experiment, on this dataset):
- Multi-object aggregation (machine↔order↔product) surfaces a
  shared-bottleneck-vs-product-cost distinction and a product/machine
  quality-concentration pattern that a case-centric view structurally
  cannot produce, using only group-bys over data already present — no new
  data collection or modelling engine required for this class of
  question.
- A naive timestamp-overlap proxy for "delay caused by shared-resource
  contention" does not produce a usable signal on this dataset (99.7% of
  gaps flagged — a discrimination failure, not a finding).

**Plausible** (appears transferable to transformer manufacturing, not
demonstrated):
- The same shared-bottleneck and quality-concentration analyses could
  apply to transformer winding/core/tank-processing stations and
  design/rating families, given comparable order/operation/machine/quality
  event data.
- Material/supplier propagation to delay is the most plausible
  high-value pattern for transformer manufacturing specifically, but was
  not testable here.

**Unknown** (requires customer data or domain validation):
- Whether real transformer-factory data (ERP/MES/QMS/engineering) exposes
  a genuine resource-occupancy or scheduling signal that would make
  delay-propagation analysis (§5.5, §6 Q6/Q7) actually work.
- Whether material/supplier data would be made available at all, and at
  what granularity (lot-level, PO-level, supplier-level).
- Whether the quality-concentration pattern (§5.2) reflects a genuine
  rate anomaly or is fully explained by production volume, once normalised
  properly against real data.

## 11. Questions for Chris

1. **Customer problem:** What specific factory problem is the customer
   trying to solve — diagnosis of a known issue, general optimization,
   benchmarking against peers/standards, or engineering/design validation?
   Different answers point to very different next steps.
2. **Desired output:** Is the customer expecting a diagnostic finding
   ("here is what's wrong"), a benchmark ("here is how you compare"), or
   an ongoing monitoring capability?
3. **Data availability:** Would the customer provide raw ERP/MES/QMS/
   engineering data, or do they already have process metrics and expect
   LENSIPS to analyse/benchmark those metrics rather than raw events?
4. **Data granularity:** At what level is data actually recorded —
   order, operation, machine, material/lot, quality event, cost? This
   experiment shows the value of the multi-object view is highly
   dependent on which of these levels actually exist and are populated.
5. **Historical depth:** How much history is available, and is it clean
   enough for the same category-coverage checks Gate 2/3 established to
   be meaningful (i.e., can we tell whether missing evidence means
   "didn't happen" or "wasn't logged")?
6. **Benchmarking type:** Is the customer expecting benchmarking against
   their own historical performance, against peer factories, against
   regional industry benchmarks, or against engineering/design standards
   (IEC/IEEE)? These require entirely different evidence sources, and
   LENSIPS should not claim to provide external industry benchmarks
   without one.
7. **Commercial model:** Is this envisioned as a one-off paid factory
   assessment, a consulting/data-analysis engagement, a LENSIPS
   capability/module, a recurring factory-intelligence subscription, or
   bespoke customer development?
8. **Repeatability:** Is this a requirement specific to one transformer
   manufacturer, a recurring need across multiple transformer
   manufacturers, or potentially applicable to engineered manufacturing
   more broadly? The answer materially changes whether further investment
   should be scoped as a one-off engagement or a reusable capability.

## 12. Recommendation on Whether to Proceed

This experiment demonstrated a real, low-complexity analytical gain from
multi-object aggregation for two question types (shared-bottleneck
identification, product/machine quality concentration) — these need no new
data and no new architecture beyond ordinary cross-case grouping, so they
are low-risk to prototype further if a customer need for them is
confirmed. It also demonstrated that the more ambitious multi-object
questions (delay propagation across shared resources, material/supplier
chains) are either not achievable with the kind of data this dataset
represents, or require materially more data and modelling investment than
this reconnaissance attempted — those should not be assumed available or
easy.

**What this experiment actually proved:** that a subset of multi-object
questions (machine-as-shared-bottleneck, product/machine quality
concentration) are answerable from data already present in this dataset,
using simple aggregation, in a way a case-centric-only tool structurally
cannot produce; and that a naive proxy for delay-propagation-via-shared-
-resource does not hold up under scrutiny.

**What this experiment did not prove:** that these patterns are common or
reliable across real transformer-factory data; that material/supplier
propagation questions are answerable at all (no data existed to test
them); that LENSIPS has any competitive advantage in this space; that any
of this is commercially validated; or that the delay-propagation/
contention questions can be made reliable without materially more data
than start/complete timestamps.

**What can only be answered by Chris/customer evidence:** the actual
factory problem, the data the customer would provide and at what
granularity, the benchmarking type expected, the commercial model, and
whether this need repeats across multiple customers (§11).

Per the Gate 4 boundary, this reconnaissance does not proceed to a larger
architecture. Any further work should wait on answers to §11.
