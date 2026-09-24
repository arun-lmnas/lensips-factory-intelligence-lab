# Enterprise Evidence Register — Gate 1

For each capability/claim: capability, organization/platform, customer/use
case, industry, evidence type, source, what the evidence actually proves,
what it does NOT prove, and confidence level.

Confidence levels used throughout this Gate 1 research:

- `PROVEN` — credible production evidence (independently verifiable, or
  strong convergent evidence from multiple independent sources)
- `DEMONSTRATED` — working industrial/research demonstration, but evidence
  is vendor- or partner-published and not independently audited
- `EMERGING` — credible but limited evidence (e.g. single academic case
  study, small sample)
- `HYPOTHESIS` — plausible but insufficient evidence
- `INSUFFICIENT EVIDENCE` — explicitly flagged where the research could not
  establish a claim either way

---

## 1. Process mining reduces manufacturing lead time / cycle time

- **Platform**: Celonis
- **Customer/use case**: unnamed automotive manufacturer
- **Claim**: 30% lead-time reduction, 20% operational cost reduction
- **Source**: aggregated case-study summary,
  https://www.ciklum.com/blog/5-ways-celonis-process-mining-boosts-manufacturing-efficiency/
- **What it proves**: process mining *can* surface lead-time reduction
  opportunities that get acted on, in at least one attributed case.
- **What it does NOT prove**: it does not establish a generalizable
  percentage improvement for other manufacturers, does not disclose
  baseline data quality, and is not independently audited.
- **Confidence**: `DEMONSTRATED`

## 2. Process mining improves shop-floor schedule visibility

- **Platform**: Celonis
- **Customer/use case**: Siemens (inventory/production management)
- **Claim**: factories moved from twice-daily printed production schedules
  to ~15-minute real-time on-time readouts; direct-material order approvers
  halved
- **Source**: https://www.celonis.com/customer/siemens-inventory-management/
- **What it proves**: a named, large industrial company (Siemens) publicly
  attributes a specific operational change (printed→real-time schedules) to
  Celonis.
- **What it does NOT prove**: no independent third-party audit found; no
  quantified business outcome (e.g. revenue, on-time-delivery %) beyond the
  process-change description itself.
- **Confidence**: `DEMONSTRATED`

## 3. Process mining improves supplier PO confirmation rates

- **Platform**: Celonis
- **Customer/use case**: Molex, supply chain reliability
- **Claim**: supplier PO confirmation rate rose from 30% to 90%
- **Source**: https://www.molex.com/en-us/about/case-studies/celonis-process-mining-for-supply-chain-reliability
- **What it proves**: a named company reports a large, specific, and
  plausible metric improvement.
- **What it does NOT prove**: methodology for measuring the 30%/90% figures
  is not published; not independently audited.
- **Confidence**: `DEMONSTRATED`

## 4. SAP Signavio reduces maintenance work-order processing time

- **Platform**: SAP Signavio ("Maintenance Excellence" solution)
- **Customer/use case**: unnamed manufacturing company
- **Claim**: 30% reduction in work-order processing time, 10% increase in
  equipment uptime
- **Source**: https://www.ennuviz.com/blogs/unlocking-the-power-of-process-intelligence-in-manufacturing-with-sap-signavio
- **What it proves**: a partner-published account of a specific
  manufacturing maintenance improvement attributed to Signavio.
- **What it does NOT prove**: customer is unnamed, so the claim cannot be
  independently traced or verified; partner (not SAP or the customer
  directly) is the publisher.
- **Confidence**: `EMERGING`

## 5. Process mining reveals inconsistent process execution despite a "working" ERP

- **Platform**: not specified (QPR-published case)
- **Customer/use case**: unnamed global manufacturer
- **Claim**: ERP was functioning as intended, but only 40% of orders
  followed the defined standard process; process mining helped the company
  avoid an unnecessary €3M ERP re-investment
- **Source**: https://www.qpr.com/blog/process-mining-manufacturing-case-study-erp-optimization
- **What it proves**: a documented example of process mining correctly
  diagnosing a process-execution problem as distinct from a
  system/technology problem — directly relevant to the "don't blindly trust
  ERP data, and don't assume the system is the problem" principle in this
  lab's README.
- **What it does NOT prove**: vendor-published, customer unnamed; no
  independent verification of the €3M figure.
- **Confidence**: `EMERGING`

## 6. Process mining identifies delays/bottlenecks in manufacturing via MES+ERP event logs

- **Platform**: academic (Heuristic mining algorithm), and a separate
  peer-reviewed methodology paper
