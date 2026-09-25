"""
Gate 2 experiment: does PM4Py process discovery, conformance, and performance
analysis stay useful when a real manufacturing event log is degraded to look
like the sparse, incomplete data a medium manufacturer is documented to
typically produce?

Dataset: "Production Analysis with Process Mining Technology" (Dafna Levy,
Eindhoven University of Technology, published via 4TU.ResearchData,
DOI 10.4121/uuid:68726926-5ac5-4fab-b873-ee76ea412399). A real machine-shop
production event log: 225 work orders (cases), 55 distinct
activities/operations across ~31 machines/resources, with explicit Start
and Complete timestamps per operation and quality fields (Qty Rejected,
Qty for MRB, Rework).

Method: discover a reference process model from the FULL (undegraded) log —
this stands in for "what actually happened." Then apply each degradation
scenario to a fresh copy of the raw event data, rebuild the log, and
measure: (a) conformance of the degraded log against the reference model,
(b) whether performance-analysis findings (bottleneck activity, case
duration) survive, and (c) how many cases/events are lost. Because the
underlying process did not change between scenarios, any degradation in
these numbers is attributable purely to the *data* becoming worse, not to
the *process* actually being different one that is the exact confusion a
factory-intelligence system must not silently make.

Run inside the Gate 0 devcontainer (has pm4py, pandas). Does not modify the
devcontainer or the smoke test.
"""
import json
import random
import sys
from pathlib import Path

import pandas as pd
import pm4py

RANDOM_SEED = 42
DATA_CSV = Path("/workspace/datasets/production_analysis/Production_Data.csv")
RESULTS_DIR = Path("/workspace/experiments/gate2_data_realism/results")

QUALITY_ACTIVITY_SUBSTRINGS = ["Q.C.", "Inspection", "MRB"]


def load_raw() -> pd.DataFrame:
    df = pd.read_csv(DATA_CSV)
    df["Start Timestamp"] = pd.to_datetime(df["Start Timestamp"], format="%Y/%m/%d %H:%M:%S.%f")
    df["Complete Timestamp"] = pd.to_datetime(df["Complete Timestamp"], format="%Y/%m/%d %H:%M:%S.%f")
    # canonical event order within a case, by completion time, ties broken by
    # original row order (stable sort preserves CSV order)
    df = df.sort_values(["Case ID", "Complete Timestamp"], kind="stable").reset_index(drop=True)
    return df


def to_event_log_df(df: pd.DataFrame) -> pd.DataFrame:
    formatted = pm4py.format_dataframe(
        df.copy(),
        case_id="Case ID",
        activity_key="Activity",
        timestamp_key="Complete Timestamp",
    )
    return formatted


# ---------------------------------------------------------------------------
# Degradation scenarios
# ---------------------------------------------------------------------------

def scenario_baseline(df: pd.DataFrame) -> pd.DataFrame:
    return df.copy()


def scenario_milestone_only(df: pd.DataFrame) -> pd.DataFrame:
    """Keep only the first and last recorded event per case: a coarse ERP
    milestone log ("order started" / "order finished"), as documented to be
    the status quo for many small/medium manufacturers."""
    out = []
    for _, g in df.groupby("Case ID", sort=False):
        g = g.sort_values("Complete Timestamp")
        if len(g) == 1:
            out.append(g)
        else:
            out.append(g.iloc[[0, -1]])
    return pd.concat(out, ignore_index=True)


def scenario_missing_timestamps(df: pd.DataFrame, frac: float = 0.3) -> pd.DataFrame:
    """Randomly drop the timestamp on a fraction of events. An event with no
    reliable timestamp cannot be ordered, so it is dropped from the log
    entirely (LENSIPS cannot place it in the sequence)."""
    rng = random.Random(RANDOM_SEED)
    n = len(df)
    drop_idx = set(rng.sample(range(n), int(n * frac)))
    keep_mask = [i not in drop_idx for i in range(n)]
    return df[keep_mask].reset_index(drop=True)


def scenario_missing_resource(df: pd.DataFrame, frac: float = 0.4) -> pd.DataFrame:
    """Null out the machine/resource identifier on a fraction of events.
    Events are kept (activity + timestamp still known), but resource-level
    analysis (which machine is the bottleneck) is degraded."""
    out = df.copy()
    rng = random.Random(RANDOM_SEED)
    n = len(out)
    idx = rng.sample(range(n), int(n * frac))
    out.loc[out.index[idx], "Resource"] = None
    return out


