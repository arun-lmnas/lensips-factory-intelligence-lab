"""
Gate 4b: object-centric manufacturing intelligence research, re-run on a
real multi-object dataset.

This supersedes the Gate 4 v1 experiment (reports/GATE4_MULTI_OBJECT_RECONNAISSANCE.md),
whose machine-shop event log was judged too case-centric (no real material/
supplier/quality objects) to properly test the object-centric hypothesis.
That report and its conclusions are NOT rewritten or defended here -- this
is a fresh experiment on a different, genuinely multi-object dataset.

Dataset: a real-data subsample of the BPI Challenge 2019 OCEL log
(purchase-to-pay process of a real coatings/paints manufacturer), built by
experiments/gate4b_object_centric_research/scripts/build_sample.py. See
reports/GATE4_DATASET_SELECTION.md for full provenance and sampling method.
Object types: PO (purchase order), POItem (purchase order line item),
Vendor (supplier), Resource (the user/batch process that performed an
event). This is a genuine OCEL 1.0 log, loaded with pm4py.read_ocel, not a
pandas table reshaped to look like one.

Structure:
  Part A - load + describe the OCEL
  Part B - case-centric baseline (OCEL flattened to POItem-level traditional
           event log; genuine PM4Py process discovery/conformance/performance)
  Part C - object-centric analysis (genuine PM4Py OCEL functions: OC-DFG,
           object interaction graph, connected components)
  Part D - evidence degradation scenario (Gate 2 principle, re-tested here)
  Part E - evidence-grounded findings gated by coverage (Gate 3 principle,
           re-tested here)
  Part F - explicit PM4Py/OCEL contribution log for every finding

No LLM, no digital twin, no transformer ontology, no external benchmarking,
no production integration. Reused Gate 2/3 principles are re-implemented
against this dataset's actual schema, not copy-pasted from the old script
(the old script's coverage checks were specific to the machine-shop CSV's
columns and do not apply here).
"""
import json
import random
from collections import defaultdict
from pathlib import Path

import pandas as pd
import pm4py

SAMPLE_PATH = Path("/workspace/datasets/bpic2019_ocel/sample/BPIC19_sample.jsonocel")
RESULTS_DIR = Path("/workspace/experiments/gate4b_object_centric_research/results")

PM4PY_CONTRIBUTIONS = []  # populated as we go; written to results.json Part F


def log_contribution(part: str, finding: str, api_calls: list, would_pandas_suffice: bool, note: str):
    PM4PY_CONTRIBUTIONS.append({
        "part": part,
        "finding": finding,
        "pm4py_api_calls": api_calls,
        "would_ordinary_pandas_groupby_join_suffice": would_pandas_suffice,
        "classification": "ordinary relational analytics" if would_pandas_suffice else "genuine process-mining/OCEL finding",
        "note": note,
    })


# ---------------------------------------------------------------------------
# Part A
# ---------------------------------------------------------------------------

def load_and_describe():
    ocel = pm4py.read_ocel(str(SAMPLE_PATH))
    summary = {
        "n_events": len(ocel.events),
        "n_objects": len(ocel.objects),
        "n_activities": ocel.events["ocel:activity"].nunique(),
        "object_type_counts": ocel.objects["ocel:type"].value_counts().to_dict(),
        "activity_counts": ocel.events["ocel:activity"].value_counts().to_dict(),
        "timestamp_min": str(ocel.events["ocel:timestamp"].min()),
        "timestamp_max": str(ocel.events["ocel:timestamp"].max()),
    }
    return ocel, summary


# ---------------------------------------------------------------------------
# Part B: case-centric baseline
# ---------------------------------------------------------------------------

