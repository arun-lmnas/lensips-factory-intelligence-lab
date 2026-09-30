"""
Gate 4 experiment: multi-object manufacturing intelligence reconnaissance.

Scope (see README.md section 12 and the Gate 4 task brief this script was
written against): a small, terminating reconnaissance experiment on the
existing Gate 2/3 dataset (datasets/production_analysis/Production_Data.csv)
to test whether modelling relationships *between* manufacturing objects
(order, product, operation, machine, worker, quality event) surfaces
questions that a conventional order/case-centric process view cannot answer,
and whether that additional intelligence is worth the added modelling
complexity.

This script does NOT build an OCEL framework, a digital twin, or a reusable
multi-object model. It computes a fixed set of case-centric and multi-object
metrics directly with pandas over the one available event log and writes
them to results/results.json for the Gate 4 report to cite. No new dataset
was fabricated: the dataset already exposes order (Case ID), product (Part
Desc.), operation (Activity), machine (Resource) and quality-event (Q.C./
Rework/Qty Rejected/Qty for MRB) objects without synthetic extension. It has
no supplier or material-lot fields; questions that depend on those objects
are marked NOT_DEMONSTRATED rather than answered with invented data.
"""
import json
from pathlib import Path

import pandas as pd

DATA_PATH = Path("/workspace/datasets/production_analysis/Production_Data.csv")
RESULTS_DIR = Path("/workspace/experiments/gate4_multi_object_reconnaissance/results")

QC_SUBSTRINGS = ["Q.C.", "Inspection", "Nitration Q.C.", "Round  Q.C."]


def load() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH)
    df["Start Timestamp"] = pd.to_datetime(df["Start Timestamp"], format="mixed")
    df["Complete Timestamp"] = pd.to_datetime(df["Complete Timestamp"], format="mixed")
    df["Rework"] = df["Rework"].fillna("").str.strip().eq("Y")
    df["is_qc"] = df["Activity"].str.contains("|".join(QC_SUBSTRINGS), case=False, na=False)
    return df


# ---------------------------------------------------------------------------
# Part 1: case-centric baseline
# ---------------------------------------------------------------------------

def case_centric_baseline(df: pd.DataFrame) -> dict:
    per_case = df.groupby("Case ID").agg(
        n_events=("Activity", "count"),
        start=("Start Timestamp", "min"),
        end=("Complete Timestamp", "max"),
        n_distinct_resources=("Resource", "nunique"),
        n_distinct_activities=("Activity", "nunique"),
    )
    per_case["duration_hours"] = (per_case["end"] - per_case["start"]).dt.total_seconds() / 3600.0

    df = df.copy()
    df["event_hours"] = (df["Complete Timestamp"] - df["Start Timestamp"]).dt.total_seconds() / 3600.0
    activity_time = df.groupby("Activity")["event_hours"].sum().sort_values(ascending=False)
    resource_time = df.groupby("Resource")["event_hours"].sum().sort_values(ascending=False)

    # within-case waiting time: gap between one event's Complete and the next
    # event's Start, computed per case on chronologically sorted events.
    gaps = []
    for case_id, g in df.sort_values("Start Timestamp").groupby("Case ID"):
        g = g.sort_values("Start Timestamp").reset_index(drop=True)
        for i in range(1, len(g)):
            gap_h = (g.loc[i, "Start Timestamp"] - g.loc[i - 1, "Complete Timestamp"]).total_seconds() / 3600.0
            if gap_h > 0:
                gaps.append({
                    "case_id": case_id,
                    "gap_hours": round(gap_h, 2),
                    "after_activity": g.loc[i - 1, "Activity"],
                    "after_resource": g.loc[i - 1, "Resource"],
                    "before_activity": g.loc[i, "Activity"],
                    "before_resource": g.loc[i, "Resource"],
                    "gap_start": g.loc[i - 1, "Complete Timestamp"].isoformat(),
                    "gap_end": g.loc[i, "Start Timestamp"].isoformat(),
                })
    gaps_df = pd.DataFrame(gaps)

    return {
        "n_cases": int(per_case.shape[0]),
        "n_events": int(df.shape[0]),
        "order_duration_hours": {
            "mean": round(per_case["duration_hours"].mean(), 1),
            "median": round(per_case["duration_hours"].median(), 1),
            "max": round(per_case["duration_hours"].max(), 1),
            "top5_longest_cases": per_case["duration_hours"].sort_values(ascending=False).head(5).round(1).to_dict(),
        },
        "top10_activities_by_total_hours": activity_time.head(10).round(1).to_dict(),
        "top10_resources_by_total_hours": resource_time.head(10).round(1).to_dict(),
        "n_within_case_gaps": int(len(gaps_df)),
        "top10_longest_within_case_gaps": (
            gaps_df.sort_values("gap_hours", ascending=False).head(10).to_dict(orient="records")
            if not gaps_df.empty else []
        ),
        "limitations": [
            "Each case is analysed in isolation: this view has no mechanism to detect "
            "whether a within-case waiting gap is caused by a resource being busy on a "
            "different order, a genuine idle period, or something else.",
            "Resource/activity totals are summed per activity label across all cases, but "
            "the case-centric view gives no way to see whether high resource-time is "
            "concentrated on a few contended machines or spread evenly.",
            "No visibility into whether a quality issue recurs for a specific "
            "product-machine or worker-machine combination across different orders, "
            "since each case is a closed unit.",
        ],
    }, gaps_df


