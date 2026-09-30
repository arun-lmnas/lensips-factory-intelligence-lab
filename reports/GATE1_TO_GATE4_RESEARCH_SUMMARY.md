# Gate 1–4 Integrated Research Summary — Object-Centric Manufacturing Intelligence

## 1. Executive Summary

This report restarts and supersedes the Gate 4 reconnaissance in
[reports/GATE4_MULTI_OBJECT_RECONNAISSANCE.md](GATE4_MULTI_OBJECT_RECONNAISSANCE.md)
(commits `76a411c..4902fd3`), which was judged insufficiently convincing:
its dataset (the Gate 2/3 machine-shop log) had no real material,
supplier, or independently-identified quality object, so it could not
properly test whether object-centric process intelligence adds value over
a case-centric view. That report is not edited or defended here — this is
a fresh experiment on a genuinely multi-object real dataset, re-running
Gate 1's capability questions, Gate 2's evidence-degradation test, Gate
3's evidence-grounded-finding mechanism, and a proper Gate 4 object-centric
analysis, consistently against it.

**Dataset:** a real-data subsample of the BPI Challenge 2019 OCEL log —
the actual purchase-to-pay process of a real multinational coatings/paints
manufacturer — with four genuine object types (`PO`, `POItem`, `Vendor`,
`Resource`) and real many-to-many relationships between them. Full
provenance and sampling method:
[reports/GATE4_DATASET_SELECTION.md](GATE4_DATASET_SELECTION.md).

**Headline result:** on this dataset, object-centric analysis surfaced a
finding the case-centric view structurally cannot produce, and it survived
scrutiny: **1,002 of 1,011 sampled purchase orders (99.1%) sit in one
connected component of the object-interaction graph**, reachable from one
another only through a small number of shared vendors and shared
processing resources (one `Resource` object alone touches 2,884 other
objects). The case-centric, POItem-flattened process model has no way to
represent this — every item is an independent trace in that view. This is
a genuine, PM4Py/OCEL-native finding (graph connectivity, not a group-by).
At the same time, several of the object-centric analyses we attempted
*were* reducible to ordinary pandas group-bys, and are labelled as such
rather than counted as evidence for the hypothesis (§8). The Gate 2
conclusion (process-mining fitness is not a completeness signal) and the
Gate 3 mechanism (withhold findings when evidence is insufficient) both
re-confirmed on this new, real dataset (§5, §6).

**What this does not show:** anything about shop-floor production
(machines, operations, cycle time) — this dataset is a procurement
process, not a production floor — or about material/quality objects,
which this dataset does not contain either. See §12 and §14 for exactly
what remains unproven.

## 2. Research Question

> Can LENSIPS provide trustworthy factory intelligence from operational
> manufacturing evidence, while explicitly accounting for evidence
> completeness, data quality, multiple interacting manufacturing objects,
> and process behaviour?

Gate 4 hypothesis under test:

> Does object-centric / multi-object process intelligence reveal
> meaningful manufacturing insights that are difficult or impossible to
> obtain from a conventional case-centric process model?

## 3. Dataset and Provenance

Summarized here; full detail in
[reports/GATE4_DATASET_SELECTION.md](GATE4_DATASET_SELECTION.md).

- **BPI Challenge 2019 (OCEL)**, DOI `10.4121/46a7e15b-10c7-4ab2-988d-ee67d8ea515a`,
  CC BY 4.0, real data from a real coatings/paints multinational's
  purchase-order handling process.
- Object types: `PO` (1,011), `POItem` (3,044), `Vendor` (409),
  `Resource` (316) in our sample.
