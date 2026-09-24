# Capability Portfolio — Gate 1

Decision-oriented synthesis of
[REFERENCE_ARCHITECTURE.md](REFERENCE_ARCHITECTURE.md),
[REFERENCE_COMPARISON.md](REFERENCE_COMPARISON.md),
[ENTERPRISE_EVIDENCE.md](ENTERPRISE_EVIDENCE.md), and
[LENSIPS_GAP_ANALYSIS.md](LENSIPS_GAP_ANALYSIS.md).

Decision rules applied throughout (see original Gate 1 brief): high
enterprise evidence does not automatically mean MUST; low evidence does not
automatically mean WON'T; high effort + uncertain value leans toward
experimentation, not commitment; low effort + high potential value can
justify a small experiment even with limited evidence; commoditized
capabilities are only worth pursuing if LENSIPS can deliver them
substantially simpler for medium manufacturers; customer problem comes
before technology; insufficient evidence is stated explicitly.

---

## Capability entries

```text
Capability: Case-centric process discovery & conformance on LENSIPS's own
            order/production data (using PM4Py)
Customer problem: "Show me how orders actually flow through my factory,
            and where they deviate from the intended process."
Enterprise evidence: HIGH (mature, widely used technique; PM4Py verified
            installable in Gate 0; peer-reviewed manufacturing case studies
            in ENTERPRISE_EVIDENCE.md #6, #7)
Evidence confidence: PROVEN (methodology and tooling), EMERGING (ROI at
            SME scale)
Medium-enterprise applicability: HIGH — works with the coarser, milestone-
            level event data medium manufacturers typically have, as long
            as expectations are calibrated (see data-quality note below)
Required data: order/production timestamps already present in LENSIPS's
            own data model; no new data collection needed to start
Implementation effort: MEDIUM — algorithms are proven and available for
            free (PM4Py); effort is in mapping LENSIPS's own data model to
            a usable event log, not in inventing new mining algorithms
Expected customer value: HIGH — this is the foundational capability nearly
            every other capability in this portfolio depends on
Time to value: SHORT
Differentiation: LOW on the algorithm itself (commoditized), MEDIUM-HIGH on
            being natively embedded in the ERP the customer already uses
            (no extraction project required, unlike Signavio/Celonis)
Dependence on external IP: LOW (PM4Py is open source, Apache-licensed
            per its published documentation)
MoSCoW: MUST
Recommendation: Build this as the foundation. Reuse PM4Py; do not
            reimplement discovery/conformance algorithms.
Reason: Mature technology + direct customer value + already-owned data +
            near-zero licensing cost + clear differentiation from
            enterprise process-mining tools on cost/embedding, not on
            algorithmic novelty.
Evidence: ENTERPRISE_EVIDENCE.md #6, #7, #8; REFERENCE_ARCHITECTURE.md §2-3, §5
```

```text
Capability: Evidence / Data Reliability Layer (confidence scoring +
            explicit "what's missing" reporting, attached to every finding)
Customer problem: "Can I trust this finding, given how messy my data
            actually is?" — directly named as a business concern in
            README.md §7
Enterprise evidence: LOW — no surveyed platform (Signavio, Celonis, OFacT)
            was found to have a mature, customer-facing version of this
            (INSUFFICIENT EVIDENCE either way per ENTERPRISE_EVIDENCE.md #17
            and REFERENCE_ARCHITECTURE.md §8)
Evidence confidence: HYPOTHESIS (the need is evidenced — SME manufacturing
            data sparsity is PROVEN per ENTERPRISE_EVIDENCE.md #12 — but no
            evidence exists yet that LENSIPS's specific design for this
            layer will work)
Medium-enterprise applicability: HIGH — this is precisely the customer
            segment (SMMC) documented to have sparse, milestone-only event
            data
Required data: the same order/production data as the discovery capability,
            plus metadata about source-system coverage/completeness
Implementation effort: MEDIUM-HIGH — no off-the-shelf library computes
            this; it requires original design work (this is the "domain
            modelling" + "algorithms" kind of effort, not "AI reasoning")
Expected customer value: HIGH — differentiates LENSIPS from tools that
            silently assume complete/clean data
Time to value: MEDIUM
Differentiation: HIGH — this is a genuine, evidenced gap (Rule 4 applies:
            low evidence does not mean WON'T, especially when the customer
            problem it solves is well evidenced even if the specific
            solution isn't)
Dependence on external IP: LOW
MoSCoW: MUST
Recommendation: Design and build this alongside the discovery capability
            from the start, not as an afterthought. Every finding LENSIPS
            produces should carry a confidence/evidence-completeness
            statement.
Reason: Rule 4 (low technology evidence + high customer value justifies a
            focused effort) combined with Rule 7 (customer problem before
            technology) — the customer problem (untrustworthy data) is
            strongly evidenced even though no reference implementation
            exists to copy.
Evidence: ENTERPRISE_EVIDENCE.md #12, #17; REFERENCE_ARCHITECTURE.md §8;
            LENSIPS_GAP_ANALYSIS.md §3
```