def case_centric_baseline(ocel):
    # Flatten to the natural case notion for this process: the purchase
    # order line item (POItem). pm4py.ocel_flattening produces a standard
    # xes-style event log/dataframe indexed by that object type's cases.
    flat = pm4py.ocel_flattening(ocel, "POItem")
    flat = pm4py.format_dataframe(flat, case_id="case:concept:name",
                                   activity_key="concept:name", timestamp_key="time:timestamp") \
        if "case:concept:name" in flat.columns else flat

    n_cases = flat["case:concept:name"].nunique()

    # Genuine PM4Py process discovery (Inductive Miner) + token-based
    # replay conformance -- not a pandas reimplementation.
    net, im, fm = pm4py.discover_petri_net_inductive(flat)
    fitness = pm4py.fitness_token_based_replay(flat, net, im, fm)

    # Genuine PM4Py performance DFG: mean/median sojourn time between
    # directly-following activities, case-flattened.
    perf_dfg, start_acts, end_acts = pm4py.discover_performance_dfg(flat)
    perf_edges = sorted(
        [{"from": a, "to": b, "mean_seconds": v.get("mean"), "median_seconds": v.get("median")}
         for (a, b), v in perf_dfg.items()],
        key=lambda e: -(e["mean_seconds"] or 0),
    )[:10]

    # Case duration distribution
    case_durations = flat.groupby("case:concept:name")["time:timestamp"].agg(["min", "max"])
    case_durations["duration_days"] = (case_durations["max"] - case_durations["min"]).dt.total_seconds() / 86400.0

    # Activity frequency (case-centric: summed within the flattened log,
    # cannot see whether high-frequency activities cluster on a few shared
    # vendors/resources across DIFFERENT POItems)
    activity_freq = flat["concept:name"].value_counts().head(10).to_dict()

    log_contribution(
        part="B (case-centric baseline)",
        finding="Process model (Petri net), token-based-replay fitness, and performance DFG for the POItem-flattened log",
        api_calls=["pm4py.ocel_flattening", "pm4py.discover_petri_net_inductive", "pm4py.fitness_token_based_replay", "pm4py.discover_performance_dfg"],
        would_pandas_suffice=False,
        note="Inductive-miner process discovery and token-based-replay fitness are genuine process-mining algorithms with no direct pandas equivalent; this part is standard single-case-notion process mining, applied here as the baseline the object-centric part is compared against.",
    )

    return {
        "n_cases_poitem": int(n_cases),
        "petri_net_places": len(net.places),
        "petri_net_transitions": len(net.transitions),
        "token_based_replay_fitness": {k: (float(v) if isinstance(v, (int, float)) else v) for k, v in fitness.items()},
        "top10_slowest_directly_follows_edges": perf_edges,
        "case_duration_days": {
            "mean": round(case_durations["duration_days"].mean(), 1),
            "median": round(case_durations["duration_days"].median(), 1),
            "max": round(case_durations["duration_days"].max(), 1),
        },
        "top10_activities": activity_freq,
        "limitations": [
            "The flattened log treats every POItem as an independent case: it has no way to represent that many "
            "different POItems share the same Vendor or the same processing Resource, so it cannot show whether "
            "delays or workload cluster on a shared object across cases.",
            "Token-based-replay fitness and the performance DFG summarise the SINGLE chosen object type (POItem); "
            "flattening on a different object type (e.g. Vendor) would silently produce a structurally different "
            "process model from the same underlying data, and the case-centric view gives no signal that this "
            "choice matters.",
            "A Vendor or Resource involved in many POItems' events appears only implicitly, as a repeated attribute "
            "value on many independent cases -- there is no object-level view of it.",
        ],
    }


# ---------------------------------------------------------------------------
# Part C: object-centric analysis
# ---------------------------------------------------------------------------