def scenario_incomplete_relationships(df: pd.DataFrame, frac: float = 0.3) -> pd.DataFrame:
    """Drop a fraction of *middle* events per case (never the first or last),
    simulating steps that simply never produced an event, while the case's
    start/end are still known."""
    rng = random.Random(RANDOM_SEED)
    out = []
    for _, g in df.groupby("Case ID", sort=False):
        g = g.sort_values("Complete Timestamp").reset_index(drop=True)
        if len(g) <= 2:
            out.append(g)
            continue
        middle_idx = list(range(1, len(g) - 1))
        n_drop = int(len(middle_idx) * frac)
        drop = set(rng.sample(middle_idx, n_drop)) if n_drop > 0 else set()
        keep = [i for i in range(len(g)) if i not in drop]
        out.append(g.iloc[keep])
    return pd.concat(out, ignore_index=True)


def scenario_inconsistent_records(df: pd.DataFrame, frac: float = 0.1) -> pd.DataFrame:
    """Introduce duplicate events with slightly perturbed timestamps and a
    few swapped (out-of-order) timestamps, simulating manually re-entered or
    conflicting records from disconnected systems."""
    rng = random.Random(RANDOM_SEED)
    out = df.copy()
    n = len(out)
    # duplicate a fraction of rows with a small time jitter
    dup_idx = rng.sample(range(n), int(n * frac))
    dups = out.loc[dup_idx].copy()
    dups["Complete Timestamp"] = dups["Complete Timestamp"] + pd.to_timedelta(
        [rng.randint(1, 5) for _ in range(len(dups))], unit="m"
    )
    out = pd.concat([out, dups], ignore_index=True)
    # swap start/complete on a small fraction to create logically impossible
    # (negative-duration) records
    swap_idx = rng.sample(range(len(out)), int(len(out) * 0.03))
    tmp_start = out.loc[swap_idx, "Start Timestamp"].copy()
    out.loc[swap_idx, "Start Timestamp"] = out.loc[swap_idx, "Complete Timestamp"]
    out.loc[swap_idx, "Complete Timestamp"] = tmp_start
    return out.sort_values(["Case ID", "Complete Timestamp"], kind="stable").reset_index(drop=True)


def scenario_missing_quality_events(df: pd.DataFrame) -> pd.DataFrame:
    """Drop every quality/inspection-related activity entirely, simulating a
    factory whose QMS is not connected to the systems LENSIPS can reach."""
    mask = ~df["Activity"].str.contains("|".join(QUALITY_ACTIVITY_SUBSTRINGS), case=False, na=False)
    return df[mask].reset_index(drop=True)


SCENARIOS = {
    "baseline": scenario_baseline,
    "milestone_only": scenario_milestone_only,
    "missing_timestamps_30pct": scenario_missing_timestamps,
    "missing_resource_40pct": scenario_missing_resource,
    "incomplete_relationships_30pct": scenario_incomplete_relationships,
    "inconsistent_records_10pct": scenario_inconsistent_records,
    "missing_quality_events": scenario_missing_quality_events,
}


# ---------------------------------------------------------------------------
# Analysis
# ---------------------------------------------------------------------------

def compute_performance(df: pd.DataFrame) -> dict:
    case_span = (
        df.groupby("Case ID")
        .agg(case_start=("Start Timestamp", "min"), case_end=("Complete Timestamp", "max"))
    )
    case_span["duration_hours"] = (
        case_span["case_end"] - case_span["case_start"]
    ).dt.total_seconds() / 3600.0
    mean_case_duration_h = float(case_span["duration_hours"].mean())
    median_case_duration_h = float(case_span["duration_hours"].median())

    df = df.copy()
    df["activity_duration_min"] = (
        df["Complete Timestamp"] - df["Start Timestamp"]
    ).dt.total_seconds() / 60.0
    # only meaningful where Complete >= Start (post-swap corruption may violate this)
    valid = df["activity_duration_min"] >= 0
    activity_totals = (
        df[valid].groupby("Activity")["activity_duration_min"].sum().sort_values(ascending=False)
    )
    top_bottlenecks = list(activity_totals.head(5).index)

    n_events = len(df)
    n_missing_resource = int(df["Resource"].isna().sum())
    resource_valid = df[valid & df["Resource"].notna()]
    resource_totals = (
        resource_valid.groupby("Resource")["activity_duration_min"].sum().sort_values(ascending=False)
    )
    top_resource_bottlenecks = list(resource_totals.head(5).index)

    return {
        "n_cases": int(df["Case ID"].nunique()),
        "n_events": n_events,
        "n_activities_observed": int(df["Activity"].nunique()),
        "n_negative_duration_events": int((~valid).sum()),
        "mean_case_duration_hours": round(mean_case_duration_h, 2),
        "median_case_duration_hours": round(median_case_duration_h, 2),
        "top5_bottleneck_activities_by_total_time": top_bottlenecks,
        "n_resources_observed": int(df["Resource"].nunique(dropna=True)),
        "pct_events_missing_resource": round(100.0 * n_missing_resource / n_events, 1) if n_events else None,
        "top5_bottleneck_resources_by_total_time": top_resource_bottlenecks,
    }