```text
Capability: Targeted object-centric modeling for specific multi-object
            sub-problems (e.g., transformer order ↔ core/windings/tank/tests)
Customer problem: "Which specific batch/machine/operation caused this
            quality problem?" — a question case-centric mining answers
            poorly when several objects (order, component, machine,
            inspection) interact
Enterprise evidence: MEDIUM — OCEL 2.0 is a real, adopted standard with
            production-grade tool support (PM4Py); but real-world adoption
            of OCPM remains narrow and concentrated in supply chain
            (ENTERPRISE_EVIDENCE.md #9)
Evidence confidence: PROVEN (the standard and tooling exist and work),
            EMERGING (manufacturing-specific production value)
Medium-enterprise applicability: MEDIUM — valuable for specific
            traceability questions, but full object-centric modeling
            everywhere adds complexity SME teams may struggle to interpret
            (REFERENCE_COMPARISON.md)
Required data: relationships between orders, components, machines, and
            inspections — likely already present in LENSIPS's BOM/routing
            data model, needs to be projected into OCEL form
Implementation effort: MEDIUM — PM4Py provides the OCEL tooling; effort is
            in selecting the right narrow scope and mapping LENSIPS data to
            it, not building OCPM algorithms from scratch
Expected customer value: MEDIUM-HIGH for the specific traceability
            question it targets; LOW if applied broadly/by default
Time to value: MEDIUM
Differentiation: MEDIUM — few competitors apply OCPM to transformer-style
            component traceability specifically
Dependence on external IP: LOW (PM4Py, open OCEL standard)
MoSCoW: SHOULD
Recommendation: Do not adopt object-centric modeling as the default data
            representation. Pilot it narrowly on one genuinely multi-object
            traceability question before deciding how far to extend it.
Reason: Rule 6 (do not build a technically impressive capability merely
            because it fits the architecture) combined with Rule 3 (high
            effort + uncertain broad value should lean toward
            experimentation) — the narrow, targeted version is justified;
            the broad version is not yet.
Evidence: REFERENCE_ARCHITECTURE.md §5; REFERENCE_COMPARISON.md
            ("Object-centric vs. case-centric"); ENTERPRISE_EVIDENCE.md #8, #9
```

```text
Capability: Targeted "what-if" simulation of a single bottleneck step
            (not a full-factory digital twin)
Customer problem: "If I add a shift / a machine / change this one step,
            what happens to my bottleneck?"
Enterprise evidence: MEDIUM — discrete-event simulation is a mature field
            in general; OFacT is a credible open foundation but verified in
            Gate 0 to be early-stage (broken packaging at its only tagged
            release)
Evidence confidence: EMERGING
Medium-enterprise applicability: MEDIUM — full digital twins are
            documented as hard for SMEs (ENTERPRISE_EVIDENCE.md #10); a
            single-bottleneck, narrowly scoped simulation is a much smaller
            ask, though this narrower framing has not itself been
            evidenced in the literature reviewed (INSUFFICIENT EVIDENCE)
Required data: cycle-time and capacity data for the specific bottleneck
            step, output from the discovery/analytics capability above
Implementation effort: HIGH — simulation modeling requires real expertise
            even at small scope, and OFacT's actual usability beyond
            import/packaging is unverified
Expected customer value: MEDIUM-HIGH if it works, but unproven
Time to value: LONG relative to the discovery/data-reliability capabilities
Differentiation: MEDIUM
Dependence on external IP: MEDIUM — depends on how much of OFacT (an
            early-stage, single-release open project) LENSIPS would end up
            depending on vs. building bespoke
MoSCoW: COULD
Recommendation: Defer. Do not build on OFacT until its actual
            simulation/analytics code has been exercised on a toy scenario
            (see Proposed Next Gate candidates) — Gate 0 only verified that
            it imports, not that it works.
Reason: Rule 3 — high effort, uncertain value, and an unverified foundation
            argue for experimentation before commitment, not for building
            a roadmap around it yet.
Evidence: ENTERPRISE_EVIDENCE.md #10, #11; REFERENCE_ARCHITECTURE.md §6
```