- **Customer/use case**: Make-To-Order manufacturing case; general
  MES/ERP bottleneck-identification methodology
- **Claim**: process discovery + conformance + bottleneck analysis
  correctly located activities with abnormally long lead time in a
  three-phase manufacturing process (preprocessing → main manufacturing →
  inspection)
- **Source**: https://researchgate.net/publication/271910986 ;
  https://www.acadlore.com/article/JII/2025_3_2/jii030202
- **What it proves**: peer-reviewed/academic evidence that process mining
  techniques (discovery, conformance, performance/bottleneck analysis) work
  methodologically on manufacturing event data reconstructed from MES/ERP.
- **What it does NOT prove**: academic case studies are typically smaller
  scale and more controlled than live enterprise deployments; does not by
  itself establish ROI at typical medium-manufacturer scale.
- **Confidence**: `PROVEN` (methodology), `EMERGING` (real-world ROI)

## 7. Explainable ML + process mining predicts deadline violation in steel manufacturing

- **Platform**: academic framework (event-log readiness assessment +
  process mining + predictive monitoring + explainable ML + domain
  validation)
- **Customer/use case**: an Ecuadorian steel manufacturer
- **Claim**: process discovery found rework, accumulated waiting, route
  deviations, and resource congestion positively associated with deadline
  violation; a process-aware ridge logistic model achieved PR-AUC 0.839 vs.
  0.419 for a static (non-process-aware) baseline
- **Source**: https://www.mdpi.com/2078-2489/17/9/877 (peer-reviewed,
  Information journal)
- **What it proves**: peer-reviewed evidence, in a real manufacturing
  setting (steel), that process-aware modeling substantially outperforms
  naive/static modeling for predicting a real operational outcome
  (deadline violation), and that the underlying process patterns
  (rework, waiting, congestion) are interpretable and match intuition.
- **What it does NOT prove**: single company/industry; does not generalize
  automatically to transformer manufacturing or other discrete
  manufacturing without adaptation.
- **Confidence**: `PROVEN` (this is the strongest single piece of
  peer-reviewed manufacturing evidence found in this research)

## 8. PM4Py supports OCEL 2.0 object-centric discovery and conformance

- **Platform**: PM4Py (open source)
- **Claim**: full OCEL 2.0 support; object-centric process discovery (OCPN,
  OC-DFG, OC-BPMN) and object-centric conformance checking via Petri nets,
  DFGs and object graphs
- **Source**: PM4Py paper, ScienceDirect,
  https://www.sciencedirect.com/science/article/pii/S2665963823000933 —
  peer-reviewed software paper
- **What it proves**: the specific technical capability exists in an
  open-source, no-license-cost tool, independent of any commercial vendor's
  claims. This was also directly, independently confirmed in this lab's
  Gate 0 (`pm4py.objects.ocel.obj.OCEL` imports and instantiates — see
  [BOOTSTRAP_REPORT.md](BOOTSTRAP_REPORT.md)), though Gate 0 only verified
  the import, not discovery/conformance functionality on real data.