- Sample: 20,011 events / 1,011 purchase orders, deterministically
  selected (seed 42) from the dominant subsidiary
  (`companyID_0000`, 99.6% of the full log's events) out of 75,962
  available purchase orders, whole-PO sampling (no partial orders), fully
  reproducible via
  [experiments/gate4b_object_centric_research/scripts/build_sample.py](../experiments/gate4b_object_centric_research/scripts/build_sample.py).
- No fabricated events or relationships. No material or quality object
  exists in this dataset — disclosed as a limitation, not worked around.

Reproducible experiment script:
[experiments/gate4b_object_centric_research/run_experiment.py](../experiments/gate4b_object_centric_research/run_experiment.py).
Full machine-readable output:
[experiments/gate4b_object_centric_research/results/results.json](../experiments/gate4b_object_centric_research/results/results.json).
Run inside the Gate 0 devcontainer image (`pm4py==2.7.14`).

## 4. Gate 1 — Capability Hypotheses, Re-tested

Re-applying the Gate 1 MUST/SHOULD/COULD/WON'T structure
([reports/CAPABILITY_PORTFOLIO.md](CAPABILITY_PORTFOLIO.md)) to what this
dataset actually let us demonstrate. Gate 1's strategic conclusions are
not rewritten — this section only classifies what ran against real data
this time.

| Capability | Status | Evidence |
|---|---|---|
| **MUST** — Case-centric process discovery and conformance | **Demonstrated** | Inductive-miner Petri net (72 places, 105 transitions) discovered over the 3,044-case POItem-flattened log; token-based-replay log fitness 0.997, 77.4% perfectly-fitting traces (§5) |
| **MUST** — Integration / normalization / reconciliation / reliability | **Partially demonstrated** | Evidence-coverage checking against the dataset's own documented compliance rule, and a degradation test reconfirming Gate 2, both ran successfully (§6). Reconciliation across independently-sourced systems (e.g. separate ERP + MES + QMS exports) was NOT tested — this OCEL is a single pre-built log, not something we integrated ourselves; **requires customer data** to test |
| **SHOULD** — Targeted object-centric modelling | **Demonstrated** | OC-DFG and object-interaction-graph analysis produced a finding (the 99.1%-connected component) the case-centric view cannot represent (§7) |
| **SHOULD** — Historical benchmarking | **Not demonstrated** | Only internal, within-sample vendor-to-vendor comparison was computed (§6); no peer-factory or industry benchmark source exists to test against — **requires external evidence** |
| **SHOULD** — Evidence-grounded reasoning over structured outputs | **Demonstrated** | Gate 3 mechanism re-run against this dataset's own schema; one of three questions deliberately withheld for insufficient evidence (§6) |
| **COULD** — Targeted what-if / simulation | **Not attempted** | Out of Gate 4b scope by design |
| **WON'T FOR NOW** (IEC/IEEE compliance, full digital twin, general enterprise process-management suite) | **Not attempted** | Unchanged from Gate 1; out of scope |

## 5. Gate 2 — Evidence Degradation, Re-tested

Gate 2's question: *can apparently useful process findings remain
misleading when important evidence is missing?*

This dataset documents its own evidence requirement (README.txt, quoted
in [GATE4_DATASET_SELECTION.md](GATE4_DATASET_SELECTION.md) §4): items
with category `3-way match, invoice after GR` or
`3-way match, invoice before GR` require a **Goods Receipt** event for the
process to be compliant; `Consignment` items do not.

**Baseline (untouched sample) coverage:**

| Item category | N items | Requires GR event? | Items with a GR event | Coverage |
|---|---|---|---|---|
| 3-way match, invoice after GR | 194 | Yes | 181 | 93.3% |
| 3-way match, invoice before GR | 2,651 | Yes | 2,539 | 95.8% |
| Consignment | 199 | No | 187 | 94.0% (not required) |

**Degradation scenario:** Goods Receipt events removed for a random,
documented 30% of the 2,845 three-way-match items (853 items; seed 7).

| Metric | Before | After |
|---|---|---|
| GR-event coverage on 3-way-match items | 95.6% | **67.1%** |
| Token-based-replay log fitness | 0.9968 | **0.9963** |
| Percentage of perfectly-fitting traces | 77.43% | **77.63%** (up, not down) |

**Result: the Gate 2 conclusion reconfirms on this new, real dataset.** A
required evidence category collapsed by 28.5 percentage points
(95.6%→67.1%), and the standard process-mining conformance score barely
moved — one of its two components (percentage of fitting traces) even
rose slightly, because removing an event can shorten a trace into a
shape the discovered model still accepts. **Process-mining fitness is not
a usable proxy for evidence completeness**, on a second, unrelated, real
dataset.

## 6. Gate 3 — Evidence-Grounded Findings, Re-tested

Three questions, following Question → Evidence requirement → Evidence
availability → Analysis → Finding → Confidence:

**Q1 — Which vendor is associated with abnormally long purchase-item
cycle time?**
Evidence requirement: ≥5 items per vendor for a stable mean. Of 392
distinct vendors in the sample, only 126 (32.1%) meet that bar — flagged
`PARTIAL` coverage, **confidence LOW**. The 5 slowest vendors meeting the
bar (`vendor_1039`: 211.3 days mean, `vendor_0453`: 192.0 days,
`vendor_0539`: 171.2 days, `vendor_0274`: 153.0 days, `vendor_0194`:
135.3 days) are reported as a candidate signal only — cycle time here is
confounded with item category and spend area, which was not controlled
for.

**Q2 — Is 3-way-match compliance satisfied for each item category?**
Answered directly from §5's coverage numbers against the dataset's own
documented rule: both applicable categories show `OK` coverage (93.3%,
95.8%, both above the 70% MEDIUM threshold carried over from Gate 3) —
**HIGH_CONFIDENCE** for both.

**Q3 — Does a delay in one PO propagate to another through a shared
vendor or resource?**
Evidence requirement: a resource-occupancy or workload-queue signal
showing the shared object was actually busy/blocked at the relevant time
— not just that it is connected to many objects. This OCEL has no such
signal (only event timestamps, no queue/lock log). **Confidence:
WITHHELD.** The object-interaction graph (§7) shows *which* POs share a
vendor or resource; it cannot show that sharing *caused* a delay. This
mirrors the same discipline Gate 3 established on the machine-shop
dataset and the same discipline Gate 4 v1 applied to its own (failed)
delay-attribution attempt — reconfirmed here on different data.

## 7. Gate 4 — Object-Centric Process Intelligence

### 7.1 Case-centric baseline (Part B)

The natural case notion for this process is the purchase-order line item
(`POItem`). Flattening the OCEL to this single object type
(`pm4py.ocel_flattening`) and running genuine PM4Py process discovery:

- Inductive Miner discovers a Petri net with 72 places, 105 transitions.
- Token-based-replay fitness: 0.997 log fitness, 77.4% perfectly-fitting
  traces, across 3,044 cases.
- Mean case duration 73.0 days, median 66.0 days, max 772.6 days.
- The slowest directly-follows activity pairs by mean elapsed time (e.g.
  `Cancel Goods Receipt → Cancel Invoice Receipt`, mean ~182 days) are
  dominated by rare cancellation/correction paths, not the everyday flow.

**What this view cannot answer**, confirmed by attempting it: whether many
different `POItem` cases share the same `Vendor` or the same processing
`Resource`; whether the choice of which object type to flatten on would
produce a structurally different process model from the same data (it
does — see §7.2); or whether a resource that looks unremarkable within one
item's trace is in fact touching thousands of others.

### 7.2 Object-centric analysis (Part C)

**OC-DFG (`pm4py.discover_ocdfg`)**, computed natively across all four
object types without collapsing to one case notion: the number of
*distinct* directly-follows activity-pairs observed differs by which
object type's thread you follow through the identical underlying events —
**Vendor: 286, PO: 247, POItem: 221, Resource: 166** distinct pairs. The
same event data looks like a different-shaped process depending on the
object lens used; a case-centric tool that must pick one object type has
no way to show this variation exists.

**Object interaction graph (`pm4py.discover_objects_graph`,
`graph_type="object_interaction"`)**: 26,543 edges between objects that
co-occur in at least one shared event. Edge counts by object-type pair:
`POItem–Resource` 12,484, `PO–Resource` 4,239, `Resource–Vendor` 2,721,
`POItem–Vendor` 3,044, `PO–POItem` 3,044, `PO–Vendor` 1,011. A small
number of `Resource` objects dominate connectivity — the top-connected
resource touches 2,884 other objects; the top-connected vendor touches
258.

**Connected components of the object interaction graph** — the clearest
genuinely OCEL-native finding in this experiment: the graph decomposes
into **3 components**, but one of them contains **4,752 of 4,780 objects
(99.4%)**, including **1,002 of the 1,011 sampled purchase orders
(99.1%)**. The other two components have 22 and 6 objects respectively.
In other words: almost every purchase order in the sample is transitively
reachable from almost every other purchase order, through shared vendors
and shared processing resources. Treating each order as an independent
case (as §7.1's case-centric view does, and as the original BPIC19
process-mining literature does) is a modelling simplification that this
object-centric analysis shows does not hold structurally for this real
dataset.

### 7.3 Compare the two models

| Question | Case-centric answer | Object-centric answer | Additional info revealed | Requires OCEL? | Evidence quality |
|---|---|---|---|---|---|
| What does the "normal" process look like? | Inductive-miner Petri net, 72 places / 105 transitions, 0.997 fitness | OC-DFG shows the shape varies by object type (166–286 distinct DF pairs depending on lens) | Process shape is not a single fixed thing — it depends on which object you track | Yes (OC-DFG is OCEL-native) | High — reproducible from a valid OCEL |
| Are purchase orders independent of one another? | Assumed yes (each is a separate case/trace) | No — 99.1% of orders sit in one connected component via shared vendors/resources | Materially different: the independence assumption the case-centric model makes is empirically false here | Yes (graph connectivity over the object-interaction graph) | High — direct graph computation, not inferred |
| Which vendors/resources are most "central"? | Not answerable — vendor/resource are event attributes, not first-class in a case-centric trace | Ranked by object-interaction-graph degree (top resource: 2,884 connections; top vendor: 258) | Materially different — this ranking has no case-centric analogue | No — this specific ranking is reproducible with a pandas group-by on the event-object mapping | Medium — correct but methodologically ordinary (§8) |
| Is a required evidence category (Goods Receipt) present? | Answerable per-case from the flattened log's activity set | Same answer; no OCEL-specific advantage | Not materially different | No | High, but not an object-centric-specific finding |
| Does a delay in one PO propagate to another via a shared vendor/resource? | Not answerable at all | Attempted; the object-interaction graph shows *connection*, not *propagation* | **Not demonstrated** — the necessary occupancy/queue evidence does not exist in this OCEL | Would require the OCEL relationship plus additional data this dataset lacks | Insufficient — deliberately withheld (§6, Q3) |

All three legitimate Gate 4 outcomes occurred in this single experiment:
**(A)** the connected-component finding is object-centric-required,
material intelligence; **(B)** the vendor/resource centrality ranking is
answerable both ways, with OCEL only adding convenience; **(C)** the
propagation question is blocked by missing evidence regardless of model
choice.

## 8. What PM4Py and OCEL Actually Contributed

For every major finding above, logged programmatically in
[results.json `part_f_pm4py_ocel_contributions`](../experiments/gate4b_object_centric_research/results/results.json),
including the mandatory thought experiment (*if PM4Py/OCEL were removed
and pandas could produce the same result, is this ordinary relational
analytics?*):

| Finding | PM4Py/OCEL API used | Removable → still pandas? | Classification |
|---|---|---|---|
| Case-centric Petri net + fitness (§7.1) | `ocel_flattening`, `discover_petri_net_inductive`, `fitness_token_based_replay`, `discover_performance_dfg` | No — inductive-miner discovery and token-based-replay fitness are process-mining algorithms with no pandas equivalent | **Genuine process-mining finding** |
| OC-DFG per-object-type DF-pair counts (§7.2) | `discover_ocdfg` | No — requires re-implementing OCEL directly-follows semantics per object type | **Genuine OCEL finding** |
| Vendor/Resource centrality ranking (§7.2) | `discover_objects_graph` | **Yes** — a group-by/count over the event-object mapping reproduces this ranking | **Ordinary relational analytics**, reported honestly as such rather than claimed as OCEL-specific evidence |
| Connected-component analysis (§7.2, the headline finding) | `discover_objects_graph` + `networkx.connected_components` | No — graph reachability/transitive-closure is not a group-by or join | **Genuine OCEL-native finding** — the strongest result in this experiment |
| Evidence-degradation re-test (§5) | `ocel_flattening`, `discover_petri_net_inductive`, `fitness_token_based_replay` | No — same reasoning as the baseline | **Genuine process-mining finding** |
| Evidence-grounded confidence gating (§6) | none (control flow over already-computed numbers) | Yes | **Ordinary relational analytics / control flow**, not attributed to OCEL |

**Net assessment:** roughly half of what this experiment produced is
genuinely attributable to PM4Py/OCEL algorithms (case-centric discovery
and conformance, OC-DFG, connected-component analysis on the object
graph); the other half (centrality ranking, confidence gating) is
ordinary analytics that OCEL made convenient to compute but did not
uniquely enable. The single finding that most directly supports the Gate
4 hypothesis — 99.1% of orders forming one connected component through
shared objects — is in the genuinely-OCEL-required category.

## 9. Evidence Reliability Across Gates

```
Gate 2: Can process analysis survive degraded evidence?
   -> No: fitness barely moved (0.9968->0.9963) while a required
      evidence category collapsed (95.6%->67.1%), reconfirmed on
      real BPIC19 data (§5), same conclusion as the machine-shop dataset.

Gate 3: Can the system recognize when a finding is insufficiently
        supported?
   -> Yes: 1 of 3 questions withheld (delay propagation, §6 Q3) for
      missing occupancy evidence; 1 downgraded to LOW confidence
      (vendor cycle time, §6 Q1) for insufficient per-vendor volume.

Gate 4: Can multi-object process intelligence reveal additional
        factory behaviour?
   -> Partially: yes for connectivity/independence-assumption
      questions (§7.2, genuinely OCEL-required); yes but only as
      "convenient analytics" for centrality ranking; no (withheld)
      for delay propagation, which needs evidence this dataset
      does not have.

Combined hypothesis: Can LENSIPS produce trustworthy intelligence
from complex, imperfect manufacturing evidence?
   -> Not proven universally. This experiment shows the evidence-
      gating discipline (Gates 2/3) transfers cleanly to a second,
      unrelated real dataset, and that object-centric modelling can
      surface a real structural finding (Gate 4) -- but only for
      questions the available data can actually support, and this
      remains one company's procurement process, not a transformer
      manufacturer's shop floor.
```

## 10. Potential Transformer Manufacturing Relevance

Mapping demonstrated object types conceptually onto a transformer
manufacturing chain — no transformer-specific model was built:

| BPIC19 object | Transformer manufacturing analogue |
|---|---|
| `PO` (purchase order) | Sales order or production order |
| `POItem` (line item) | BOM line item / operation |
| `Vendor` | Component supplier or subcontractor (e.g. CRGO steel, copper winding wire, bushings) |
| `Resource` | The engineer/planner/system that processes a step, or (by loose analogy) a work centre |

The **connected-component finding (§7.2)** is the most transferable
pattern conceptually: if a transformer manufacturer's real order book
shows the same structure — most open orders transitively linked through a
small number of shared critical suppliers or shared engineering/production
resources — then per-order diagnostics would systematically miss
shared-root-cause delays (e.g. one CRGO steel supplier's issue quietly
affecting nearly the whole order book). This is **plausible, not
demonstrated** — it has not been tested against any transformer or even
shop-floor production data.

## 11. Demonstrated vs Plausible vs Unknown

**Demonstrated** (in this experiment, on this dataset):
- Object-centric analysis (OC-DFG, object-interaction-graph connectivity)
  reveals a structural finding — near-total connectivity of purchase
  orders through shared vendors/resources — that the case-centric
  flattened view cannot represent, using genuine PM4Py OCEL algorithms,
  not pandas reimplementation (§7.2, §8).
- The Gate 2 conclusion (process-mining fitness ≠ evidence completeness)
  and the Gate 3 mechanism (withhold/downgrade findings under
  insufficient evidence) both reconfirm on a second, independent, real
  dataset (§5, §6).
- Not every object-centric-flavoured analysis is genuinely OCEL-required:
  roughly half of what we computed here was ordinary relational analytics
  that OCEL made convenient, not uniquely possible (§8) — an important,
  previously untested, honest boundary.

**Plausible** (appears transferable to transformer manufacturing, not
demonstrated):
- A similarly-structured order book (near-total connectivity through a
  few shared critical suppliers/resources) in a real transformer
  manufacturer's data, and the shared-root-cause-delay risk that would
  imply.
- The evidence-degradation and evidence-grounded-findings discipline
  (Gates 2/3) applying equally well to whatever real data a transformer
  manufacturer provides.

**Unknown** (requires customer data or domain validation):
- Whether transformer shop-floor data (machines, operations, materials,
  quality/testing) shows the same connectivity structure this procurement
  dataset showed — no dataset combining real shop-floor and real
  material/supplier/quality objects at this relationship depth was found
  publicly (§14, Gate 4 Dataset Selection §14).
- Whether delay propagation through a shared object is real in any
  concrete factory setting — this requires occupancy/queue-level data
  neither dataset we have used contains.
- Whether any of this changes an actual factory decision Chris's customer
  would make.

## 12. Research Limitations

- This is one company's (anonymized) purchase-to-pay process, sampled to
  1,011 of 76,349 available purchase orders for tractability. Findings are
  not claimed to generalize to other companies, other processes, or the
  full (unsampled) dataset without re-verification.
- No shop-floor production data (machines, operations) was analyzed in
  this restart — that remains covered only by the (dataset-limited) Gate
  4 v1 experiment, which itself found nothing decisive there either.
- No material or quality object was available to test — the most
  transformer-relevant object types (material shortage, quality defect)
  remain completely untested across both Gate 4 attempts.
- The evidence-grounded thresholds (20%/70% coverage bands) are the same
  provisional, non-statistically-validated thresholds carried from Gate 2
  — restated here, not re-derived.
- Gate 1's strategic capability classification is a judgment call based on
  what this one dataset let us exercise; a different dataset could shift
  some rows between "demonstrated" and "partially demonstrated."

## 13. Questions for Chris

### Research finding: 99.1% of sampled purchase orders sit in one connected component, reachable only through a small number of shared vendors/resources.
**Why it matters:** if real factory or procurement data behaves the same way, a single shared supplier or shared production resource could tie together nearly an entire order book — meaning per-order diagnostics could systematically miss a shared root cause.
**Question for Chris:** Does the transformer manufacturer's production or procurement data have a similarly small number of high-degree shared resources (specific machines, subcontractors, critical suppliers) that touch a large fraction of orders, or is their production more siloed/cellular?

### Research finding: process-mining conformance/fitness barely moved (0.9968→0.9963) even as real evidence coverage collapsed (95.6%→67.1%) — the second time we've shown this, on two unrelated datasets.
**Why it matters:** any LENSIPS factory-intelligence capability cannot rely on a standard conformance score as a "is this data trustworthy" signal.
**Question for Chris:** What evidence-completeness signal would the customer actually trust or act on, if not a standard process-mining conformance/fitness score?

### Research finding: only 32.1% of vendors had enough transaction volume (≥5 items) for a statistically meaningful cycle-time estimate.
**Why it matters:** any per-supplier or per-machine benchmarking will be low-confidence for the long tail of low-volume relationships — plausibly also true for a transformer manufacturer's many low-volume specialty subcontractors or custom designs.
**Question for Chris:** Does the customer expect findings for low-volume or one-off production paths (custom transformer designs, rare subcontractors), and what confidence bar would they accept for those?

### Research finding: this dataset, despite coming from a real manufacturer, is a procurement/back-office process, not shop-floor production — and our earlier (Gate 4 v1) shop-floor dataset had no material/supplier objects. No public dataset combining both was found.
**Why it matters:** we have evidence for the object-centric hypothesis in procurement and (separately, weakly) in shop-floor process behaviour, but never together, and never for material or quality objects at all.
**Question for Chris:** Is the customer's actual pain point closer to procurement/supply-chain relationship intelligence (vendor/material delays) or shop-floor production/operations intelligence (machine, operation, cycle time), or genuinely both — since the data sources and object types needed differ substantially?

### Research finding: even this well-documented real dataset had no Material or Quality object distinct from the order/item level.
**Why it matters:** the material-shortage and quality-propagation questions in the original Gate 4 brief — plausibly the most relevant to transformer manufacturing (e.g. CRGO steel or copper supply issues) — remain completely untested by either Gate 4 attempt.
**Question for Chris:** Can the customer provide, or confirm the existence of, linked material-lot/BOM and quality-inspection records — not just order and vendor-level records?

### Research finding: producing this experiment required subsampling a 1.5 GB, 1.6M-event real log down to 20,011 events for tractability.
**Why it matters:** real customer data volumes could be materially larger than anything analyzed in either Gate 4 attempt; ingestion and scaling are real, not hypothetical, questions.
**Question for Chris:** What data volume and history depth should we expect from the customer (events per month, years of history), and would the customer expect analysis at full scale or on a rolling window?

### Research finding: of the object-centric analyses attempted, roughly half (the centrality ranking) were reproducible with an ordinary pandas group-by; only the connected-component/propagation-relevant analysis was genuinely OCEL-required.
**Why it matters:** this bounds how much of an "object-centric" pitch is really "compare across orders," which conventional BI can already do, versus a genuine multi-object/graph capability that needs real investment.
**Question for Chris:** Is the customer's interest closer to the "compare across orders" capability (fast, low investment) or a genuine multi-object propagation/connectivity model (higher investment, still unproven whether it changes a decision)?

### Research finding: benchmarking in this experiment was internal-relative only (vendor-vs-vendor within the same sample) — never peer-factory or engineering-standard.
**Why it matters:** LENSIPS has no established evidence source for peer-factory, regional-industry, or IEC/IEEE-standard benchmarking; claiming any of those without one would be unsupported.
**Question for Chris:** Which benchmarking type does the customer actually expect — their own historical performance, peer-factory comparison, regional-industry benchmarks, or engineering/design standards?

### Research finding: this whole restart was necessary because no repeatable pattern has yet been shown across more than one real dataset for the SAME object types (shop floor vs procurement differ).
**Why it matters:** whether this is worth building as a reusable LENSIPS capability, versus a one-off analysis, depends heavily on repeatability across customers and processes.
**Question for Chris:** Is this a requirement specific to one transformer manufacturer, a recurring need across multiple transformer manufacturers, or potentially applicable to engineered manufacturing more broadly?

### Research finding: nothing in this research establishes a commercial packaging.
**Why it matters:** the technical investment required differs a lot between a one-off assessment and a recurring product capability.
**Question for Chris:** What commercial model does the customer actually expect — a paid one-off factory assessment, a consulting/data-analysis engagement, a LENSIPS capability/module, a recurring subscription, or bespoke development?

## 14. Investment Decision Points

Further investment in an object-centric/multi-object LENSIPS capability
looks justified only if **most** of the following hold, based on Chris's
answers to §13:

1. The customer can provide (or already has) data with genuine,
   independently-identified object types beyond order/case — material,
   supplier, machine, or quality-inspection records that actually link to
   the same events, not just descriptive attributes on a single case.
2. The customer's problem plausibly involves a shared-resource or
   shared-supplier structure (§7.2's connected-component pattern), not
   purely independent, siloed orders — otherwise object-centric modelling
   adds complexity without the payoff this experiment demonstrated.
3. The desired output is diagnosis/relationship-intelligence (where the
   connected-component-style finding is relevant), not a benchmarking
   claim that would require an external evidence source LENSIPS does not
   have (§13, benchmarking-type question).
4. This need is repeatable across more than one customer/engagement, or
   the customer/LMNAs explicitly wants a one-off engagement priced and
   scoped as such.
5. The customer accepts that low-volume/rare production paths will
   produce low-confidence findings by design (§6 Q1, §13), rather than
   expecting uniform confidence everywhere.

If most of these are unresolved or answered negatively, the technically
honest recommendation is to scope any further work as a small, targeted,
customer-data-specific pilot rather than a general LENSIPS capability.

## 15. Recommendation for Next Research Step

**Do not start Gate 5 or any production implementation.** Per the
research brief, this reconnaissance is complete once this report and its
supporting experiment exist.

The single highest-leverage next step is **not more public-dataset
research** — we have now tested the hypothesis on two structurally
different real datasets (shop-floor machine shop, back-office procurement)
and gotten a consistent methodological result (evidence-gating discipline
transfers; object-centric value is real but narrower than "OCEL helps
everywhere," and depends on data richness this experiment could not
manufacture). The next step is **Chris's answers to §13**, specifically
the customer-problem and data-availability questions, since those
determine which of this report's demonstrated capabilities (Gate 1 table,
§4) are actually relevant to the customer LMNAs is discussing, and whether
a transformer-manufacturing pilot would even have the object types
(material, quality) that both Gate 4 attempts found were unavailable in
public data.

---

## Completion Test

**Dataset:** Does this dataset genuinely contain the relationships
required to test object-centric manufacturing intelligence? — **Yes**,
for order/vendor/resource relationships (verified via
`pm4py.discover_objects_graph`/`discover_ocdfg` running natively against
it, §7.2). **No**, for material or quality relationships — this dataset,
like the Gate 4 v1 dataset, does not contain those object types (§3, §12).

**PM4Py:** Did we actually use PM4Py process-mining capabilities, and what
did they contribute? — **Yes**: `ocel_flattening`,
`discover_petri_net_inductive`, `fitness_token_based_replay`,
`discover_performance_dfg` for the case-centric baseline and the
degradation re-test; `discover_ocdfg` and `discover_objects_graph` for the
object-centric analysis. Full accounting with the "would pandas suffice"
thought experiment for each finding is in §8.

**OCEL:** Did we actually construct and analyse an object-centric event
log, rather than merely describe one? — **Yes**: the sample is a real
subset of a genuine OCEL 1.0 log (§16 of the dataset selection report),
loaded with `pm4py.read_ocel`, and analysed with OCEL-native discovery
functions, not a pandas table reshaped to look like one.

**Incremental value:** What finding can OCEL/object-centric analysis
reveal that case-centric analysis cannot, if any? — **The connected-
component finding (§7.2)**: 99.1% of sampled orders are transitively
linked through shared vendors/resources, invisible to a case-centric
flattened trace by construction. Some other object-centric-flavoured
analyses (centrality ranking) added convenience, not unique capability
(§8) — reported honestly rather than folded into the headline claim.

**Evidence:** Can we determine whether those findings are adequately
supported by the available evidence? — **Yes for the connected-component
finding** (direct graph computation from real event-object links, no
inference gap). **No for delay propagation** (§6 Q3) — deliberately
withheld, since the necessary occupancy/queue evidence does not exist in
this dataset.

**Manufacturing relevance:** Which findings plausibly matter to a
transformer manufacturer? — The connected-component/shared-critical-
resource pattern (§10) is the most plausibly transferable, conceptually,
to a transformer manufacturer's supplier/subcontractor relationships. It
has not been demonstrated on any transformer or shop-floor dataset.

**Customer dependency:** Which remaining questions cannot be answered
without Chris/customer information? — All eleven questions in §13:
customer problem, data availability and granularity, benchmarking type,
commercial model, and repeatability across customers.

**Investment:** What would we need to learn from Chris before investing
further? — See §14's five conditions, derived directly from what this
experiment could and could not demonstrate.