```text
Capability: IEC/IEEE standards-compliance determination from process/ERP data
Customer problem: "Is this manufacturing process IEC compliant?" (the
            original triggering question in README.md §1)
Enterprise evidence: LOW — no platform surveyed claims this capability;
            direct evidence indicates IEC 60076 compliance is inherently a
            test-outcome determination, not inferable from process
            execution data (ENTERPRISE_EVIDENCE.md #16)
Evidence confidence: INSUFFICIENT EVIDENCE that this is achievable at all
            from the data sources in scope; the one source found argues
            structurally against it
Medium-enterprise applicability: N/A — the capability itself is not
            established as feasible
Required data: authoritative IEC standards text/interpretation + actual
            test results, which is a fundamentally different data source
            than process/ERP execution data
Implementation effort: VERY HIGH, and possibly not solvable with process
            data at all
Expected customer value: HIGH if it worked, but feasibility itself is the
            open question
Time to value: LONG (if pursued at all)
Differentiation: N/A pending feasibility
Dependence on external IP: HIGH (would require licensed access to
            IEC/IEEE standards text and domain expertise LMNAs would need
            to acquire)
MoSCoW: WON'T FOR NOW
Recommendation: Do not attempt literal standards-compliance determination.
            Redirect the underlying customer need toward the
            benchmark-against-own-history capability below, which is
            answerable with data LENSIPS actually has.
Reason: Rule 7 (customer problem before technology) — the real underlying
            question ("is this reasonable?") can be partially answered a
            different, evidenced way; the literal "IEC compliant" framing
            is not something any studied capability can deliver honestly.
Evidence: ENTERPRISE_EVIDENCE.md #16; REFERENCE_ARCHITECTURE.md §7;
            LENSIPS_GAP_ANALYSIS.md §5
```

```text
Capability: Benchmark actual order performance against the factory's own
            historical population (not external industry benchmarks, not
            standards compliance)
Customer problem: "Is this 35 MVA transformer's X hours / Y EUR reasonable
            compared to how this factory has performed on similar orders?"
Enterprise evidence: MEDIUM — this is a natural extension of the proven
            process-mining performance-analysis capability (comparing case
            durations against historical distributions is well-established
            process mining practice), though not documented as a named
            product feature in the specific "is this reasonable" framing
Evidence confidence: EMERGING
Medium-enterprise applicability: HIGH — requires only the factory's own
            historical data, which LENSIPS already has natively; does not
            require external industry benchmark datasets that may not
            exist or be trustworthy for a niche segment like transformer
            manufacturing
Required data: sufficient historical order data of comparable
            type/size/complexity — feasibility depends on order volume and
            variability at a given factory (open question, see Proposed
            Next Gate)
Implementation effort: MEDIUM — statistical comparison against historical
            distributions, combined with the Evidence/Data Reliability
            Layer's confidence reporting
Expected customer value: HIGH — directly answers a version of the
            triggering business question from README.md §1 that is
            actually achievable
Time to value: MEDIUM
Differentiation: HIGH — no surveyed platform packages this specifically
            for a medium manufacturer's own order history
MoSCoW: SHOULD
Recommendation: Pursue after the discovery + data-reliability MUSTs are
            proven, as a direct answer to the "is this reasonable" business
            question that avoids the infeasible standards-compliance framing.
Reason: Rule 7 and Rule 5 — reframes a commoditized-sounding ambition
            ("benchmarking") into something LENSIPS can deliver more simply
            than any enterprise platform, using data it already owns.
Evidence: LENSIPS_GAP_ANALYSIS.md §3; ENTERPRISE_EVIDENCE.md #6, #7
```

