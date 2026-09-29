"""
Gate 3 experiment: evidence-grounded factory findings.

Tests the Gate 3 hypothesis: given a specific factory question, can a
category-coverage check (built in Gate 2) identify the evidence a finding
requires, measure whether that evidence is available in a given (possibly
degraded) dataset, and cause the system to withhold or qualify a finding
that PM4Py/pandas can technically still compute?

This script does NOT build a new analysis engine. It reuses, unmodified,
the scenario-generation code and category-coverage mechanism from Gate 2
(experiments/gate2_data_realism/run_experiment.py and
coverage_check_experiment.py) and adds only a thin "finding" layer on top:
for each of three factory questions, compute the same performance metrics
Gate 2 already computes, then gate the resulting finding's confidence
status on (a) coverage of the specific evidence category the question
depends on and (b) presence of logical inconsistencies (negative-duration
events), per Gate 2 Findings 1-5.

No LLM layer, no OCEL model, no digital twin, no ERP connector, and no new
process-mining algorithm are introduced here. Scope is limited to Gate 3 of
README.md section 12.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "gate2_data_realism"))
from run_experiment import (  # noqa: E402
    SCENARIOS,
    load_raw,
    compute_performance,
)

RESULTS_DIR = Path("/workspace/experiments/gate3_evidence_grounded_findings/results")

# Coverage-status thresholds, reused unchanged from Gate 2's
# coverage_check_experiment.py (SEVERE_THRESHOLD_PCT = 20.0). MEDIUM_THRESHOLD_PCT
# is new in Gate 3, to distinguish a merely-degraded-but-usable evidence base
# from a fully healthy one; it is an illustrative choice, not evidence-derived
# (documented as a limitation in the Gate 3 report, same caveat Gate 2 gave for
# its own 20% threshold).
SEVERE_THRESHOLD_PCT = 20.0
MEDIUM_THRESHOLD_PCT = 70.0

QUALITY_SUBSTRINGS = ["Q.C.", "Inspection", "MRB"]


def event_count_by_activity(df) -> dict:
    return df["Activity"].value_counts().to_dict()


def category_event_count(df, substrings) -> int:
    pattern = "|".join(substrings)
    return int(df["Activity"].str.contains(pattern, case=False, na=False).sum())


def rework_event_count(df) -> int:
    if "Rework" not in df.columns:
        return 0
    col = df["Rework"]
    return int(col.astype(str).str.strip().str.lower().isin(["true", "yes", "1"]).sum())


def rejected_qty_event_count(df) -> int:
    if "Qty Rejected" not in df.columns:
        return 0
    return int((df["Qty Rejected"].fillna(0) > 0).sum())


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
    return {"expected_count": expected, "observed_count": observed,
            "coverage_pct": coverage_pct, "flag": flag}


def confidence_status(coverage_flags: dict, n_negative_duration_events: int) -> str:
    flags = {c["flag"] for c in coverage_flags.values()}
    if "MISSING" in flags:
        return "WITHHELD"
    if n_negative_duration_events > 0:
        # Gate 2 Finding 3: logical inconsistency is a distinct, higher-severity
        # signal than plain incompleteness -- it caps confidence even if
        # coverage otherwise looks fine.
        return "LOW"
    if "SEVERELY_DEGRADED" in flags:
        return "LOW"
    if "PARTIAL" in flags:
        return "MEDIUM"
    return "HIGH"


# ---------------------------------------------------------------------------
# Question 1: What is the bottleneck (activity and resource)?
# ---------------------------------------------------------------------------

def question_bottleneck(variant_df, perf: dict, baseline_activity_counts: dict,
                         baseline_resource_counts: dict, n_negative: int) -> dict:
    top_activity = perf["top5_bottleneck_activities_by_total_time"][0] if perf["top5_bottleneck_activities_by_total_time"] else None
    top_resource = perf["top5_bottleneck_resources_by_total_time"][0] if perf["top5_bottleneck_resources_by_total_time"] else None

    variant_activity_counts = event_count_by_activity(variant_df)
    variant_resource_counts = variant_df["Resource"].value_counts(dropna=True).to_dict()

    coverage = {}
    missing_evidence = []
    if top_activity is not None:
        expected = baseline_activity_counts.get(top_activity, 0)
        observed = variant_activity_counts.get(top_activity, 0)
        coverage[f"activity:{top_activity}"] = coverage_flag(expected, observed)
    else:
        missing_evidence.append("No activity data available at all -- cannot name a bottleneck activity.")

    if top_resource is not None:
        expected = baseline_resource_counts.get(top_resource, 0)
        observed = variant_resource_counts.get(top_resource, 0)
        coverage[f"resource:{top_resource}"] = coverage_flag(expected, observed)
    else:
        missing_evidence.append("No resource data available at all -- cannot name a bottleneck resource.")

    for key, c in coverage.items():
        if c["flag"] in ("MISSING", "SEVERELY_DEGRADED"):
            missing_evidence.append(
                f"Evidence for {key} is {c['flag']} ({c['observed_count']} of "
                f"{c['expected_count']} baseline events observed, "
                f"{c['coverage_pct']}% coverage) -- the ranking that produced "
                f"this candidate may not reflect the true bottleneck."
            )

    status = confidence_status(coverage, n_negative)
    if status == "WITHHELD":
        finding = ("Cannot reliably name the bottleneck: the top-ranked "
                   "candidate has zero observed evidence in this dataset.")
    else:
        finding = (f"Candidate bottleneck activity: '{top_activity}'. "
                   f"Candidate bottleneck resource: '{top_resource}'.")

    return {
        "question": "What is the bottleneck (activity and resource)?",
        "finding": finding,
        "supporting_evidence": {
            "top5_bottleneck_activities_by_total_time": perf["top5_bottleneck_activities_by_total_time"],
            "top5_bottleneck_resources_by_total_time": perf["top5_bottleneck_resources_by_total_time"],
            "n_events": perf["n_events"],
            "n_cases": perf["n_cases"],
        },
        "evidence_coverage": coverage,
        "missing_evidence": missing_evidence,
        "logical_inconsistencies": {"negative_duration_events": n_negative},
        "confidence_status": status,
        "limitations": [
            "Bottleneck is proxied by total recorded activity duration, not by "
            "queueing/waiting time or true resource utilization rate (out of "
            "scope per Gate 2 section 7).",
            "Evidence coverage here is computed only for the specific "
            "activity/resource that happens to rank #1 in this scenario, not "
            "for every activity/resource in the process.",
        ],
    }


# ---------------------------------------------------------------------------
# Question 2: Is quality/rework a significant issue in this process?
# ---------------------------------------------------------------------------

def question_quality(variant_df, baseline_counts: dict, n_negative: int) -> dict:
    variant_counts = {
        "quality_inspection_events": category_event_count(variant_df, QUALITY_SUBSTRINGS),
        "rework_flagged_events": rework_event_count(variant_df),
        "rejected_qty_events": rejected_qty_event_count(variant_df),
    }
    coverage = {
        name: coverage_flag(baseline_counts[name], variant_counts[name])
        for name in variant_counts
    }
    status = confidence_status(coverage, n_negative)

    missing_evidence = [
        f"{name}: {c['flag']} ({c['observed_count']} of {c['expected_count']} "
        f"baseline events observed, {c['coverage_pct']}% coverage)"
        for name, c in coverage.items()
        if c["flag"] in ("MISSING", "SEVERELY_DEGRADED")
    ]

    total_quality_signal = sum(variant_counts.values())
    if status == "WITHHELD":
        finding = ("Cannot determine whether quality/rework is a significant "
                   "issue in this process: one or more quality-related "
                   "evidence categories have zero observed events, even "
                   "though other process-mining outputs (discovery, "
                   "conformance) still run and produce a result.")
    elif total_quality_signal == 0:
        finding = "No quality/rework issue observed in the available evidence."
    else:
        finding = (f"Quality/rework signal observed: "
                   f"{variant_counts['quality_inspection_events']} quality-"
                   f"inspection events, {variant_counts['rework_flagged_events']} "
                   f"rework-flagged events, {variant_counts['rejected_qty_events']} "
                   f"events with rejected quantity > 0.")

    return {
        "question": "Is quality/rework a significant issue in this process?",
        "finding": finding,
        "supporting_evidence": variant_counts,
        "evidence_coverage": coverage,
        "missing_evidence": missing_evidence,
        "logical_inconsistencies": {"negative_duration_events": n_negative},
        "confidence_status": status,
        "limitations": [
            "Category membership is determined by activity-name substring "
            "match (Q.C./Inspection/MRB) and a boolean Rework/Qty Rejected "
            "field, not a validated quality taxonomy.",
            "This question is the one Gate 2 section 4 (missing_quality_events "
            "scenario) specifically showed can silently vanish from a "
            "fitness-score-only or ranking-only report; it is included here "
            "specifically to test whether the withholding behavior fires.",
        ],
    }


# ---------------------------------------------------------------------------
# Question 3: Is a specific process step showing abnormal performance?
# ---------------------------------------------------------------------------

TARGET_ACTIVITY = "Final Inspection Q.C."
MIN_EVENTS_FOR_DURATION_CLAIM = 20
ABNORMAL_RATIO_THRESHOLD = 1.5  # variant mean vs baseline mean


def activity_mean_duration_minutes(df, activity: str):
    sub = df[df["Activity"] == activity].copy()
    if sub.empty:
        return None, 0
    sub["duration_min"] = (sub["Complete Timestamp"] - sub["Start Timestamp"]).dt.total_seconds() / 60.0
    valid = sub[sub["duration_min"] >= 0]
    if valid.empty:
        return None, len(sub)
    return float(valid["duration_min"].mean()), len(sub)


def question_abnormal_step(variant_df, baseline_mean: float, baseline_count: int, n_negative: int) -> dict:
    variant_mean, variant_count = activity_mean_duration_minutes(variant_df, TARGET_ACTIVITY)

    coverage = {
        f"activity:{TARGET_ACTIVITY}": coverage_flag(baseline_count, variant_count)
    }
    missing_evidence = []
    sample_size_sufficient = variant_count >= MIN_EVENTS_FOR_DURATION_CLAIM
    if not sample_size_sufficient:
        missing_evidence.append(
            f"Only {variant_count} events observed for '{TARGET_ACTIVITY}' "
            f"(baseline: {baseline_count}); below the "
            f"{MIN_EVENTS_FOR_DURATION_CLAIM}-event minimum this check "
            f"requires to trust a mean-duration comparison."
        )
    if coverage[f"activity:{TARGET_ACTIVITY}"]["flag"] in ("MISSING", "SEVERELY_DEGRADED"):
        missing_evidence.append(
            f"Coverage of '{TARGET_ACTIVITY}' events is "
            f"{coverage[f'activity:{TARGET_ACTIVITY}']['flag']} in this dataset."
        )

    status = confidence_status(coverage, n_negative)
    if not sample_size_sufficient:
        status = "WITHHELD"

    if status == "WITHHELD" or variant_mean is None:
        finding = (f"Cannot determine whether '{TARGET_ACTIVITY}' shows "
                   f"abnormal performance: insufficient surviving evidence "
                   f"for this specific activity in this dataset.")
        ratio = None
    else:
        ratio = round(variant_mean / baseline_mean, 2) if baseline_mean else None
        if ratio is not None and ratio >= ABNORMAL_RATIO_THRESHOLD:
            finding = (f"'{TARGET_ACTIVITY}' shows abnormal performance: mean "
                       f"duration {variant_mean:.1f} min is {ratio}x the "
                       f"baseline mean ({baseline_mean:.1f} min).")
        else:
            finding = (f"'{TARGET_ACTIVITY}' does not show abnormal performance "
                       f"in this dataset (mean duration {variant_mean:.1f} min "
                       f"vs. baseline {baseline_mean:.1f} min).")

    return {
        "question": f"Is '{TARGET_ACTIVITY}' showing abnormal performance (duration)?",
        "finding": finding,
        "supporting_evidence": {
            "variant_mean_duration_min": round(variant_mean, 1) if variant_mean is not None else None,
            "baseline_mean_duration_min": round(baseline_mean, 1),
            "ratio_vs_baseline": ratio,
            "variant_event_count": variant_count,
            "baseline_event_count": baseline_count,
        },
        "evidence_coverage": coverage,
        "missing_evidence": missing_evidence,
        "logical_inconsistencies": {"negative_duration_events": n_negative},
        "confidence_status": status,
        "limitations": [
            f"Fixed to a single, hand-picked target activity ('{TARGET_ACTIVITY}') "
            "for this experiment; a real implementation would need to run this "
            "check per-activity, not on one preselected step.",
            f"The {MIN_EVENTS_FOR_DURATION_CLAIM}-event minimum-sample-size "
            f"threshold and the {ABNORMAL_RATIO_THRESHOLD}x abnormality "
            "threshold are illustrative choices for this experiment, not "
            "derived from any statistical power analysis or domain evidence.",
        ],
    }


def main():
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    raw = load_raw()

    baseline_activity_counts = event_count_by_activity(raw)
    baseline_resource_counts = raw["Resource"].value_counts(dropna=True).to_dict()
    baseline_quality_counts = {
        "quality_inspection_events": category_event_count(raw, QUALITY_SUBSTRINGS),
        "rework_flagged_events": rework_event_count(raw),
        "rejected_qty_events": rejected_qty_event_count(raw),
    }
    baseline_mean_target, baseline_count_target = activity_mean_duration_minutes(raw, TARGET_ACTIVITY)

    print(f"Baseline quality-related counts: {baseline_quality_counts}", file=sys.stderr)
    print(f"Baseline '{TARGET_ACTIVITY}' mean duration: {baseline_mean_target:.1f} min "
          f"over {baseline_count_target} events", file=sys.stderr)

    all_results = {}
    for scenario_name, fn in SCENARIOS.items():
        variant_df = fn(raw.copy())
        perf = compute_performance(variant_df)
        n_negative = perf["n_negative_duration_events"]

        findings = {
            "bottleneck": question_bottleneck(
                variant_df, perf, baseline_activity_counts, baseline_resource_counts, n_negative
            ),
            "quality_rework": question_quality(variant_df, baseline_quality_counts, n_negative),
            "abnormal_step": question_abnormal_step(
                variant_df, baseline_mean_target, baseline_count_target, n_negative
            ),
        }
        all_results[scenario_name] = findings
        statuses = {q: f["confidence_status"] for q, f in findings.items()}
        print(f"[{scenario_name}] confidence_status={statuses}", file=sys.stderr)

    out_path = RESULTS_DIR / "results.json"
    with open(out_path, "w") as f:
        json.dump(all_results, f, indent=2, default=str)
    print(f"Wrote {out_path}", file=sys.stderr)

    withheld_cases = [
        (scenario, q) for scenario, findings in all_results.items()
        for q, f in findings.items() if f["confidence_status"] == "WITHHELD"
    ]
    print(f"\nScenarios/questions where the finding was WITHHELD: {withheld_cases}", file=sys.stderr)


if __name__ == "__main__":
    main()