def discover_reference_model(baseline_df: pd.DataFrame):
    formatted = to_event_log_df(baseline_df)
    net, im, fm = pm4py.discover_petri_net_inductive(formatted)
    return net, im, fm, formatted


def conformance_against_reference(df: pd.DataFrame, net, im, fm) -> dict:
    formatted = to_event_log_df(df)
    try:
        fitness = pm4py.fitness_token_based_replay(formatted, net, im, fm)
    except Exception as e:  # pragma: no cover - defensive, report the failure as data
        return {"error": str(e)}
    return {
        "average_trace_fitness": round(float(fitness.get("average_trace_fitness", float("nan"))), 4),
        "log_fitness": round(float(fitness.get("log_fitness", float("nan"))), 4),
        "percentage_of_fitting_traces": round(float(fitness.get("percentage_of_fitting_traces", float("nan"))), 2),
    }


def own_discovery_summary(df: pd.DataFrame) -> dict:
    formatted = to_event_log_df(df)
    try:
        net, im, fm = pm4py.discover_petri_net_inductive(formatted)
    except Exception as e:  # pragma: no cover
        return {"error": str(e)}
    return {
        "n_places": len(net.places),
        "n_transitions": len(net.transitions),
        "n_arcs": len(net.arcs),
    }


def main():
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    raw = load_raw()

    print(f"Loaded {len(raw)} raw rows, {raw['Case ID'].nunique()} cases, "
          f"{raw['Activity'].nunique()} distinct activities.", file=sys.stderr)

    net, im, fm, _ = discover_reference_model(raw)
    baseline_perf = compute_performance(raw)
    baseline_top_bottlenecks = set(baseline_perf["top5_bottleneck_activities_by_total_time"])
    baseline_top_resource_bottlenecks = set(baseline_perf["top5_bottleneck_resources_by_total_time"])

    results = {}
    for name, fn in SCENARIOS.items():
        variant_df = fn(raw.copy())
        perf = compute_performance(variant_df)
        conf = conformance_against_reference(variant_df, net, im, fm)
        own = own_discovery_summary(variant_df)

        overlap = set(perf["top5_bottleneck_activities_by_total_time"]) & baseline_top_bottlenecks
        bottleneck_ranking_preserved = perf["top5_bottleneck_activities_by_total_time"][:1] == \
            baseline_perf["top5_bottleneck_activities_by_total_time"][:1]
        resource_overlap = set(perf["top5_bottleneck_resources_by_total_time"]) & baseline_top_resource_bottlenecks
        resource_top1_preserved = perf["top5_bottleneck_resources_by_total_time"][:1] == \
            baseline_perf["top5_bottleneck_resources_by_total_time"][:1]

        results[name] = {
            "performance": perf,
            "conformance_vs_baseline_reference_model": conf,
            "own_discovered_model_size": own,
            "top5_bottleneck_overlap_with_baseline": sorted(overlap),
            "top1_bottleneck_matches_baseline": bottleneck_ranking_preserved,
            "top5_resource_bottleneck_overlap_with_baseline": sorted(resource_overlap),
            "top1_resource_bottleneck_matches_baseline": resource_top1_preserved,
            "case_retention_pct": round(100.0 * perf["n_cases"] / baseline_perf["n_cases"], 1),
            "event_retention_pct": round(100.0 * perf["n_events"] / baseline_perf["n_events"], 1),
        }
        print(f"[{name}] cases={perf['n_cases']} events={perf['n_events']} "
              f"fitness={conf.get('average_trace_fitness')} "
              f"top1_bottleneck_matches={bottleneck_ranking_preserved}", file=sys.stderr)

    out_path = RESULTS_DIR / "results.json"
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"Wrote {out_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
