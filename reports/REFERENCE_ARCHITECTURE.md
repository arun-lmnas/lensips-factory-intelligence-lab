# Reference Architecture Study — Gate 1

Scope: describe the architectures found in credible enterprise process
intelligence, factory intelligence, and digital-twin/simulation solutions,
and show where each capability sits relative to ERP/MES/QMS/IoT. This
report does **not** design LENSIPS. See
[LENSIPS_GAP_ANALYSIS.md](LENSIPS_GAP_ANALYSIS.md) and
[CAPABILITY_PORTFOLIO.md](CAPABILITY_PORTFOLIO.md) for the resulting
LENSIPS-specific conclusions.

All claims below are sourced. Where a claim is a vendor statement rather
than independently verified fact, it is labeled `[VENDOR CLAIM]`.

---

## 1. Layered view of the space

Across every architecture studied, five broadly separable layers recur,
though vendors bundle them differently:

```
Layer 5:  AI / reasoning over structured findings
Layer 4:  Simulation / digital twin ("what if")
Layer 3:  Analytics (conformance, bottlenecks, root cause, benchmarking)
Layer 2:  Process/object model (case-centric or object-centric)
Layer 1:  Evidence ingestion & event extraction (ERP / MES / QMS / IoT)
```

No platform surveyed treats Layer 1 (data extraction and reliability) as an
afterthought — it is consistently described as the hardest and most
resource-intensive part of a real deployment (see §6 and
[ENTERPRISE_EVIDENCE.md](ENTERPRISE_EVIDENCE.md)).

---

## 2. SAP Signavio Process Intelligence

**Position relative to ERP/MES**: sits above SAP ERP (S/4HANA, ECC) and
non-SAP systems, connecting directly to source systems via extractors.