- **What it does NOT prove**: does not prove PM4Py's OCEL implementation
  performs adequately at industrial data volumes, or that discovered
  object-centric models are interpretable by non-experts (see
  REFERENCE_COMPARISON.md's OCPM limitations).
- **Confidence**: `PROVEN` (capability exists), `INSUFFICIENT EVIDENCE`
  (performance/usability at scale — not tested in this gate)

## 9. Object-centric process mining adoption remains limited in practice

- **Platform**: cross-industry (systematic literature review)
- **Claim**: despite academic promise, OCPM adoption "remains limited,"
  concentrated mainly in supply chain management use cases; lacks
  standardized cross-object KPIs; large/heterogeneous OCEL logs tend toward
  "spaghetti" models that are hard to interpret
- **Source**: arXiv:2311.08795, "Advancements and Challenges in
  Object-Centric Process Mining: A Systematic Literature Review,"
  https://arxiv.org/abs/2311.08795
- **What it proves**: peer-reviewed literature review evidence (not a
  single anecdote) that OCPM's real-world footprint is currently narrow.
- **What it does NOT prove**: does not prove OCPM cannot work for
  transformer manufacturing specifically — it establishes that this would
  be a relatively novel application, not a well-trodden path.
- **Confidence**: `PROVEN` (as a statement about current adoption breadth)

## 10. Discrete-event simulation / digital twin adoption in SMEs faces high barriers

- **Platform**: cross-industry (academic + industry commentary)
- **Claim**: SMEs face high setup costs, scarce specialized expertise,
  fragmented source data, and substantial effort to build/validate
  simulation interfaces
- **Source**: https://www.tandfonline.com/doi/full/10.1080/17477778.2026.2628033 ;
  https://www.tttech.com/digital-twin-barriers
- **What it proves**: converging evidence from an academic source and an
  industry source that digital-twin/DES adoption is genuinely harder for
  SMEs than for large enterprises, not just a matter of preference.
- **What it does NOT prove**: does not quantify the barrier in a way that
  is directly transferable to a cost/effort estimate for LENSIPS.
- **Confidence**: `PROVEN` (as a directional finding)

## 11. OFacT / OpenFactoryTwin — early-stage, unaudited beyond what Gate 0 verified

- **Platform**: OFacT (Fraunhofer ISST + partners)
- **Claim (vendor/publisher)**: integrates ERP/WMS/sensor data into a
  single state model; supports what-if simulation ("OFacT Sim") and derived
  cost/performance analytics ("OFacT Analytics")
- **Source**: https://www.isst.fraunhofer.de/en/departments/industrial-manufacturing/technologies/OFacT.html ;
  https://zenodo.org/records/13734211
- **What was independently verified (Gate 0, this repository)**: the
  `0.1.0` tag can be cloned and `import ofact` succeeds as a namespace
  package after installing its declared dependencies; the packaging
  manifest (`pyproject.toml`) is broken (`pip install -e` fails) at that
  tag; no OFacT simulation or analytics functionality was exercised.
- **What it does NOT prove**: does not establish that OFacT's simulation or
  analytics capabilities work as described, at any release. This is an
  open item for a later gate, not resolved here.
- **Confidence**: `HYPOTHESIS` (capability as marketed), `PROVEN` (narrowly,
  for the specific import/packaging facts verified directly in Gate 0)

## 12. Medium manufacturers commonly produce manufacturing event data with large gaps

- **Platform**: academic (focus group study across small/medium
  manufacturing companies, SMMC)
- **Claim**: "the status quo in SMMC is that logging is part of the
  business logic and data-centric, with selected milestones in production
  producing a data dump with a timestamp, while most process steps in the
  manufacturing domain just produce no events at all"
- **Source**: Stertz, Mangler, Scheibel, Rinderle-Ma, "Expectations vs.
  Experiences – Process Mining in Small and Medium Sized Manufacturing
  Companies," BPM Forum 2021,
  https://link.springer.com/chapter/10.1007/978-3-030-85440-9_12
- **What it proves**: direct, peer-reviewed evidence (not inference) that
  incomplete event data is the *norm*, not the exception, in the exact
  customer segment (small/medium manufacturers) that this lab is targeting.
- **What it does NOT prove**: does not establish this is true of the
  specific Italian transformer manufacturer mentioned in
  [README.md](../README.md) §1 — that would need direct investigation.
- **Confidence**: `PROVEN` (as a general finding about SMMC data
  readiness) — this is treated as a load-bearing fact for the
  Evidence/Data-Reliability-Layer conclusion in
  [LENSIPS_GAP_ANALYSIS.md](LENSIPS_GAP_ANALYSIS.md).

## 13. Process mining adoption in SMEs is constrained mainly by resources and process maturity, not by lack of value

- **Platform**: academic (SME-specific process mining literature)
- **Claim**: "the main barriers are (1) limited resources and (2) lower
  process maturity"; a dedicated methodology (PROMISE) has been proposed
  and evaluated via two industrial case studies plus expert review, found
  "feasible in SME settings"
- **Source**: https://link.springer.com/chapter/10.1007/978-3-031-16103-2_11 ;
  https://www.researchgate.net/publication/405285806
- **What it proves**: peer-reviewed evidence that SME process mining is
  feasible with the right methodology, and that the barrier is
  organizational/resource-based rather than a fundamental technical
  limitation.
- **What it does NOT prove**: PROMISE has only been validated on two
  industrial case studies; not proof of broad generalizability.
- **Confidence**: `EMERGING`

## 14. Celonis licensing/implementation cost is prohibitive for a medium manufacturer without adaptation

- **Platform**: Celonis
- **Claim**: enterprise license $150K–$250K+/year; implementation services
  $120K–$500K+ one-time; ongoing CoE/consulting $200K–$700K/year; a
  composite enterprise customer's Year-1 cost was $1.26M, scaling to $5.25M
  by Year 3
- **Source**: https://vendorbenchmark.com/blog/process-mining-platform-pricing-benchmark ;
  corroborated directionally by https://www.processmaker.com/blog/how-much-does-process-mining-cost-2024-pricing-guide/
- **What it proves**: converging market-research evidence (not a single
  source) that Celonis-class tooling is priced for large enterprises.
- **What it does NOT prove**: does not reflect any SME-specific tier
  Celonis may or may not offer — no such tier was found in the sources
  reviewed (`INSUFFICIENT EVIDENCE` on whether one exists).
- **Confidence**: `PROVEN` (as a statement about typical enterprise
  pricing), `INSUFFICIENT EVIDENCE` (on SME-tier options)

## 15. LLM-based process/factory diagnosis carries a documented, measured hallucination risk

- **Platform**: academic (LLM + process mining intersection)
- **Claim**: a taxonomy of process-mining-specific LLM hallucinations (4
  families, 12 sub-types) has been developed and benchmarked; "higher
  benchmark scores align with fewer hallucinations... hallucination
  families tend to co-occur rather than trade off"; a related study shows
  "knowledge-driven hallucination" where a model's prior knowledge
  overrides explicit source evidence in process-modeling tasks
- **Source**: https://www.techrxiv.org/doi/full/10.36227/techrxiv.175977705.50503509/v1 ;
  https://arxiv.org/pdf/2509.15336
- **What it proves**: this is a measured, named, peer-reviewed-adjacent
  phenomenon directly relevant to the README's requirement that "the LLM
  must NOT be responsible for calculating operational metrics from raw
  data."
- **What it does NOT prove**: no manufacturing- or transformer-specific
  study of this risk was found — the risk is general to LLM+process-mining,
  not proven in this specific domain.
- **Confidence**: `PROVEN` (general phenomenon), `HYPOTHESIS` (specific
  manifestation in a factory-intelligence context)

## 16. IEC 60076 compliance is established via test results, not process data

- **Platform**: N/A — standards research
- **Claim**: "Transformer compliance is demonstrated through objective test
  results rather than theoretical design intent... IEC 60076 provides
  detailed and test-oriented specifications that directly guide transformer
  design validation, manufacturing processes, and acceptance procedures"
- **Source**: https://electrical-engineering-portal.com/guide-to-transformer-specification-compliance-iec-60076-part-1
- **What it proves**: a credible technical-publication source confirms
  that IEC 60076 compliance is fundamentally an outcome/test-based
  determination.
- **What it does NOT prove**: this single secondary source is not the IEC
  standard text itself (which was not accessed in this research); the
  finding should be treated as directionally reliable but not a substitute
  for reading IEC 60076 directly before making product claims.
- **Confidence**: `EMERGING` — sufficient to shape the architecture
  conclusion in REFERENCE_ARCHITECTURE.md §7, insufficient to make specific
  compliance-checking product claims.

## 17. Manufacturing data is commonly fragmented across MES/ERP/CMMS/quality/historian/spreadsheets

- **Platform**: industry commentary (not peer-reviewed)
- **Claim**: "more than 83% of manufacturers struggle with slow root cause
  analysis because operational data is fragmented across MES, ERP, CMMS,
  quality tools, historians, and spreadsheets"
- **Source**: https://www.evoketechnologies.com/blog/business-blogs/manufacturing-data-lakehouse-strategy/
- **What it proves**: directionally consistent with the SMMC academic
  finding above (#12), but this specific 83% figure is from an industry
  blog, not an audited survey — the underlying survey/methodology was not
  independently traced.
- **What it does NOT prove**: the exact "83%" figure should not be quoted
  as an audited statistic; treat as a plausibility signal only.
- **Confidence**: `EMERGING` (directional finding), the numeric statistic
  itself is `INSUFFICIENT EVIDENCE` to cite as fact.

---

## Explicit `INSUFFICIENT EVIDENCE` findings from this gate

- Whether Celonis or SAP Signavio have a mature, customer-facing evidence
  confidence/data-quality scoring layer (as opposed to general "clean
  data" marketing language).
- Whether any commercial platform can credibly answer "is this process IEC
  compliant?" — no such product capability was found.
- Whether OFacT's simulation/analytics capabilities work as described
  beyond the packaging/import facts verified in Gate 0.
- Whether LLM hallucination risk in a factory-diagnosis context specifically
  (as opposed to general process mining) has been studied.
- Whether any surveyed platform publishes a reproducible, audited ROI case
  study for a transformer manufacturer specifically (none was found in this
  research).
