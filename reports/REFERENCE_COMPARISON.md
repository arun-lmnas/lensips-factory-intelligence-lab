# Reference Comparison — Gate 1

Compares the platforms/approaches named in the Gate 1 brief across purpose,
inputs, outputs, process model, object model, analytics, simulation, data
quality, AI, manufacturing applicability, SME suitability, and limitations.

Ratings (`HIGH`/`MEDIUM`/`LOW`/`INSUFFICIENT EVIDENCE`) reflect what the
sources reviewed actually support, not intuition. See
[ENTERPRISE_EVIDENCE.md](ENTERPRISE_EVIDENCE.md) for the underlying evidence
register and confidence levels behind each row.

| Dimension | SAP Signavio Process Intelligence | Celonis (PI Graph / EMS) | SAP Digital Manufacturing (Cloud) | Object-centric process mining / OCEL (PM4Py) | OFacT / OpenFactoryTwin |
|---|---|---|---|---|---|
| **Purpose** | Process mining & analysis on top of SAP/non-SAP systems | End-to-end process intelligence + orchestrated action ("Execution Management") | MES + manufacturing intelligence (shop-floor execution) | Open standard + library for object-centric event data and analysis | Open-source simulation-based digital twin for production/logistics material flow |
| **Inputs** | Extracted event data from ERP/other systems | Event/master data from SAP, Oracle, Salesforce, ServiceNow, etc. | Shop-floor device/equipment data via Production Connector; ERP order data | Any source system's data, once mapped to OCEL 2.x (event, object, relationship records) | ERP, WMS, sensor data, integrated into one state model |
| **Outputs** | Process maps, conformance results, dashboards, triggered workflows/bots | PI Graph (digital twin of processes), bottleneck/value findings, orchestrated actions | Execution schedules, quality inspection results, OEE/analytics, operator dashboards | Object-centric process models (OCPN, OC-DFG, OC-BPMN), conformance diagnostics | Simulated what-if scenario results, calculated cost/performance figures |
| **Process model** | Primarily case-centric (per SAP Help documentation reviewed); embedded AI mentioned generically `[VENDOR CLAIM]` | Case-centric plus object-centric via Context Model / PI Graph `[VENDOR CLAIM]` | Not a process-mining model — an execution/scheduling model | Native object-centric (OCEL 2.x): explicit object-to-object and event-to-object relationships with qualifiers | State-model based (factory state + possible behaviors), not an event-log process model |
| **Object model** | Not confirmed as object-centric in sources reviewed — `INSUFFICIENT EVIDENCE` on internal architecture | Explicitly object-centric per Celonis's own OCPM material `[VENDOR CLAIM]` | N/A (execution system, not analytics) | Formal, standardized: OCEL 2.0 (SQLite/XML/JSON exchange formats) | Custom state model for factory entities/resources — not OCEL-based |
| **Analytics** | Discovery, conformance, performance analysis | Discovery, conformance, bottleneck/root-cause style "value opportunity" identification | OEE, quality analytics, real-time execution KPIs | Object-centric discovery + object-centric conformance checking (PM4Py implements both) | "OFacT Analytics": cost/performance figures computed from the state model |
| **Simulation** | Not a simulation product | Not primarily a simulation product (action orchestration ≠ simulation) | Not a simulation product | Not a simulation capability — this is a data/analytics standard | Core capability: "OFacT Sim" what-if scenario evaluation |
| **Data quality** | No detailed public methodology found for confidence scoring — `INSUFFICIENT EVIDENCE` | No detailed public methodology found for confidence scoring — `INSUFFICIENT EVIDENCE` | Positioned as producing "a clean data foundation" `[VENDOR CLAIM]`, no independent verification found | Not addressed by the standard itself; data-quality handling is a research topic layered on top (see academic sources in ENTERPRISE_EVIDENCE.md) | Not addressed as a first-class capability in sources reviewed |
| **AI** | "Embedded AI" `[VENDOR CLAIM]`, no technical detail found | "Enterprise AI powered by Celonis" `[VENDOR CLAIM]`, reasoning described as over the Context Model, not raw data | ML-based visual inspection for quality | Not an AI capability; OCEL is cited as an enabler for more reliable generative/predictive/prescriptive AI in academic work (arXiv:2508.00116) — an argument, not proof | Not an AI capability |
| **Manufacturing applicability** | Demonstrated (maintenance excellence case; S/4HANA migration case) | Demonstrated (Siemens, Molex, automotive OEM cases) | Purpose-built for manufacturing (native MES) | Explicitly named as a relevant domain (manufacturing, procurement) in academic literature; production tool support (PM4Py) confirmed | Explicitly built for production/logistics material flow |
| **SME suitability** | `LOW–MEDIUM`: no SME-tier pricing/case evidence found; enterprise-oriented positioning | `LOW`: enterprise pricing ($150K–$250K+/yr license; $120K–$500K+ implementation; $1.26M+ Year-1 TCO in a composite enterprise example) makes it a poor fit for medium manufacturers without adaptation [SOURCE: vendorbenchmark.com pricing benchmark, https://vendorbenchmark.com/blog/process-mining-platform-pricing-benchmark] | `LOW–MEDIUM`: full MES deployments are a major undertaking; not evaluated for SME cost specifically here | `HIGH` on cost (PM4Py is free/open source), `MEDIUM` on skill requirement — OCPM specifically is reported as adding real complexity and requiring analytical expertise beyond case-centric mining (see below) | `MEDIUM` on cost (open source), `LOW–MEDIUM` on maturity/completeness verified directly in Gate 0 (packaging bug in the only tagged release) |
| **Key limitations found** | Public documentation is high-level; independent (non-vendor) verification of claims is scarce | Very high cost; "Context Model" blends observed data with modeled business knowledge, which needs care to keep evidence vs. inference distinguishable; OCPM adoption in industry still described as limited even by a Celonis-authored blog responding to an Everest Group report [SOURCE: https://www.celonis.com/blog/object-centric-process-mining-addresses-challenges-outlined-by-everest-group-report] | Not a process-intelligence tool; a source of Layer-1 evidence, not a competitor capability | OCPM is reported in a systematic literature review as computationally intensive at scale, hard to interpret for non-experts, lacking standardized cross-object KPIs, and still concentrated in a narrow set of use cases (chiefly supply chain) [SOURCE: arXiv:2311.08795] | Verified directly: `0.1.0` tag ships a broken Poetry package definition (declares package `dt`, no matching folder) — see [BOOTSTRAP_REPORT.md](BOOTSTRAP_REPORT.md). Early-stage, single tagged release, tutorial-level maturity as far as verified. |

## Free/open-source alternatives relevant to SME cost constraints

Because Celonis-tier pricing is a real barrier for medium manufacturers (see
above), it is worth noting **Apromore** as a documented alternative: an
open-source process-mining platform (Community edition, self-hosted via
Docker) offering process discovery, conformance checking, performance
analysis, log animation, and simulation, originating from academic research
at the University of Melbourne and University of Tartu, with a separate
commercial Enterprise tier [SOURCE:
https://www.deep-analysis.net/vendor-vignette-0/apromore-review/ ;
https://processminingpro.com/free-process-mining-tools/]. This is relevant
evidence that the SME-appropriate tier of process mining tooling already
exists in the market and does not need to be built from PM4Py alone,
though PM4Py plus DuckDB/Pandas (as already evaluated in Gate 0) remains a
credible, zero-license-cost foundation for bespoke, LENSIPS-embedded
capability.

## Object-centric vs. case-centric — direct tradeoff, not a strict upgrade

The evidence does **not** support treating object-centric process mining as
a strict improvement over case-centric mining for every situation:

- **Where OCPM helps**: processes with genuinely multiple interacting
  objects and non-trivial cardinalities (one order → many components → many
  operations → many inspections) are exactly the case where case-centric
  mining forces an arbitrary case notion and can hide dependencies between
  objects [SOURCE: arXiv:2311.08795; Celonis OCPM blog].
- **Where OCPM costs more than it returns**: the same literature reports
  real costs — computational intensity, harder interpretation for
  non-experts, lack of standardized KPIs across object types, and a
  still-narrow base of production use cases outside supply chain
  [SOURCE: arXiv:2311.08795]. A 2026 ECIS proceedings paper frames
  "Challenges and Opportunities of Object-Centric Process Mining in
  Industry" as an open research agenda, not a solved problem
  [SOURCE: https://aisel.aisnet.org/ecis2026/bpm/bpm/2/].

This directly informs the MUST/SHOULD/COULD/WON'T classification in
[CAPABILITY_PORTFOLIO.md](CAPABILITY_PORTFOLIO.md): object-centric modeling
is treated as a targeted tool for specific, genuinely multi-object
sub-problems (e.g. linking a transformer's core/windings/tank/tests to one
order), not a wholesale replacement for simpler case-centric analysis
everywhere in LENSIPS.