def object_centric_analysis(ocel):
    # Genuine OC-DFG: directly-follows relations broken down per object type,
    # not collapsed onto one case notion.
    ocdfg = pm4py.discover_ocdfg(ocel)
    ocdfg_object_types = sorted(ocdfg.get("object_types", []))
    # Number of DISTINCT directly-follows activity-pairs observed per object
    # type -- i.e. how much more varied the process looks depending on
    # which object type's "thread" you follow through the same events.
    ocdfg_distinct_df_pairs_per_type = {
        ot: len(pairs) for ot, pairs in ocdfg.get("edges", {}).get("event_couples", {}).items()
    }

    log_contribution(
        part="C (object-centric: OC-DFG)",
        finding="Object-centric directly-follows graph across all 4 object types simultaneously",
        api_calls=["pm4py.discover_ocdfg"],
        would_pandas_suffice=False,
        note="The OC-DFG discovery algorithm computes per-object-type directly-follows relations and their "
             "interplay natively from the OCEL event-object mapping; reproducing it with pandas would require "
             "re-implementing the OCEL directly-follows semantics (per-object-type sequencing) from scratch, not "
             "just a group-by.",
    )

    # Genuine object interaction graph: which OBJECTS (not object types) are
    # connected because they co-occur in the same event.
    edges = pm4py.discover_objects_graph(ocel, graph_type="object_interaction")
    obj_type = dict(zip(ocel.objects["ocel:oid"].astype(str), ocel.objects["ocel:type"]))

    degree = defaultdict(int)
    cross_type_edges_by_pair = defaultdict(int)
    for a, b in edges:
        degree[a] += 1
        degree[b] += 1
        ta, tb = obj_type.get(a, "?"), obj_type.get(b, "?")
        cross_type_edges_by_pair[tuple(sorted((ta, tb)))] += 1

    vendor_degree = sorted(
        [{"object_id": oid, "degree": d} for oid, d in degree.items() if obj_type.get(oid) == "Vendor"],
        key=lambda x: -x["degree"],
    )[:10]
    resource_degree = sorted(
        [{"object_id": oid, "degree": d} for oid, d in degree.items() if obj_type.get(oid) == "Resource"],
        key=lambda x: -x["degree"],
    )[:10]

    log_contribution(
        part="C (object-centric: object interaction graph)",
        finding="Vendor/Resource objects ranked by how many other objects (POs, POItems, other resources) they co-occur with in events",
        api_calls=["pm4py.discover_objects_graph(graph_type='object_interaction')"],
        would_pandas_suffice=True,
        note="This specific ranking COULD be reproduced with a pandas group-by on the event-object mapping "
             "(count distinct co-occurring object ids per Vendor/Resource). It is reported here as ORDINARY "
             "RELATIONAL ANALYTICS made convenient by pm4py's object graph API, not as evidence unique to OCEL. "
             "The genuinely OCEL-native step is the interaction-graph CONSTRUCTION itself and the connected-"
             "component analysis below (Part C, connected components), which does not reduce to a simple group-by.",
    )

    # Connected components of the object interaction graph: does the whole
    # dataset collapse into a few giant components (shared vendors/resources
    # link almost everything), or stay in many small independent components
    # (the case-centric independence assumption roughly holds)?
    import networkx as nx  # transitively available via pm4py's own deps
    G = nx.Graph()
    G.add_edges_from(edges)
    components = list(nx.connected_components(G))
    po_objects = set(oid for oid, t in obj_type.items() if t == "PO")
    component_sizes = sorted([len(c) for c in components], reverse=True)
    largest_component_po_count = len(components[0] & po_objects) if components else 0
    n_singleton = sum(1 for c in components if len(c) == 1)

    log_contribution(
        part="C (object-centric: connected components)",
        finding="Whether the object interaction graph decomposes into many small independent components or a few giant ones",
        api_calls=["pm4py.discover_objects_graph", "networkx.connected_components (over the pm4py-produced edge set)"],
        would_pandas_suffice=False,
        note="Connected-component analysis over an object-relationship graph is not a group-by or join; it is a "
             "graph-structural question (transitive reachability through shared objects) that pandas alone cannot "
             "answer without effectively re-implementing graph traversal. This is the clearest genuinely "
             "OCEL-native finding in this experiment.",
    )

    return {
        "ocdfg_object_types_covered": ocdfg_object_types,
        "ocdfg_distinct_directly_follows_pairs_per_object_type": ocdfg_distinct_df_pairs_per_type,
        "n_object_interaction_edges": len(edges),
        "cross_object_type_edge_counts": {f"{a}-{b}": c for (a, b), c in cross_type_edges_by_pair.items()},
        "top10_vendors_by_connection_degree": vendor_degree,
        "top10_resources_by_connection_degree": resource_degree,
        "connected_components": {
            "n_components": len(components),
            "n_singleton_components": n_singleton,
            "largest_component_size": component_sizes[0] if component_sizes else 0,
            "largest_component_n_distinct_pos": largest_component_po_count,
            "top10_component_sizes": component_sizes[:10],
        },
    }


