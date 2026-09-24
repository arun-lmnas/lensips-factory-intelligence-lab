# LENSIPS Gap Analysis — Gate 1

This is the most important report of Gate 1. It lets the evidence gathered
in [REFERENCE_ARCHITECTURE.md](REFERENCE_ARCHITECTURE.md),
[REFERENCE_COMPARISON.md](REFERENCE_COMPARISON.md), and
[ENTERPRISE_EVIDENCE.md](ENTERPRISE_EVIDENCE.md) determine the conclusions
below, rather than forcing a predetermined architecture.

---

## 1. Already solved by existing platforms — LENSIPS should probably NOT reinvent

- **Case-centric process discovery, conformance checking, and performance
  analysis on ERP-style event data.** This is mature, available for free in
  PM4Py (verified installable and importable in Gate 0), and is the core
  product of SAP Signavio and Celonis. Reimplementing directly-follows-graph
  discovery, token-based replay, or basic conformance checking would be
  pure duplication of proven algorithms.
- **Generic enterprise-scale process orchestration/automation** ("trigger a
  workflow when a bottleneck is found"). Both Signavio and Celonis already
  build this, and it is not process-mining-specific — it's workflow
  automation, out of scope for a factory-intelligence research question.
- **General-purpose MES functionality** (scheduling, dispatching, quality
  inspection UI, operator dashboards). SAP Digital Manufacturing and
  numerous MES vendors already do this; it is Layer 1 (evidence source),
  not something LENSIPS should build as a factory-intelligence capability.
- **The OCEL 2.x data standard itself**, and its reference implementation in
  PM4Py. Building a competing object-centric event format would contradict
  the repository's own principle of reusing proven foundations, and there
  is no evidence gap that would justify it.

## 2. Solved but too enterprise-heavy — worth simplifying for medium manufacturers

- **Celonis-style "Execution Management System."** The evidence (§14 of
  ENTERPRISE_EVIDENCE.md) is unambiguous that this class of platform is
  priced and implemented for large enterprises ($150K–$250K+/yr license,
  $120K–$500K+ implementation, ongoing CoE staffing). A medium transformer
  manufacturer will not buy this, and does not need its full breadth
  (cross-functional orchestration across dozens of processes) to get value
  from process visibility into one or two high-value processes (e.g. HV/LV
  winding, order-to-delivery).
- **Full object-centric process mining as a default modeling approach.**
  The evidence (REFERENCE_COMPARISON.md, "Object-centric vs. case-centric")
  shows OCPM adds real complexity, computational cost, and interpretation
  difficulty, and its production use is still concentrated in supply chain.
  A simplified version — object-centric modeling applied narrowly to the
  specific sub-problems where it earns its cost (e.g. linking one
  transformer order to its core/windings/tank/tests) rather than
  object-centric-by-default across the whole factory — is the SME-sized
  version of this capability.
- **Full digital-twin / discrete-event simulation of an entire factory.**
  The evidence (ENTERPRISE_EVIDENCE.md #10) shows this requires expertise
  and setup effort that is a documented barrier for SMEs specifically. A
  simplified version — targeted simulation of one bottleneck process step
  or one what-if question (e.g. "what if HV winding had one more shift?")
  rather than a full-factory state model — is far more tractable, and does
  not require adopting a full digital-twin platform like OFacT wholesale.
- **Manufacturing Execution System-grade real-time shop-floor data
  capture** (à la SAP Digital Manufacturing Cloud). Medium manufacturers
  may not have this. LENSIPS's factory-intelligence capability should be
  designed to degrade gracefully with partial/coarse shop-floor data
  (milestone timestamps only) rather than assume MES-grade event streams —
  this is directly supported by evidence #12 in ENTERPRISE_EVIDENCE.md.

## 3. Genuine gaps / opportunities — where there appears to be meaningful room for LENSIPS

- **An evidence/data-reliability layer that is a first-class, customer-facing
  output, not an internal preprocessing step.** No platform surveyed
  (Signavio, Celonis, OFacT) was found to publish a mature, customer-facing
  confidence-scoring/data-quality-reporting capability — this is flagged
  `INSUFFICIENT EVIDENCE` in ENTERPRISE_EVIDENCE.md #17 and REFERENCE_
  ARCHITECTURE.md §8. Given that this lab's README already identifies data
  reliability as a first-class business concern, and that the academic
  literature confirms SME manufacturing data is commonly sparse (evidence
  #12), a LENSIPS capability that explicitly reports "what we know, what we
  inferred, what's missing, and how confident we are" appears to be a real,
  evidenced gap rather than a hypothesis. This is squarely inside LENSIPS's
  existing ERP-native position — LENSIPS already sits inside the data
  source, unlike Signavio/Celonis which connect externally.
- **A right-sized, ERP-embedded process/factory intelligence capability for
  medium manufacturers**, at a cost and implementation-effort point far
  below Celonis/Signavio. Because LENSIPS is already the ERP for these
  customers, it can reuse master data and process context that an external
  process-mining tool would otherwise have to extract and reconcile from
  scratch — a structural advantage no platform surveyed has for this
  customer segment specifically.
- **Narrow, evidence-grounded engineering-intelligence assistance** —
  *not* "is this IEC compliant" (unsupported by any platform, and
  contradicted by how IEC 60076 compliance actually works — see
  REFERENCE_ARCHITECTURE.md §7) but the more modest and evidenced-feasible
  question: "is this order's actual time/cost/resource consumption
  significantly different from this factory's own historical population
  for comparable orders?" This is an operational-analytics /
  benchmarking-against-own-history capability, not a standards-compliance
  capability, and it does not require IEC/IEEE domain modeling to be useful
  — it requires reliable historical data and honest confidence reporting.
- **A narrowly scoped object-centric model for the transformer
  order → core/windings/tank/tests structure specifically**, applied where
  it demonstrably helps (cross-checking whether a specific quality issue
  traces to a specific winding batch/machine) rather than as the default
  representation for every process.

## 4. Hard research problems — require experimentation before committing

- **Can a factory-intelligence capability produce useful findings from the
  kind of sparse, milestone-only manufacturing event data that evidence #12
  says is typical of SME manufacturers** — or does it need MES-grade data
  the target customers don't have? This is the single most important
  uncertainty carried into the "Proposed Next Gate" section of
  [CAPABILITY_PORTFOLIO.md](CAPABILITY_PORTFOLIO.md).
- **Can an LLM reasoning layer reliably stay evidence-grounded** (not
  calculate metrics itself, not silently override missing evidence with
  plausible-sounding inference) given the documented, measured
  hallucination risk in process-mining-adjacent LLM tasks (evidence #15)?
  No manufacturing-specific study of this was found — it needs to be tested
  directly, with a validation harness, before any LENSIPS AI-reasoning
  capability is trusted with customer-facing conclusions.
- **Does object-centric modeling of the transformer order structure
  actually surface findings that case-centric modeling misses**, for real
  (or realistic synthetic) transformer manufacturing data — or is the
  added complexity not worth it at LENSIPS's target customer scale? This
  needs a small, direct experiment (see Proposed Next Gate), not an
  architectural assumption either way.
- **Whether OFacT (or any similar open digital-twin foundation) is mature
  enough to build on**, beyond the packaging/import-level verification done
  in Gate 0. This requires actually exercising its simulation/analytics
  code on a toy scenario before any simulation capability is planned around
  it.
- **What data actually exists inside a real medium transformer
  manufacturer's systems** (per README §1's original trigger — the Italian
  transformer manufacturer). All the SME-manufacturing evidence gathered in
  this gate is about SMMCs (small/medium manufacturing companies) in
  general, not this specific company or even the transformer sub-sector
  specifically — that remains `INSUFFICIENT EVIDENCE` until direct
  investigation.

## 5. Things LENSIPS should explicitly NOT attempt initially

- **Do not attempt to determine IEC/IEEE standards compliance from process
  or ERP data.** The evidence is clear that compliance is a test-outcome
  determination, not a process-mining inference. At most, LENSIPS could
  flag "this process appears inconsistent with our historical/benchmark
  population" (an operational-analytics statement) — never "this is/isn't
  IEC compliant" (a standards-compliance statement) without direct access
  to test data and standards text, which is out of scope for the
  foreseeable roadmap.
- **Do not attempt to build or adopt a full-factory digital twin.** The
  evidence on SME digital-twin adoption barriers (evidence #10) and the
  immaturity of OFacT as verified in Gate 0 both argue against this. A
  full digital twin is a "hard research problem" candidate at most, not a
  near-term capability.
- **Do not make object-centric modeling the default representation for all
  LENSIPS process data.** The complexity/interpretability cost documented
  in REFERENCE_COMPARISON.md is real; apply it narrowly, only where a
  concrete multi-object problem justifies it.
- **Do not let an LLM calculate operational metrics from raw data**, per
  the README's existing principle — this is now further reinforced by
  documented hallucination risk (evidence #15), not just a stylistic
  preference.
- **Do not attempt to compete with Celonis/SAP Signavio on general-purpose,
  cross-enterprise process orchestration.** LENSIPS's differentiation is
  being embedded in the ERP for a specific customer segment with a
  specific manufacturing focus, not breadth of process coverage.
- **Do not build a general-purpose event-log extraction/ETL framework for
  arbitrary third-party ERPs.** LENSIPS already has direct, native access
  to its own data model — the "extract event logs from an external SAP
  system" problem that Signavio/Celonis solve does not apply to LENSIPS's
  own data in the same way, and solving it for arbitrary external systems
  is a different (and much larger) problem than the one motivating this
  research.