# ---------------------------------------------------------------------------
# Part 2: multi-object analysis
# ---------------------------------------------------------------------------

def machine_contention(df: pd.DataFrame) -> dict:
    """For each Resource (machine/work-centre object), find event pairs from
    *different* Case IDs (order objects) whose [Start, Complete) intervals
    overlap in wall-clock time. This is a cross-order relationship that is
    invisible from any single case's process view."""
    results = {}
    for resource, g in df.groupby("Resource"):
        g = g.sort_values("Start Timestamp").reset_index(drop=True)
        overlap_hours = 0.0
        overlap_pairs = set()
        intervals = list(zip(g["Start Timestamp"], g["Complete Timestamp"], g["Case ID"]))
        # sweep: O(n log n) via sorted starts, compare against active set
        active = []
        for start, end, case_id in intervals:
            active = [a for a in active if a[1] > start]
            for a_start, a_end, a_case in active:
                if a_case != case_id:
                    ov_start = max(start, a_start)
                    ov_end = min(end, a_end)
                    ov_h = (ov_end - ov_start).total_seconds() / 3600.0
                    if ov_h > 0:
                        overlap_hours += ov_h
                        overlap_pairs.add(tuple(sorted((case_id, a_case))))
            active.append((start, end, case_id))
        n_cases_on_resource = g["Case ID"].nunique()
        if overlap_hours > 0 or n_cases_on_resource > 1:
            results[resource] = {
                "n_distinct_cases_using_resource": int(n_cases_on_resource),
                "n_cross_order_overlapping_pairs": len(overlap_pairs),
                "total_cross_order_overlap_hours": round(overlap_hours, 1),
            }
    return dict(sorted(results.items(), key=lambda kv: -kv[1]["total_cross_order_overlap_hours"]))


def quality_by_product_machine(df: pd.DataFrame) -> dict:
    """Aggregates reject/MRB/rework across ALL orders for a given
    (product, machine) pair -- a relationship a single case-centric view
    cannot surface because it never compares across orders."""
    g = df.groupby(["Part Desc.", "Resource"]).agg(
        n_orders=("Case ID", "nunique"),
        n_events=("Activity", "count"),
        qty_rejected=("Qty Rejected", "sum"),
        qty_mrb=("Qty for MRB", "sum"),
        n_rework_events=("Rework", "sum"),
    ).reset_index()
    g = g[(g["qty_rejected"] > 0) | (g["qty_mrb"] > 0) | (g["n_rework_events"] > 0)]
    g = g.sort_values(["qty_rejected", "n_rework_events"], ascending=False)
    return g.head(15).to_dict(orient="records")


def worker_machine_reject_rate(df: pd.DataFrame) -> dict:
    g = df.groupby(["Worker ID", "Resource"]).agg(
        n_events=("Activity", "count"),
        qty_completed=("Qty Completed", "sum"),
        qty_rejected=("Qty Rejected", "sum"),
    ).reset_index()
    g = g[g["n_events"] >= 5]
    g["reject_rate_pct"] = (100.0 * g["qty_rejected"] / (g["qty_completed"] + g["qty_rejected"]).clip(lower=1)).round(1)
    g = g.sort_values("reject_rate_pct", ascending=False)
    return g.head(10).to_dict(orient="records")


def shared_resource_delay_attribution(gaps_df: pd.DataFrame, contention: dict) -> dict:
    """Of the within-case waiting gaps found in the case-centric baseline,
    how many occur on a resource this experiment independently flags as
    cross-order-contended? This tests whether "the order was just slow" and
    "the order was waiting on a machine another order was occupying" are
    distinguishable -- a case-centric view cannot make this distinction."""
    if gaps_df.empty:
        return {"n_gaps_total": 0, "n_gaps_on_contended_resource": 0}
    contended_resources = set(contention.keys())
    gaps_df = gaps_df.copy()
    gaps_df["before_resource_contended"] = gaps_df["before_resource"].isin(contended_resources)
    on_contended = gaps_df[gaps_df["before_resource_contended"]]
    return {
        "n_gaps_total": int(len(gaps_df)),
        "n_gaps_on_contended_resource": int(len(on_contended)),
        "total_gap_hours_on_contended_resource": round(on_contended["gap_hours"].sum(), 1),
        "total_gap_hours_all": round(gaps_df["gap_hours"].sum(), 1),
        "caveat": (
            "This is a coincidence check (gap precedes an event on a resource this "
            "script separately flags as cross-order-contended), not a proven causal "
            "link -- the waiting order and the contending order are not shown to be "
            "queued for the SAME resource slot at the SAME time. See Evidence "
            "Reliability in the report."
        ),
    }


