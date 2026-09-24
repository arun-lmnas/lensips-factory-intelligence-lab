# LENSIPS Factory Intelligence Lab

An exploratory research lab for LMNAs Cloud Solutions. See [AGENTS.md](AGENTS.md)
for ground rules when working in this repository and the current gate status.

## 1. Business context

LMNAs develops LENS, a Frappe/ERPNext-based cloud platform, with a strong focus on
engineered manufacturing, particularly transformer manufacturing.

One of our products is **LENSIPS — LENS Intelligent Planning / Intelligence**.

LENSIPS currently has capabilities around manufacturing planning, forecasting,
MPS/MRP, material readiness, production planning and transformer-specific
planning concepts.

We are now investigating a much broader opportunity:

> Can LENSIPS become a factory intelligence system that can reconstruct how a
> factory actually operates, identify process and operational problems,
> determine whether processes are appropriate/efficient, compare performance
> against relevant engineering/industry evidence, simulate improvements, and
> explain its findings with evidence?

This investigation was triggered by discussions with an experienced
transformer-industry professional who asked whether LENSIPS could analyse a
medium-sized Italian transformer manufacturer's processes and answer questions
such as:

* Are the manufacturing processes compliant with relevant IEC/IEEE requirements?
* Are the processes optimized?
* Are costs and manufacturing times reasonable?
* Is a particular machine or process step optimized?
* Can actual process time/cost be compared with industry benchmarks?
* Can the system identify subprocesses causing problems?
* Can it recommend remedies?
* For example, if a 35 MVA transformer takes X hours and Y EUR, can the
  system determine whether those figures are reasonable and explain why?

We do NOT yet know that we can answer these questions.

This repository exists to establish what is already possible using proven
technologies before we build anything proprietary.

---

## 2. Architectural hypothesis

We believe this problem may require several distinct capabilities rather than
one technology.

Potential layers include:

### Process Intelligence

Answers: *What actually happened?*

Examples: process discovery, process variants, cycle time, waiting time,
rework, deviations, conformance, root-cause analysis.

Relevant technologies include SAP Signavio Process Intelligence, Celonis,
PM4Py, OCEL / object-centric process mining.

### Factory Intelligence

Answers: *Why is the factory behaving this way?*

Examples: bottlenecks, machine utilization, downtime, quality events,
material shortages, queues, resource constraints, process variation.

### Factory Simulation / Digital Twin

Answers: *What happens if we change something?*

Examples: add a machine, change routing, change operation time, alter
capacity, change production sequence, change subcontracting strategy.

Potential foundation being evaluated: OpenFactoryTwin / OFacT.

### Engineering Intelligence

Answers: *Is this manufacturing process technically appropriate?*

This is where transformer-specific engineering knowledge, standards,
historical evidence and industry benchmarks may eventually be required. This
is NOT assumed to be solved by process mining.

### LENSIPS AI Reasoning

The eventual LENSIPS layer should reason over structured evidence from the
above systems. It must distinguish: observed fact, calculated metric,
inference, recommendation, missing evidence, confidence.

The LLM must NOT be responsible for calculating operational metrics from raw
data.

---

## 3. Important architectural principle

We are NOT trying to invent process mining.

Enterprise process mining is already a mature discipline. SAP Signavio,
Celonis and other established platforms demonstrate that ERP and
enterprise-system event data can be transformed into process representations
and analysed for process discovery, conformance, bottlenecks, deviations and
root causes. There are also established approaches for manufacturing process
mining, object-centric process mining and digital twins.

Therefore: **reuse proven foundations wherever possible.**

Do not implement process mining algorithms ourselves unless an experiment
proves that an existing foundation cannot satisfy the requirement. Do not
create our own digital-twin engine if an existing open foundation can provide
the required capability. Do not build infrastructure merely for the sake of
architectural completeness.

The purpose of this repository is **evaluation and evidence**, not premature
product construction.

---

## 4. Why this research is necessary

The team has extensive SAP/ERP experience, but factory/process intelligence
outside conventional ERP process analysis is a newer area for us. We
therefore need additional validation before making architectural
commitments.

In particular, we need to distinguish:

1. ERP process mining — mature and proven
2. Manufacturing process mining — established but more complex
3. Digital twins / manufacturing simulation — established but a separate discipline
4. Transformer engineering intelligence — specialized and requires domain evidence
5. IEC/IEEE compliance reasoning — requires authoritative standards and careful interpretation
6. Industry time/cost benchmarking — requires trustworthy benchmark populations
7. LLM-based factory diagnosis — must be evidence-grounded and independently validated

Do not assume that success in one category proves success in another.

---

## 5. Reference architecture direction (hypothesis only, not yet implemented)

```
                        LENSIPS
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
   Process             Factory            Engineering
 Intelligence        Intelligence        Intelligence
        │                  │                  │
     PM4Py              OFacT              Domain
     OCEL              Digital            Knowledge /
                        Twin              Standards
        │                  │                  │
        └──────────────────┼──────────────────┘
                           │
                    Evidence Layer
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
      ERP                MES              QMS / IoT
```

This is ONLY a hypothesis. This architecture is not implemented in this
repository yet.