```text
Capability: Evidence-grounded LLM reasoning layer over structured findings
Customer problem: "Explain what you found and why, in plain language, with
            evidence and confidence."
Enterprise evidence: LOW-MEDIUM — vendors market "embedded AI" generically
            (ENTERPRISE_EVIDENCE.md general findings), but no independent
            technical verification of a robust evidence-grounding
            architecture was found; measured hallucination risk is
            documented specifically for process-mining-adjacent LLM tasks
Evidence confidence: PROVEN (the risk is real and measured), HYPOTHESIS
            (that it can be adequately mitigated for this use case)
Medium-enterprise applicability: HIGH if trustworthy — this is exactly the
            kind of explanation a medium manufacturer without a data
            science team needs
Required data: the structured, confidence-scored outputs of the other
            capabilities above — this capability must NOT be given raw data
            to reason over directly, per README.md's own principle
Implementation effort: HIGH — requires a validation harness to catch
            hallucination before any customer-facing use, not just prompt
            engineering
Expected customer value: HIGH if trustworthy, potentially harmful if not
            (a wrong "explanation" stated with confidence is worse than no
            explanation)
Time to value: LONG (responsible time-to-value, given the risk)
Differentiation: MEDIUM-HIGH if done credibly (most competitors' AI claims
            are unverified marketing per this research)
Dependence on external IP: MEDIUM (depends on underlying LLM provider)
MoSCoW: SHOULD
Recommendation: Design this to reason ONLY over structured,
            confidence-scored outputs from the MUST capabilities — never
            over raw data — and build an explicit hallucination-detection
            validation step before any customer-facing deployment.
Reason: Rule 3 — real risk (documented) + high potential value argues for
            careful experimentation with a validation harness, not for
            either skipping it or shipping it uncritically.
Evidence: ENTERPRISE_EVIDENCE.md #15; README.md §2 ("LENSIPS AI Reasoning")
```

```text
Capability: Full digital twin of the entire factory (all lines, all
            resources, continuously synced)
Customer problem: theoretically "simulate any change anywhere," but no
            specific medium-manufacturer customer problem was evidenced at
            this scope
Enterprise evidence: MEDIUM (OFacT and academic DES literature exist) but
            explicitly documented as hard for SMEs
Evidence confidence: PROVEN that the barrier is high (ENTERPRISE_EVIDENCE.md
            #10), INSUFFICIENT EVIDENCE that a medium manufacturer needs or
            can sustain a full digital twin
Medium-enterprise applicability: LOW
Required data: comprehensive, continuously updated data across the entire
            factory — far beyond what evidence #12 says medium
            manufacturers typically have
Implementation effort: VERY HIGH
Expected customer value: uncertain — likely lower than targeted
            alternatives given data/expertise constraints
Time to value: LONG
Differentiation: LOW at this stage (many organizations attempt full
            digital twins; few medium manufacturers successfully sustain
            them per the SME barrier literature)
Dependence on external IP: HIGH if built on OFacT wholesale
MoSCoW: WON'T FOR NOW
Recommendation: Do not pursue. Revisit only if the narrow, targeted
            simulation capability (above, COULD) proves valuable and the
            customer explicitly asks for broader scope.
Reason: Rule 6 — technically interesting, but effort and evidence do not
            support it for this customer segment now.
Evidence: ENTERPRISE_EVIDENCE.md #10, #11; LENSIPS_GAP_ANALYSIS.md §5
```

```text
Capability: General-purpose, Celonis/Signavio-style cross-enterprise
            Execution Management System (broad orchestration across many
            processes, third-party ERP connectors, etc.)
Customer problem: not a specific medium-manufacturer problem — this is a
            platform-breadth ambition, not a customer pain point
Enterprise evidence: HIGH for the enterprise segment, but priced and built
            for large enterprises (ENTERPRISE_EVIDENCE.md #14)
Evidence confidence: PROVEN (as an enterprise-segment product category)
Medium-enterprise applicability: LOW
Required data: extraction pipelines from arbitrary third-party systems —
            a fundamentally different (and larger) engineering problem than
            LENSIPS's native-data advantage
Implementation effort: VERY HIGH
Expected customer value: LOW relative to effort, for LENSIPS's actual
            target segment
Time to value: LONG
Differentiation: LOW — this would put LENSIPS in direct feature-breadth
            competition with well-funded incumbents on their own turf
MoSCoW: WON'T FOR NOW
Recommendation: Do not pursue. LENSIPS's differentiation is native
            embedding + medium-manufacturer focus, not platform breadth.
Reason: Rule 5 — this capability is already commoditized by incumbents at
            a scale/price point LENSIPS should not try to match; no
            evidence that LENSIPS could deliver it "substantially more
            simply."
Evidence: REFERENCE_COMPARISON.md; ENTERPRISE_EVIDENCE.md #14;
            LENSIPS_GAP_ANALYSIS.md §5
```

---

## MUST

1. **Case-centric process discovery & conformance on LENSIPS's own data**
   (PM4Py-based) — the proven, low-cost, high-value foundation.
2. **Evidence / Data Reliability Layer** — the evidenced customer need with
   no proven off-the-shelf answer; must be designed in from the start, not
   bolted on later.

## SHOULD

1. **Targeted object-centric modeling** for specific multi-object
   traceability questions (not a default representation).
2. **Benchmark against the factory's own historical order population** —
   the achievable, evidenced version of the "is this reasonable" question.