def cross_order_shared_bottleneck(df: pd.DataFrame) -> dict:
    """Which resources are heavily used across many DISTINCT products/orders
    (a genuine shared-resource bottleneck) vs. resources whose time is
    concentrated in one product family (an order/product-specific cost, not
    a shared-resource issue). Case-centric view cannot make this
    distinction since it never aggregates across cases."""
    df = df.copy()
    df["event_hours"] = (df["Complete Timestamp"] - df["Start Timestamp"]).dt.total_seconds() / 3600.0
    g = df.groupby("Resource").agg(
        total_hours=("event_hours", "sum"),
        n_distinct_products=("Part Desc.", "nunique"),
        n_distinct_orders=("Case ID", "nunique"),
    ).reset_index()
    g = g.sort_values("total_hours", ascending=False)
    return g.head(10).to_dict(orient="records")


# ---------------------------------------------------------------------------
# Part 5: evidence reliability (Gate 2/3 category-coverage principle, reused)
# ---------------------------------------------------------------------------

def evidence_reliability(df: pd.DataFrame) -> dict:
    n_cases = df["Case ID"].nunique()
    cases_with_qc = df[df["is_qc"]]["Case ID"].nunique()
    return {
        "quality_event_coverage": {
            "n_cases_total": int(n_cases),
            "n_cases_with_at_least_one_qc_event": int(cases_with_qc),
            "coverage_pct": round(100.0 * cases_with_qc / n_cases, 1),
            "note": "Reuses the Gate 2/3 category-coverage check: presence of Q.C.-labelled "
                    "activities per case, not an assumption that all quality outcomes are logged.",
        },
        "material_and_supplier_objects": {
            "present_in_dataset": False,
            "note": "Production_Data.csv has no material-lot, BOM, or supplier fields. Any "
                    "finding that would require them is marked NOT_DEMONSTRATED, not answered "
                    "with fabricated data, per the Gate 4 boundary against inventing customer data.",
        },
        "machine_contention_evidence": {
            "note": "Contention is inferred purely from Start/Complete timestamp overlap on the "
                    "same Resource across different Case IDs. The dataset has no explicit queue, "
                    "scheduling, or resource-lock log, so overlap is a proxy for contention, not "
                    "a direct observation of a queueing event. Two overlapping intervals on one "
                    "named resource could also reflect a data-entry granularity artefact (e.g. "
                    "timestamps rounded to the same minute) rather than genuine simultaneous "
                    "physical use -- not independently verifiable from this dataset alone.",
        },
        "worker_reject_rate_evidence": {
            "note": "Qty Rejected is attributed to the (Worker ID, Resource) pair active on that "
                    "event row. The dataset does not distinguish worker-caused rejects from "
                    "machine-caused or material-caused rejects, so this is a correlation, not an "
                    "attributed root cause.",
        },
    }


def main():
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    df = load()

    baseline, gaps_df = case_centric_baseline(df)
    contention = machine_contention(df)
    quality_pm = quality_by_product_machine(df)
    worker_mc = worker_machine_reject_rate(df)
    delay_attr = shared_resource_delay_attribution(gaps_df, contention)
    shared_bottleneck = cross_order_shared_bottleneck(df)
    reliability = evidence_reliability(df)

    results = {
        "dataset": {
            "path": "datasets/production_analysis/Production_Data.csv",
            "n_rows": int(df.shape[0]),
            "n_cases": int(df["Case ID"].nunique()),
            "n_resources": int(df["Resource"].nunique()),
            "n_products": int(df["Part Desc."].nunique()),
            "n_workers": int(df["Worker ID"].nunique()),
            "object_types_present": ["Order (Case ID)", "Product (Part Desc.)",
                                       "Operation (Activity)", "Machine/Resource",
                                       "Worker", "Quality event (Q.C./Rework/Reject/MRB)"],
            "object_types_absent": ["Material/BOM", "Supplier"],
        },
        "part1_case_centric_baseline": baseline,
        "part2_multi_object": {
            "machine_contention_cross_order": contention,
            "quality_by_product_machine_top15": quality_pm,
            "worker_machine_reject_rate_top10": worker_mc,
            "shared_resource_delay_attribution": delay_attr,
            "cross_order_shared_bottleneck_top10": shared_bottleneck,
        },
        "part5_evidence_reliability": reliability,
    }

    out_path = RESULTS_DIR / "results.json"
    out_path.write_text(json.dumps(results, indent=2, default=str))
    print(f"Wrote {out_path}")
    print(json.dumps({k: "..." for k in results}, indent=2))


if __name__ == "__main__":
    main()