**Architecture, as documented** [SOURCE: SAP Signavio product page,
https://www.signavio.com/products/process-intelligence/ ; SAP Help Portal,
https://help.sap.com/docs/signavio-process-intelligence/user-guide/process-analysis-and-mining]:

- **Data connection layer**: "automated, advanced process data extraction"
  connects to source systems and produces continuous updates, `[VENDOR
  CLAIM]` typically "within hours."
- **Process model layer**: builds an event-log-based process representation
  from extracted data; supports investigations (ad hoc analysis) and
  dashboards (recurring monitoring).
- **Analytics layer**: process mining/discovery, conformance against a
  reference process, performance analysis.
- **Action layer**: findings can trigger notifications, workflows, or bots
  via SAP Build Process Automation or third-party automation — i.e.
  Signavio explicitly separates *finding* a problem from *acting* on it.
- **AI**: "embedded AI" is mentioned generically for faster analysis
  `[VENDOR CLAIM]`; no independent technical detail on the reasoning
  architecture was found in the sources reviewed.

**Manufacturing-specific case evidence found**: a "Maintenance Excellence"
solution powered by SAP Signavio reduced work-order processing time by
30% and increased equipment uptime by 10% at one manufacturing company; an
electronics manufacturer (~$3.2B revenue) used it during an S/4HANA
migration to analyze and optimize processes pre-cutover [SOURCE:
https://www.ennuviz.com/blogs/unlocking-the-power-of-process-intelligence-in-manufacturing-with-sap-signavio ;
https://www.agcapps.com/customer-success-story-revolutionising-process-management-with-ag-sap-signavio].
These are vendor/partner-published case studies, not independently audited
— see confidence ratings in ENTERPRISE_EVIDENCE.md.

## 3. Celonis (Execution Management System / Process Intelligence Graph)

**Position relative to ERP/MES**: connects to SAP, Oracle, Salesforce,
ServiceNow and other systems of record; explicitly promoted as
system-agnostic.

**Architecture, as documented** [SOURCE: Celonis PI Graph announcement,
https://www.celonis.com/news/press/celonis-pioneers-the-next-generation-of-process-intelligence-with-the-introduction-of-the-process-intelligence-graph ;
Celonis platform page, https://www.celonis.com/platform/process-intelligence-graph/]:

- **Context Model**: described as "the heart of the Celonis Platform" — a
  dynamic, system-agnostic representation built from process data *and*
  business knowledge across systems, applications, devices and
  interactions. This is a broader concept than a pure event log: it
  deliberately blends observed events with modeled business knowledge.
- **Process Intelligence Graph (PI Graph)**: Celonis's current top-level
  architecture, described as an "enriched digital twin of the business"
  that layers process mining and **object-centric process mining** on top
  of the Context Model to reconstruct end-to-end flows across systems
  `[VENDOR CLAIM, product-marketing language]`.
- **Analytics/action layer**: bottleneck and value-opportunity
  identification, plus orchestrated actions to "fix them in real time"
  `[VENDOR CLAIM]` — again explicitly separating discovery from action.
- **AI layer**: marketed as "Enterprise AI powered by Celonis," positioned
  as reasoning over the Context Model / PI Graph rather than over raw
  system data directly `[VENDOR CLAIM]`.

**Manufacturing-specific case evidence found** (see
ENTERPRISE_EVIDENCE.md for confidence ratings):

- Siemens: factories moved from twice-daily printed production schedules
  to near-real-time (15-minute) readouts of on-time production/assembly
  status; direct-material order approver count halved [SOURCE:
  https://www.celonis.com/customer/siemens-inventory-management/].
- Molex: supplier PO confirmation rate rose from 30% to 90% [SOURCE:
  https://www.molex.com/en-us/about/case-studies/celonis-process-mining-for-supply-chain-reliability].
- An AWS-published case describes a manufacturing client saving "over 240
  hours monthly across 30 production sites" using Celonis plus Amazon
  Bedrock [SOURCE: https://aws.amazon.com/solutions/case-studies/celonis-case-study/]
  — vendor/partner-published, figures not independently audited.

## 4. SAP Digital Manufacturing (Cloud)

This is materially different from Signavio/Celonis: it is a **Manufacturing
Execution System (MES) + Manufacturing Intelligence (MII)** product, not a
process-mining product. It sits closer to the shop floor.

**Architecture, as documented** [SOURCE:
https://www.sap.com/products/scm/digital-manufacturing.html ; SAPinsider,
https://sapinsider.org/topic/sap-supply-chain-management/sap-digital-manufacturing-cloud/]:

- **Execution layer**: production scheduling, dispatching, resource
  orchestration, labor allocation (discrete and process industries).
- **Quality layer**: manual and ML-based visual inspection.
- **Connectivity layer**: a "Production Connector" for shop-floor
  devices/equipment; positioned as producing "a clean data foundation for
  AI, predictive maintenance and executive analytics" `[VENDOR CLAIM]`.
- **Intelligence layer**: manufacturing intelligence (MII) that combines
  shop-floor and business data for real-time analytics/OEE reporting, and
  operator-facing Fiori dashboards (Production Operator Dashboards).

**Implication for this research**: SAP DM is the kind of system that would
sit at Layer 1 (evidence source) for a factory-intelligence system, not a
competitor to PM4Py/OCEL-based process intelligence. It is relevant mainly
as a description of what "good" shop-floor data capture looks like, and as
a reminder that many medium manufacturers do **not** run anything this
mature (see §6 and §7).

## 5. Object-centric process mining (OCEL 2.x) as an architectural layer

**Standard**: OCEL 2.0, released 2023, extends OCEL 1.0 (2020). It adds
normative object-to-object relationships, qualifiers on both
event-to-object and object-to-object relationships, and evolving object
attribute values. Exchange formats: SQLite (relational), XML, JSON.
Reference site: https://www.ocel-standard.org/specification/overview/
[SOURCE: OCEL 2.0 Specification, arXiv:2403.01975,
https://arxiv.org/pdf/2403.01975].

**How it fits architecturally**: OCEL is a *data model / interchange
format* that sits at Layer 2 (process/object model), independent of any
specific analytics or vendor. PM4Py (open source, Python) fully supports
OCEL 2.0, including object-centric process discovery (OCPN, OC-DFG,
OC-BPMN model types) and object-centric conformance checking [SOURCE: PM4Py
paper, ScienceDirect, https://www.sciencedirect.com/science/article/pii/S2665963823000933].
Both SAP Signavio and Celonis have published material describing
object-centric process mining as part of their roadmap/current capability
[SOURCE: https://www.signavio.com/wiki/process-discovery/object-centric-process-mining-ocpm/ ;
https://www.celonis.com/blog/what-is-object-centric-process-mining-ocpm]
— i.e. OCEL/OCPM is being absorbed into commercial platforms, not just an
academic construct.

**Manufacturing relevance**: manufacturing, along with procurement and
order-to-cash, is explicitly named as a domain where multiple interacting
objects (orders, components, machines, quality inspections) make
case-centric modeling awkward [SOURCE: arXiv:2311.08795, "Advancements and
Challenges in Object-Centric Process Mining: A Systematic Literature
Review," https://arxiv.org/abs/2311.08795]. See
[REFERENCE_COMPARISON.md](REFERENCE_COMPARISON.md) for a direct comparison
of case-centric vs. object-centric tradeoffs.

## 6. Factory simulation / digital twin

**OFacT / OpenFactoryTwin** (Fraunhofer ISST and partners): an open-source
"simulation-based digital twin for production and logistics material
flows." It is built on a general state model describing factory state and
possible behaviors, applicable to assembly lines, flexible matrix
production, job shops, warehouses, and supply networks. It integrates data
sources (ERP, WMS, sensors) into a single data model and supports what-if
scenario evaluation ("OFacT Sim") and derived cost/performance figures
("OFacT Analytics") [SOURCE: Fraunhofer ISST,
https://www.isst.fraunhofer.de/en/departments/industrial-manufacturing/technologies/OFacT.html ;
GitHub, https://github.com/OpenFactoryTwin/ofact ; Zenodo initial release,
https://zenodo.org/records/13734211]. As verified directly in Gate 0, the
public `0.1.0` release is an early-stage artifact (data model + tutorial;
packaging metadata is broken — see
[reports/BOOTSTRAP_REPORT.md](BOOTSTRAP_REPORT.md)), not a
production-hardened product.

**Architectural position**: digital twin/simulation sits at Layer 4,
consuming the same kind of evidence (ERP/MES/sensor data) that feeds
process mining at Layer 1–2, but answering a different question ("what
happens if we change X") rather than "what happened" or "why."

**Evidence on adoption difficulty**: academic literature is consistent that
discrete-event simulation and digital-twin adoption in manufacturing SMEs
faces high setup cost, scarce specialized expertise, fragmented source
data, and substantial effort to build and validate interfaces and models
[SOURCE: https://www.tandfonline.com/doi/full/10.1080/17477778.2026.2628033 ;
TTTech, "Nine digital twin barriers for manufacturing SMEs,"
https://www.tttech.com/digital-twin-barriers]. This is treated in detail in
[ENTERPRISE_EVIDENCE.md](ENTERPRISE_EVIDENCE.md).

## 7. Engineering intelligence and standards compliance — architecturally distinct

None of the platforms studied (Signavio, Celonis, SAP DM, OFacT, PM4Py)
claim to determine whether a process is *technically/engineering-wise*
appropriate against a standard such as IEC 60076. Investigation of IEC
60076 (power transformers) itself confirms why: **compliance is
demonstrated through objective test results** (insulation coordination,
temperature rise, short-circuit withstand, etc.), not through inference
over ERP process-execution data [SOURCE: EEP, "Comprehensive Guide to
Transformer Specification: Ensuring Compliance with IEC 60076,"
https://electrical-engineering-portal.com/guide-to-transformer-specification-compliance-iec-60076-part-1].
This confirms the architectural separation asked for in the task:
"is this technically appropriate" is a distinct capability (Layer 3.5,
arguably its own layer) that requires domain/engineering knowledge and
authoritative test/standards data — not something process mining or
simulation alone can answer. See §5 of
[LENSIPS_GAP_ANALYSIS.md](LENSIPS_GAP_ANALYSIS.md).

## 8. Evidence/data-reliability layer — present in the literature, not a marketed product feature

Every process-mining-specific source reviewed treats event log quality as a
first-order, hard problem, distinct from the analytics built on top of it:
real event logs are described as "fine-granular, heterogeneous,
voluminous, incomplete, and noisy" [SOURCE: Event Log Data Quality Issues
and Solutions, https://doi.org/10.3390/math11132858], and "Process-Data
Quality" is argued to be "the true frontier of process mining" [SOURCE:
https://dl.acm.org/doi/10.1145/3613247]. Vendor product pages for Signavio
and Celonis describe fast connection to source systems but do not publish
detailed methodology for measuring or reporting evidence confidence
per-finding; this is `INSUFFICIENT EVIDENCE` to say whether either product
has a mature, customer-facing data-quality/confidence layer. This is the
single most important open question carried into
[LENSIPS_GAP_ANALYSIS.md](LENSIPS_GAP_ANALYSIS.md).

## 9. AI reasoning layer — general risk, not manufacturing-specific evidence found

Academic work on LLMs applied to process mining tasks documents a taxonomy
of hallucination types specific to process mining (four families, twelve
sub-types), and shows that "knowledge-driven hallucination" — where a
model's generalized prior knowledge overrides explicit source evidence —
is a real, measured phenomenon in process-modeling tasks [SOURCE:
https://www.techrxiv.org/doi/full/10.36227/techrxiv.175977705.50503509/v1 ;
https://arxiv.org/pdf/2509.15336]. No manufacturing-specific or
transformer-specific evidence of LLM-based factory diagnosis was found;
this is `INSUFFICIENT EVIDENCE` and is treated as a hard research problem
in [LENSIPS_GAP_ANALYSIS.md](LENSIPS_GAP_ANALYSIS.md).

---

## Summary table: where each layer sits relative to ERP/MES/QMS/IoT

| Layer | Consumes from | Produces | Example platforms/standards |
|---|---|---|---|
| Evidence ingestion | ERP, MES, QMS, IoT/sensors | Cleaned event/object records + explicit data-quality signal | SAP extractors, OFacT's ERP/WMS/sensor integration |
| Process/object model | Evidence layer | Event log (XES) or object-centric event log (OCEL 2.x) | PM4Py, Celonis Context Model, Signavio process model |
| Analytics | Process/object model | Discovery, conformance, bottlenecks, root cause | PM4Py, Signavio, Celonis PI Graph |
| Simulation/digital twin | Process/object model + engineering parameters | What-if scenario results | OFacT, generic DES tools |
| Engineering intelligence | Domain standards, test data, benchmarks (NOT process data alone) | Technical-appropriateness judgments | Not found as a product in any platform surveyed |
| AI reasoning | Structured outputs of the above, with evidence/confidence attached | Explained findings and recommendations | Marketed by Celonis/Signavio `[VENDOR CLAIM]`; academic evidence of hallucination risk applies |