3. **Evidence-grounded LLM reasoning layer**, reasoning only over
   structured/confidence-scored outputs, with an explicit
   hallucination-validation step before customer-facing use.

## COULD

1. **Targeted, single-bottleneck "what-if" simulation** — explore only
   after the MUSTs are proven, and only after directly verifying whether
   OFacT (or an alternative) is actually usable beyond import/packaging.

## WON'T FOR NOW

1. **Literal IEC/IEEE standards-compliance determination** from process or
   ERP data — evidence suggests this is not achievable the way the
   original business question framed it; redirect to the historical-
   benchmark capability instead.
2. **Full-factory digital twin** — documented SME adoption barriers plus
   OFacT's verified early-stage maturity argue against committing here now.
3. **General-purpose, cross-enterprise Execution Management System
   breadth** (competing with Celonis/Signavio on their own turf) — wrong
   differentiation for LENSIPS's target segment.

---

## Final Executive Conclusion

### What We Know

- Case-centric process mining (discovery, conformance, performance
  analysis) is mature, proven in manufacturing settings including
  peer-reviewed evidence from steel manufacturing, and available today at
  zero license cost via PM4Py, which this lab's own Gate 0 already verified
  installs and imports correctly.
- Object-centric process mining (OCEL 2.x) is a real, standardized,
  tool-supported capability, but its real-world adoption is still narrow
  and its complexity cost is well documented — it is a targeted tool, not a
  default architecture.
- Medium/small manufacturing companies, as a class, commonly produce
  event data with large gaps ("most process steps... produce no events at
  all") — this is peer-reviewed, not assumed, and it is the single most
  important constraint on everything else in this portfolio.
- Enterprise-grade process intelligence platforms (Celonis, SAP Signavio)
  are priced for large enterprises; a medium manufacturer is not a
  realistic customer for these platforms at their current pricing.
- IEC 60076 compliance is established through objective test results, not
  through inference over process-execution data — the originating business
  question ("is this IEC compliant?") cannot honestly be answered by a
  factory-intelligence system built on process/ERP data alone.
- LLMs used adjacent to process mining have a documented, measured
  hallucination risk, including a specific failure mode where the model's
  prior knowledge overrides explicit source evidence.

### What We Suspect

- LENSIPS's native position inside the ERP (rather than an external tool
  that must extract and reconcile data from source systems) is a genuine
  structural advantage for the target customer segment — but this has not
  been evidenced with a real deployment, only inferred from the evidence
  about extraction being a major cost driver for external tools.
- A confidence-scored "evidence/data reliability layer" is likely to be
  more valuable to this customer segment than more analytically
  sophisticated capabilities built on data those customers may not
  actually have.
- The "benchmark against your own history" framing can deliver most of the
  business value the original IEC-compliance question was reaching for,
  without the infeasibility problem.

### What We Should Test Next

- Whether realistic (or real, if obtainable) medium-manufacturer
  production data — even sparse, milestone-only data — produces usable
  PM4Py discovery/conformance results, and what the Evidence/Data
  Reliability Layer should say when it doesn't.
- Whether OFacT's actual simulation/analytics code (not just its imports)
  runs on a toy scenario, to know if it's a viable foundation at all.
- Whether a small, narrowly scoped OCEL model of an order's
  core/windings/tank/tests relationships surfaces anything a case-centric
  model misses, on realistic synthetic transformer-manufacturing data.

### What We Should Not Build Yet

- A full-factory digital twin.
- Any product claim of IEC/IEEE standards-compliance determination.
- A general-purpose, cross-ERP Execution Management System competing
  directly with Celonis/SAP Signavio on breadth.
- An LLM reasoning layer that calculates metrics itself or reasons over raw
  data rather than structured, confidence-scored outputs.

### Proposed Next Gate

The smallest experiment that would reduce the most important remaining
uncertainty is:

> **Reproduce a case-centric process-mining discovery + conformance +
> performance analysis (Gate 2, as already planned) using a public
> manufacturing event-log dataset that includes deliberately incomplete /
> milestone-only event coverage** (or a synthetically degraded version of a
> complete public dataset), and evaluate: (a) whether PM4Py's discovery and
> conformance results remain usable under that degradation, and (b) what a
> first-cut Evidence/Data Reliability Layer should report when they don't.

This directly tests the single largest uncertainty identified in this
gate — whether the sparse data conditions documented as typical for medium
manufacturers (evidence #12) still allow useful process-intelligence
output — before any further architectural or product commitment is made.
This is consistent with Gate 2 as already planned in README.md §12 and
does not require starting Gate 3 or later.