# ---------------------------------------------------------------------------
# Part D: evidence degradation (Gate 2 principle, re-tested on this dataset)
# ---------------------------------------------------------------------------

def evidence_degradation(ocel):
    """The README documents that item category determines which evidence
    events MUST exist for a compliant purchase item:
      - '3-way match, invoice after GR' requires a Goods Receipt AND an
        invoice event, goods receipt first.
      - '3-way match, invoice before GR' requires the same two events but
        permits invoice before goods receipt.
      - 'Consignment' requires no invoice event on the PO (handled elsewhere).
    We measure real per-item-category evidence coverage on the untouched
    sample, then synthetically remove Goods Receipt events for a subset of
    items (as Gate 2 removed quality-inspection events) and re-measure
    whether case-centric process metrics (fitness, throughput time) still
    look normal despite the missing evidence category -- the Gate 2 test,
    reapplied to a dataset where "evidence category" now means a purchase
    compliance event, not a shop-floor QC event."""
    ev = ocel.events.copy()

    GR_ACTS = {"Record Goods Receipt", "Cancel Goods Receipt"}
    INV_ACTS = {"Record Invoice Receipt", "Vendor creates invoice", "Cancel Invoice Receipt"}

    per_item = ev.groupby("cID").agg(item_cat=("cItemCat", "first"))
    has_gr = ev[ev["ocel:activity"].isin(GR_ACTS)]["cID"].unique()
    has_inv = ev[ev["ocel:activity"].isin(INV_ACTS)]["cID"].unique()
    per_item["has_gr_event"] = per_item.index.isin(has_gr)
    per_item["has_inv_event"] = per_item.index.isin(has_inv)

    coverage_by_category = {}
    for cat, g in per_item.groupby("item_cat"):
        requires_gr = cat in ("3-way match, invoice after GR", "3-way match, invoice before GR")
        n = len(g)
        n_with_gr = int(g["has_gr_event"].sum())
        coverage_by_category[cat] = {
            "n_items": n,
            "requires_gr_event_per_readme": requires_gr,
            "n_items_with_gr_event": n_with_gr,
            "gr_coverage_pct": round(100.0 * n_with_gr / n, 1) if n else None,
            "n_items_with_invoice_event": int(g["has_inv_event"].sum()),
        }

    # --- Synthetic degradation: remove GR events for a random 30% of
    # 3-way-match items (documented, not silently mixed with real data) ---
    rng = random.Random(7)
    three_way_items = per_item[per_item["item_cat"].isin(
        ["3-way match, invoice after GR", "3-way match, invoice before GR"])].index.tolist()
    degraded_items = set(rng.sample(three_way_items, k=max(1, int(0.3 * len(three_way_items)))))

    ev_degraded = ev[~(ev["cID"].isin(degraded_items) & ev["ocel:activity"].isin(GR_ACTS))].copy()

    def flat_fitness(events_df):
        tmp_ocel = pm4py.objects.ocel.obj.OCEL(events=events_df, objects=ocel.objects, relations=ocel.relations[ocel.relations["ocel:eid"].isin(events_df["ocel:eid"])])
        flat = pm4py.ocel_flattening(tmp_ocel, "POItem")
        net, im, fm = pm4py.discover_petri_net_inductive(flat)
        fitness = pm4py.fitness_token_based_replay(flat, net, im, fm)
        return {k: (float(v) if isinstance(v, (int, float)) else v) for k, v in fitness.items()}

    fitness_original = flat_fitness(ev)
    fitness_degraded = flat_fitness(ev_degraded)

    # Coverage check (Gate 2/3 style): fraction of 3-way-match items with a
    # GR event, before/after degradation.
    def gr_coverage(events_df, items):
        has = events_df[events_df["ocel:activity"].isin(GR_ACTS)]["cID"].unique()
        n_with = sum(1 for i in items if i in has)
        return round(100.0 * n_with / len(items), 1) if items else None

    log_contribution(
        part="D (evidence degradation)",
        finding="Whether case-centric process fitness stays high even when a required evidence category (Goods Receipt events) is synthetically removed for a documented subset of items",
        api_calls=["pm4py.ocel_flattening", "pm4py.discover_petri_net_inductive", "pm4py.fitness_token_based_replay"],
        would_pandas_suffice=False,
        note="Re-tests the Gate 2 conclusion (process-mining fitness is not a completeness/reliability metric) "
             "against this dataset's own documented compliance-evidence requirement (item category -> required "
             "event types), rather than reusing the machine-shop dataset's QC-activity coverage check.",
    )

    return {
        "coverage_by_item_category_original": coverage_by_category,
        "degradation_scenario": {
            "description": "Goods Receipt events (Record/Cancel Goods Receipt) removed for a random 30% "
                            "of 3-way-match items (both invoice-before-GR and invoice-after-GR categories).",
            "n_three_way_items": len(three_way_items),
            "n_items_degraded": len(degraded_items),
            "gr_coverage_pct_before": gr_coverage(ev, three_way_items),
            "gr_coverage_pct_after": gr_coverage(ev_degraded, three_way_items),
            "token_based_replay_fitness_before": fitness_original,
            "token_based_replay_fitness_after": fitness_degraded,
        },
    }