---

## 6. Object-centric data is important

A conventional process can often be represented as `Case → Activity →
Timestamp`. But manufacturing is not always a single-case sequence.

A transformer order can involve related objects such as: customer order,
transformer, engineering design, core, LV winding, HV winding, tank,
material, purchase order, machine, production operation, quality inspection,
maintenance event.

Therefore we are specifically interested in **OCEL / object-centric process
modelling**, particularly OCEL 2.x. Do not assume that a simple case-centric
process model is sufficient for the eventual transformer use case.

---

## 7. Data reliability is a first-class concern

A major business concern is that real enterprise data may be: incomplete,
inconsistent, duplicated, manually corrected, contradictory, missing
timestamps, missing machine/resource relationships, selectively entered,
distributed across departments, unreliable for some processes.

Therefore the eventual system must not blindly trust ERP/MES data. A desired
future output could look like:

```
Finding:
HV winding is a candidate constraint.

Evidence:
Utilization = 91%
P90 queue time = 6.2 hours
Rework = 8.3%

Data quality:
Timestamp coverage = 94%
Machine telemetry coverage = 76%

Confidence:
Medium-high

Missing evidence:
24% of machine-state data unavailable.
```

This is an example only — do not fabricate numbers like these.

The important principle is: **conclusions must be traceable to evidence, and
evidence quality must be measurable.**

---

## 8. Development philosophy

The owner of this project is acting primarily as a **functional/solution
architect**, not as the person who wants to manually build infrastructure.
The goal is to minimize human setup work.

Agents should therefore: bootstrap environments, install dependencies,
investigate existing frameworks, run documented examples, download and
prepare evaluation datasets, write small experiment scripts, execute tests,
produce reports.

The human architect should mainly: define hypotheses, review evidence, judge
whether results are industrially meaningful, make architectural decisions,
provide transformer-domain knowledge, determine product relevance.

Do not require the human to manually perform routine environment setup when
it can be safely automated.

---

## 9. Agent usage philosophy

Claude Code and Codex will be used differently.

**Claude Code** is primarily for: repository archaeology, understanding
existing frameworks, researching architecture, reading documentation/source,
comparing approaches, running exploratory examples, documenting findings.

**Codex** is primarily for: bounded implementation, adapters, scripts, tests,
data transformations, reproducible experiments, fixing specific failures.

Do NOT use autonomous multi-agent orchestration at this stage. Do NOT
introduce OpenAI Symphony, Linear task orchestration, self-spawning agents,
or long autonomous loops until the architecture and repeatable engineering
workflow have been proven.

Previous experimentation with agentic orchestration showed that large
autonomous tasks can consume significant model/agent credits. We therefore
deliberately want **small, bounded, terminating tasks**.

---

## 10. Agent task contract

Every experiment in this repository should have:

* **Scope** — what may be changed.
* **Inputs** — what data/frameworks may be used.
* **Outputs** — exactly what must be produced.
* **Do not** — what must not be changed.
* **Exit criteria** — the precise condition that means the task is complete.
* **Evidence** — how the result can be reproduced or verified.

Agents must stop when the exit criteria are met. Do not continue by
inventing additional improvements or future tasks.

---

## 11. Repository philosophy

This is a disposable research laboratory. It is NOT the LENSIPS production
repository, LensCloud, ERPNext, a production infrastructure repository, or a
customer implementation.

Do not introduce Frappe, ERPNext, Kubernetes, Redis, PostgreSQL, n8n,
production credentials, or production data unless a later experiment
explicitly requires them.

Keep external frameworks as external dependencies. Do not fork or modify
PM4Py or OFacT during evaluation. If a capability is missing, document the
gap before deciding to implement anything.

---

## 12. Planned evaluation gates

* **Gate 0** — Reproducible development environment. *(done — see [reports/BOOTSTRAP_REPORT.md](reports/BOOTSTRAP_REPORT.md))*
* **Gate 1** — Reference architecture study: SAP Signavio, Celonis, SAP Digital Manufacturing, enterprise manufacturing process-mining implementations, digital twin references, object-centric process mining.
* **Gate 2** — Reproduce a known ERP process-mining use case using a public dataset.
* **Gate 3** — Test data-quality/reliability handling.
* **Gate 4** — Apply the approach to manufacturing event/object data.
* **Gate 5** — Evaluate factory digital-twin/simulation capabilities.
* **Gate 6** — Build evidence-grounded LENSIPS reasoning over structured results.
* **Gate 7** — Apply the architecture to a small transformer-manufacturing model.

Do not start a gate without explicit instruction to do so, and do not skip
ahead of the current gate — see [AGENTS.md](AGENTS.md) for current status.

## Repository layout

- `.devcontainer/` — the Gate 0 evaluation environment (Dockerfile + devcontainer.json).
- `experiments/` — bounded, reproducible experiment scripts/notebooks for later gates.
- `datasets/` — evaluation datasets (public/synthetic only; no production data).
- `reports/` — findings and evidence, e.g. `BOOTSTRAP_REPORT.md`.
- `scripts/` — utility scripts, e.g. `smoke-test.sh`.