# ---------------------------------------------------------------------------
# Part E: evidence-grounded findings (Gate 3 principle, re-tested)
# ---------------------------------------------------------------------------

SEVERE_THRESHOLD_PCT = 20.0
MEDIUM_THRESHOLD_PCT = 70.0


def coverage_flag(expected: int, observed: int) -> dict:
    coverage_pct = round(100.0 * observed / expected, 1) if expected > 0 else None
    if expected == 0:
        flag = "NOT_APPLICABLE"
    elif observed == 0:
        flag = "MISSING"
    elif coverage_pct < SEVERE_THRESHOLD_PCT:
        flag = "SEVERELY_DEGRADED"
    elif coverage_pct < MEDIUM_THRESHOLD_PCT:
        flag = "PARTIAL"
    else:
        flag = "OK"
    return {"expected": expected, "observed": observed, "coverage_pct": coverage_pct, "flag": flag}


def evidence_grounded_findings(ocel, degradation_result):
    ev = ocel.events
    findings = []

    # Question 1: which vendor is associated with abnormal cycle time?
    # Evidence requirement: vendor must have events on >= 5 distinct POItems
    # to say anything about its "typical" cycle time.
    merged = ev.merge(ev.groupby("cID")["ocel:timestamp"].agg(["min", "max"]).rename(
        columns={"min": "item_start", "max": "item_end"}), on="cID")
    item_vendor = ev.groupby("cID")["cVendorName"].first()
    item_duration = ev.groupby("cID")["ocel:timestamp"].agg(lambda s: (s.max() - s.min()).total_seconds() / 86400.0)
    vendor_stats = pd.DataFrame({"vendor": item_vendor, "duration_days": item_duration}).groupby("vendor").agg(
        n_items=("duration_days", "count"), mean_duration_days=("duration_days", "mean"))
    all_vendor_count = vendor_stats.shape[0]
    vendor_stats = vendor_stats[vendor_stats["n_items"] >= 5].sort_values("mean_duration_days", ascending=False)
    # Coverage here means: how many of all distinct vendors in the sample have
    # enough items (>=5) to say anything about their typical cycle time.
    cov1 = coverage_flag(expected=all_vendor_count, observed=int(vendor_stats.shape[0]))
    findings.append({
        "question": "Which vendor is associated with abnormally long purchase-item cycle time?",
        "evidence_requirement": ">=5 items per vendor to compute a meaningful mean cycle time",
        "coverage": cov1,
        "confidence": "MEDIUM" if cov1["flag"] == "OK" else "LOW",
        "top5_slowest_vendors": vendor_stats.head(5).reset_index().to_dict(orient="records"),
        "limitation": "Vendor cycle time here is confounded with item category and spend area, which we did not "
                      "control for; this is a candidate signal, not an attributed root cause.",
    })

    # Question 2: is 3-way-match compliance broken for a given item category,
    # gated on the Part D coverage/degradation result.
    cov_by_cat = degradation_result["coverage_by_item_category_original"]
    compliance_finding = []
    for cat, stats in cov_by_cat.items():
        if not stats["requires_gr_event_per_readme"]:
            continue
        flag = coverage_flag(expected=stats["n_items"], observed=stats["n_items_with_gr_event"])
        status = "WITHHELD" if flag["flag"] in ("MISSING", "SEVERELY_DEGRADED") else (
            "MEDIUM_CONFIDENCE" if flag["flag"] == "PARTIAL" else "HIGH_CONFIDENCE")
        compliance_finding.append({"item_category": cat, "coverage": flag, "status": status})
    findings.append({
        "question": "Is 3-way-match compliance (Goods Receipt required before/alongside invoice) satisfied for each item category?",
        "evidence_requirement": "Every 3-way-match item must have >=1 Goods Receipt event per the dataset's own documented process rules",
        "per_category_result": compliance_finding,
        "note": "This question is answered from the dataset's OWN documented compliance rule (README.txt), not an invented threshold.",
    })

    # Question 3 (deliberately withheld): does a delay in one PO propagate
    # to another PO through a shared vendor or resource? Evidence
    # requirement: a genuine queue/scheduling signal, which this OCEL does
    # NOT contain (only event timestamps, no resource-occupancy log).
    findings.append({
        "question": "Does a delay in one PO propagate to another PO through a shared vendor or shared processing resource?",
        "evidence_requirement": "A resource-occupancy or workload-queue signal showing the shared object was busy/blocked, not just that it is connected to many objects",
        "coverage": {"expected": "resource-occupancy signal", "observed": "none in this OCEL", "flag": "MISSING"},
        "confidence": "WITHHELD",
        "note": "The object interaction graph (Part C) shows WHICH POs share a vendor/resource, but this OCEL has "
                "no signal of workload or queueing pressure on that shared object, so propagation cannot be "
                "demonstrated here. Recorded as WITHHELD rather than inferred from co-occurrence alone.",
    })

    log_contribution(
        part="E (evidence-grounded findings)",
        finding="Confidence gating for 3 factory-adjacent questions, one deliberately withheld for insufficient evidence",
        api_calls=["(built on Part B/C/D outputs; no new pm4py call)"],
        would_pandas_suffice=True,
        note="The confidence-gating logic itself is ordinary control flow over already-computed coverage numbers, "
             "same as Gate 3's mechanism; it is not the source of the OCEL-specific finding, but it structures how "
             "the finding is reported.",
    )

    return findings


def main():
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    ocel, summary = load_and_describe()
    print("Loaded OCEL:", summary["n_events"], "events,", summary["n_objects"], "objects")

    baseline = case_centric_baseline(ocel)
    print("Case-centric baseline done")

    obj_centric = object_centric_analysis(ocel)
    print("Object-centric analysis done")

    degradation = evidence_degradation(ocel)
    print("Evidence degradation scenario done")

    findings = evidence_grounded_findings(ocel, degradation)
    print("Evidence-grounded findings done")

    results = {
        "dataset_summary": summary,
        "part_b_case_centric_baseline": baseline,
        "part_c_object_centric_analysis": obj_centric,
        "part_d_evidence_degradation": degradation,
        "part_e_evidence_grounded_findings": findings,
        "part_f_pm4py_ocel_contributions": PM4PY_CONTRIBUTIONS,
    }

    out_path = RESULTS_DIR / "results.json"
    out_path.write_text(json.dumps(results, indent=2, default=str))
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
